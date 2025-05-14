# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "metadata_stamper"
# namespace: "omninode.tools.metadata_stamper"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T22:11:58+00:00"
# last_modified_at: "2025-05-05T22:11:58+00:00"
# entrypoint: "metadata_stamper.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['ProtocolStamper']'
# base_class:
#   - '['ProtocolStamper']'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
OmniNode Metadata Stamper

Dependency Injection (DI) Pattern:
- All logging is performed via a logger injected into the MetadataStamper class at construction.
- No function or method in this file should call logging.getLogger() directly.
- This pattern ensures testability, configurability, and compliance with project DI standards.
- This class-based logger DI pattern is now the standard for all new/refactored scripts and tools.
"""

import argparse
import ast
import datetime
import logging
import re
import uuid
from pathlib import Path
import sys
from typing import Optional, List, TYPE_CHECKING, cast
from types import ModuleType
import json
from foundation.util.util_file_output_writer import OutputWriter
from foundation.const.metadata_tags import OMNINODE_METADATA_START, OMNINODE_METADATA_END
from foundation.model.model_validation_issue_mixin import ValidationIssueMixin
from foundation.protocol.protocol_cli_tool import ProtocolCLITool, CLIToolMixin

try:
    import pathspec
except ImportError:
    pathspec = None  # type: ignore[assignment]

from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.template.metadata.metadata_template_blocks import (
    EXTENDED_METADATA,
    MINIMAL_METADATA,
)
from foundation.protocol.protocol_stamper_ignore import ProtocolStamperIgnore
from foundation.model.model_metadata import StamperIgnoreModel
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.protocol.protocol_stamper import ProtocolStamper
from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.registry.registry_metadata_block_hash import RegistryMetadataBlockHash
from foundation.util.util_hash_utils import UtilHashUtils
from foundation.model.model_enum_template_type import TemplateTypeEnum
from foundation.util.util_metadata_block_extractor_registry import get_extractor
from foundation.protocol.protocol_util_header import ProtocolUtilHeader
from foundation.registry.utility_registry import get_util


class MetadataStamper(CLIToolMixin, ValidationIssueMixin, ProtocolStamper, ProtocolCLITool):
    """
    OmniNode Metadata Stamper Tool.
    Implements ProtocolStamper for DI and orchestration.
    Implements ProtocolCLITool for CLI compliance.
    Injects/repairs metadata blocks in source files.
    All logging is performed via an injected logger (ProtocolLogger).
    Template registry is injected via DI (MetadataRegistryTemplate).
    Structured error/warning reporting via ValidationIssueMixin.

    CONTRACT: This stamper always overwrites the hash in both the file and registry after stamping. There is no enforcement or validation logic here; all enforcement is handled by the validator.
    """
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    TEMPLATE_CHOICES = ['minimal', 'extended', 'yaml', 'markdown']

    def __init__(self, logger: ProtocolLogger, template_registry: MetadataRegistryTemplate, registry: RegistryMetadataBlockHash, header_util: ProtocolUtilHeader = None):
        super().__init__()
        # Validate logger
        if not hasattr(logger, 'info') or not hasattr(logger, 'warning') or not hasattr(logger, 'error') or not hasattr(logger, 'debug'):
            raise AttributeError(f"'{logger.__class__.__name__}' object has no attribute 'info' (or other required logging methods)")
        if template_registry is None:
            raise AttributeError("'NoneType' object has no attribute 'get_template_for_extension'")
        if not hasattr(template_registry, 'get_template_for_extension'):
            raise AttributeError(f"'{template_registry.__class__.__name__}' object has no attribute 'get_template_for_extension'")
        self.logger: ProtocolLogger = logger
        self.template_registry: MetadataRegistryTemplate = template_registry
        self.registry: RegistryMetadataBlockHash = registry
        # Inject header utility via DI, fallback to registry if not provided
        self.header_util = header_util or get_util('header')
        self.errors = []
        self.warnings = []
        self.failed_files = []

    def extract_base_classes_from_file(self, file_path: str) -> list[str]:
        """
        Parse the Python file and return a sorted list of all unique base class names for all classes defined in the file.
        :param file_path: Path to the Python file.
        :return: Sorted list of base class names.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=file_path)
            base_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            base_names.add(base.id)
                        elif isinstance(base, ast.Attribute):
                            # Handles e.g. models.BaseModel
                            base_names.add(base.attr)
                        elif isinstance(base, ast.Subscript):
                            # Handles e.g. Generic[BaseModel]
                            if isinstance(base.value, ast.Name):
                                base_names.add(base.value.id)
            self.logger.debug(
                f"AST base class extraction for {file_path}: {base_names}"
            )
            return sorted(base_names)
        except Exception as e:
            self.logger.warning(f"AST parse failed for {file_path}: {e}")
            return []

    def generate_metadata_block(
        self,
        name: str,
        entrypoint: str,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        author: str = "OmniNode Team",
        owner: str = "jonah@omninode.ai",
        meta_type: str = "model",
        schema_version: str = "1.0.0",
        protocol_class: Optional[str] = None,
        base_class: Optional[str] = None,
        mock_safe: str = "true",
        file_path: Optional[str] = None,
        copyright: Optional[str] = None,
        created_at: Optional[str] = None,
        last_modified_at: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate a metadata block for a file. Ignores extra/unknown kwargs.
        """
        # Validate required fields
        if name is None or entrypoint is None:
            self.add_error(message="name and entrypoint are required", file=str(file_path or entrypoint), type="error")
            raise ValueError("name and entrypoint are required")
        now: str = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        copyright_str: str = copyright or "Copyright (c) 2025 OmniNode.ai"
        created_at = created_at or now
        last_modified_at = last_modified_at or now
        if file_path is not None:
            file_path_obj = Path(file_path)
        elif entrypoint is not None:
            file_path_obj = Path(entrypoint)
        else:
            self.add_error(message="Either file_path or entrypoint must be provided", file="<unknown>", type="error")
            raise ValueError("Either file_path or entrypoint must be provided")
        file_path_str: str = str(file_path_obj.resolve())
        self.logger.debug(f"generate_metadata_block: file_path for AST extraction: {file_path_str}")
        if not protocol_class or not base_class:
            if file_path_obj.exists():
                bases = self.extract_base_classes_from_file(file_path_str)
            else:
                self.logger.warning(f"File for AST extraction does not exist: {file_path_str}")
                bases = []
            protocol_class = protocol_class or str(bases)
            base_class = base_class or str(bases)
        self.logger.info(
            f"generate_metadata_block: name={name}, entrypoint={entrypoint}, template={template}, author={author}, owner={owner}, meta_type={meta_type}, schema_version={schema_version}, copyright={copyright_str}, created_at={created_at}, last_modified_at={last_modified_at}, protocol_class={protocol_class}, base_class={base_class}"
        )
        ext = file_path_obj.suffix.lower()
        template_str = self.template_registry.get_template_for_extension(ext, template)
        if not template_str:
            self.add_error(message=f"No template registered for extension: {ext}", file=str(file_path_obj), type="error")
            raise ValueError(f"No template registered for extension: {ext}")
        if template and hasattr(self.template_registry, '_ext_map'):
            ext_map = getattr(self.template_registry, '_ext_map', {})
            registered_template_enums = ext_map.get(ext, [])
            if isinstance(registered_template_enums, list):
                if template not in registered_template_enums:
                    self.add_error(message=f"Requested template '{template}' is not registered for extension '{ext}'", file=str(file_path_obj), type="error")
                    raise ValueError(f"Requested template '{template}' is not registered for extension '{ext}'")
            else:
                if registered_template_enums != template:
                    self.add_error(message=f"Requested template '{template}' does not match registered template '{registered_template_enums}' for extension '{ext}'", file=str(file_path_obj), type="error")
                    raise ValueError(f"Requested template '{template}' does not match registered template '{registered_template_enums}' for extension '{ext}'")
        def format_yaml_list(val: object) -> str:
            if isinstance(val, list):
                return '\n' + '\n'.join([f"  - {item}" for item in val])
            return str(val)
        import ast
        if isinstance(protocol_class, str) and protocol_class.startswith("[") and protocol_class.endswith("]"):
            try:
                protocol_class_list = ast.literal_eval(protocol_class)
                protocol_class = format_yaml_list(protocol_class_list)
            except Exception:
                pass
        elif isinstance(protocol_class, list):
            protocol_class = format_yaml_list(protocol_class)
        if isinstance(base_class, str) and base_class.startswith("[") and base_class.endswith("]"):
            try:
                base_class_list = ast.literal_eval(base_class)
                base_class = format_yaml_list(base_class_list)
            except Exception:
                pass
        elif isinstance(base_class, list):
            base_class = format_yaml_list(base_class)
        block: str = template_str.format(
            metadata_version="0.1",
            schema_version=schema_version,
            name=name,
            namespace=f"omninode.tools.{name}",
            entrypoint=entrypoint,
            author=author,
            owner=owner,
            copyright=copyright_str,
            created_at=str(created_at),
            last_modified_at=str(last_modified_at),
            meta_type=meta_type,
            version="0.1.0",
            protocols_supported=format_yaml_list(["O.N.E. v0.1"]),
            protocol_class=protocol_class,
            base_class=base_class,
            mock_safe=mock_safe,
        )
        self.logger.info(f"Rendered metadata block:\n{block}")
        return block

    def extract_metadata_block(self, text: str) -> tuple[Optional[str], Optional[int], Optional[int], Optional[str], Optional[str]]:
        """
        Extract the metadata block from the given text, supporting only the canonical delimiters.
        :return: Tuple of (block, start index, end index, start_marker, end_marker)
        """
        start_marker = f"# {OMNINODE_METADATA_START}"
        end_marker = f"# {OMNINODE_METADATA_END}"
        start = text.find(start_marker)
        if start == -1:
            return None, None, None, None, None
        end = text.find(end_marker, start)
        if end == -1:
            # Partial/corrupted: start found, end missing
            return text[start:], start, None, start_marker, end_marker
        end_idx = end + len(end_marker)
        return text[start:end_idx], start, end_idx, start_marker, end_marker

    def validate_metadata_block(self, block: str) -> tuple[str, str]:
        """
        Validate the metadata block for required fields and format.
        :return: Tuple of (status, message)
        """
        if not block:
            return "none", "No metadata block found."
        # Parse YAML block (skip delimiters)
        import yaml
        try:
            yaml_start = block.find("# === OmniNode:Metadata ===") + len("# === OmniNode:Metadata ===")
            yaml_end = block.find("# === /OmniNode:Metadata ===")
            yaml_block = block[yaml_start:yaml_end].strip()
            meta = yaml.safe_load(yaml_block)
        except Exception as e:
            return "corrupted", f"YAML parse error: {e}"
        required = [
            "metadata_version",
            "name",
            "namespace",
            "version",
            "entrypoint",
            "meta_type",
            "author",
            "owner",
            "created_at",
            "last_modified_at",
        ]
        missing = [k for k in required if k not in meta]
        if missing:
            return "partial", f"Missing fields: {missing}"
        if not block.strip().endswith("# === /OmniNode:Metadata ==="):
            return "corrupted", "End marker missing."
        # Value checks
        if meta["metadata_version"] != "0.1":
            return (
                "corrupted",
                f"metadata_version must be '0.1', got '{meta['metadata_version']}'",
            )
        if not meta["name"] or not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", meta["name"]):
            return "corrupted", f"Invalid name: {meta['name']}"
        if not meta["namespace"] or not re.match(
            r"^[a-zA-Z0-9_.]+$", meta["namespace"]
        ):
            return "corrupted", f"Invalid namespace: {meta['namespace']}"
        if not meta["entrypoint"] or not meta["entrypoint"].endswith(".py"):
            return "corrupted", f"Invalid entrypoint: {meta['entrypoint']}"
        if not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
            return "corrupted", f"Invalid version: {meta['version']}"
        # Optionally: warn on unknown fields
        return "valid", "OK"

    def strip_existing_header_and_place_metadata(self, text: str, metadata_block: str) -> str:
        """
        Remove any existing metadata block (legacy or canonical) and place the new one after the canonical header (shebang, future imports, docstring) using the injected header utility and metadata block extractor.
        :return: Modified file content as a string.
        """
        lines = text.splitlines()
        # Use DI-injected extractor for block removal
        extractor = get_extractor('python')
        if extractor is not None:
            # Find block indices
            start_idx = None
            end_idx = None
            for i, line in enumerate(lines):
                if extractor.start_re.match(line.strip()):
                    start_idx = i
                if extractor.end_re.match(line.strip()) and start_idx is not None:
                    end_idx = i
                    break
            lines_wo_meta = list(lines)
            if start_idx is not None:
                # Remove everything from start_idx to end_idx (inclusive)
                if end_idx is not None:
                    del lines_wo_meta[start_idx : end_idx + 1]
                else:
                    del lines_wo_meta[start_idx:]
        else:
            lines_wo_meta = list(lines)
        self.logger.debug(f"[DEBUG] After metadata block removal: {lines_wo_meta}")
        # Use header utility to extract canonical header and rest
        header_lines, rest = self.header_util.normalize_python_header(lines_wo_meta)
        # Compose new file: header, blank line, metadata block, blank line, rest
        new_lines = []
        new_lines.extend(header_lines)
        if header_lines:
            new_lines.append("")  # blank line after header
        new_lines.append(metadata_block.strip())
        new_lines.append("")  # single blank line after metadata
        # Remove leading blank lines from rest
        while rest and rest[0].strip() == "":
            rest = rest[1:]
        new_lines.extend(rest)
        # Remove consecutive blank lines (collapse to single blank line)
        collapsed_lines = []
        prev_blank = False
        for l in new_lines:
            if l.strip() == "":
                if not prev_blank:
                    collapsed_lines.append("")
                prev_blank = True
            else:
                collapsed_lines.append(l)
                prev_blank = False
        # Remove trailing blank lines
        while collapsed_lines and collapsed_lines[-1].strip() == "":
            collapsed_lines.pop()
        self.logger.debug(f"[DEBUG] Final output lines after collapsing: {collapsed_lines}")
        return "\n".join(collapsed_lines)

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs: object,
    ) -> bool:
        """
        Stamp the file with a metadata block, replacing any existing block (legacy or canonical).
        After stamping, compute the hash and update the metadata block and registry.
        :return: True if file was written, False if dry run.
        """
        # Extract known fields from kwargs for protocol compatibility
        file_path = kwargs.get("file_path", None)
        # Explicitly cast to Optional[str] for type safety and mypy compliance
        copyright: Optional[str] = cast(Optional[str], kwargs.get("copyright", None))
        created_at: Optional[str] = cast(Optional[str], kwargs.get("created_at", None))
        last_modified_at: Optional[str] = cast(Optional[str], kwargs.get("last_modified_at", None))
        # Check file size
        file_size: int = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max {self.MAX_FILE_SIZE} bytes)")

        text: str = path.read_text(encoding="utf-8")
        name: str = path.stem
        entrypoint: str = path.name
        metadata_block: str = self.generate_metadata_block(
            name=name,
            entrypoint=entrypoint,
            template=template,
            author=author,
            file_path=str(path),
            copyright=copyright,
            created_at=created_at,
            last_modified_at=last_modified_at,
        )

        # Validate template format
        if not metadata_block.startswith("# === OmniNode:"):
            raise ValueError("Invalid template format: must start with OmniNode metadata marker")

        # Always remove and replace any existing metadata block (legacy or canonical)
        text_wo_metadata = text
        block, start, end, start_marker, end_marker = self.extract_metadata_block(text)
        if start is not None:
            text_wo_metadata = text[:start] + text[end:] if end else text[:start]
            if start_marker and start_marker != "# === OmniNode:Metadata ===":
                self.logger.info(f"[UPGRADE] Upgrading legacy metadata block ({start_marker}) to canonical format in {path}")
        new_text = self.strip_existing_header_and_place_metadata(
            text_wo_metadata, metadata_block
        )
        if overwrite or force_overwrite or repair:
            path.write_text(new_text, encoding="utf-8")
            self.logger.info(f"[+ stamped/replaced] {path}")
            # --- HASH AND REGISTRY LOGIC ---
            # Always compute and overwrite the hash in both the file and registry after stamping.
            stamped_text = path.read_text(encoding="utf-8")
            hash_value = UtilHashUtils.compute_hash(stamped_text)
            # Delegate block hash update to utility
            updated_text = self.header_util.update_metadata_block_hash(stamped_text, hash_value)
            if updated_text is not None:
                path.write_text(updated_text, encoding="utf-8")
            self.registry.update(str(path), hash_value, committer=author)
            return True
        else:
            self.logger.info(f"[! dry run] Would stamp/replace {path}")
            return False

    def add_arguments(self, parser):
        parser.add_argument("files", nargs="+", help="Files to process")
        parser.add_argument("--overwrite", action="store_true", help="Write metadata directly")
        parser.add_argument("--repair", action="store_true", help="Repair partial/corrupted metadata blocks")
        parser.add_argument("--force-overwrite", action="store_true", help="Force overwrite any existing metadata block")
        parser.add_argument("--template", type=str, default='minimal', choices=self.TEMPLATE_CHOICES, help='Template type to use for stamping (minimal, extended, yaml, markdown)')
        parser.add_argument("--author", type=str, default="OmniNode Team", help="Author for the metadata block")
        parser.add_argument("--copyright", type=str, default="Copyright (c) 2025 OmniNode.ai", help="Copyright string for the metadata block")
        parser.add_argument("--created-at", type=str, default=None, help="Creation date (ISO 8601) for the metadata block")
        parser.add_argument("--last-modified-at", type=str, default=None, help="Last modified date (ISO 8601) for the metadata block")

    def run(self, args):
        ignore_provider = StamperIgnoreModel()
        ignore_patterns = load_stamperignore(ignore_provider=ignore_provider)
        for file in args.files:
            path = Path(file)
            if should_ignore(path, ignore_patterns):
                self.logger.info(f"[SKIP] {file} (matched .stamperignore)")
                continue
            if path.suffix == ".py":
                # Convert CLI string to Enum
                try:
                    template_enum = TemplateTypeEnum(args.template.lower())
                except ValueError:
                    self.logger.error(f"Invalid template type: {args.template}")
                    continue
                self.stamp_file(
                    path,
                    template=template_enum,
                    overwrite=args.overwrite,
                    repair=args.repair,
                    force_overwrite=args.force_overwrite,
                    author=args.author,
                    copyright=args.copyright,
                    created_at=args.created_at,
                    last_modified_at=args.last_modified_at,
                )
        return 0


def load_stamperignore(ignore_path: Optional[str] = None, ignore_provider: Optional[ProtocolStamperIgnore] = None) -> list[str]:
    """Load .stamperignore patterns from the project root or from an injected ignore provider."""
    if ignore_provider is not None:
        return ignore_provider.get_ignore_files()
    ignore_file = (
        ignore_path
        or Path(__file__).resolve().parent.parent.parent.parent / ".stamperignore"
    )
    # Ensure ignore_file is a Path for .exists()
    if isinstance(ignore_file, str):
        ignore_file = Path(ignore_file)
    if not ignore_file.exists():
        return []
    with open(ignore_file, "r", encoding="utf-8") as f:
        patterns = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]
    return patterns


def should_ignore(path: Path, patterns: list[str]) -> bool:
    """Return True if the path matches any ignore pattern."""
    if not patterns:
        return False
    rel_path = str(Path(path).as_posix())
    if pathspec:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
        return spec.match_file(rel_path)
    else:
        # Fallback: simple substring or endswith matching
        for pat in patterns:
            if pat.endswith("/") and rel_path.startswith(pat.rstrip("/")):
                return True
            if pat in rel_path:
                return True
        return False


def main() -> None:
    """Module-level CLI entrypoint. Instantiates MetadataStamper with DI logger, registry, and calls main()."""
    logger = logging.getLogger("metadata_stamper")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    template_registry = MetadataRegistryTemplate()
    registry = RegistryMetadataBlockHash()
    stamper = MetadataStamper(logger, template_registry, registry)
    sys.exit(stamper.main())

if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()