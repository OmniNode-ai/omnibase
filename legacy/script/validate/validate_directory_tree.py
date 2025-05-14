# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "validate_directory_tree"
# namespace: "omninode.validate.directory_tree"
# meta_type: "validator"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00Z"
# last_modified_at: "2025-05-07T12:00:00Z"
# entrypoint: "validate_directory_tree.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ProtocolValidate"]
# base_class: ["ProtocolValidate"]
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""Directory tree validator implementation."""

import os
import yaml
import argparse
import structlog
from pathlib import Path
from fnmatch import fnmatch
from typing import List, Dict, Any, Optional, Union
import fnmatch as fnmatch_mod
import json
import sys
import logging

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedStatus, UnifiedMessageModel
from foundation.model.model_directory_tree import (
    DirectoryTreeStructure,
    CanonicalPath,
    DirectoryPattern,
    ValidationRule,
    DirectoryTreeRules,
)
from foundation.protocol.protocol_tree_file_utils import ProtocolTreeFileUtils
from foundation.util.util_tree_file_utils import UtilTreeFileUtils
from foundation.fixture.fixture_registry import FIXTURE_REGISTRY
from foundation.util.util_tree_sync import directory_to_tree_template
from foundation.util.util_file_output_writer import OutputWriter
from foundation.model.model_struct_index import TreeNode
from foundation.protocol.protocol_tree_cli import ProtocolTreeCLI
from foundation.script.orchestrator.shared.shared_output_formatter import SharedOutputFormatter

output_writer = OutputWriter()

DEFAULT_IGNORE_PATTERNS = [
    '.treeignore', '*.tree', '*.yaml', '*.treerules',
    # Canonical cache/venv ignore patterns
    '__pycache__', '.venv', 'venv', '.mypy_cache', '.pytest_cache', '.DS_Store', '.cache', '.tox', '.coverage', '.idea', '.vscode', '.egg-info', 'dist', 'build', 'node_modules', '.git'
]

class ValidateDirectoryTree(ProtocolValidate):
    """Validates directory tree structure against a .tree file."""

    def __init__(self, logger, tree_file_utils: ProtocolTreeFileUtils, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the validator.
        
        Args:
            logger: Injected logger instance (DI-compliant).
            tree_file_utils: Injected tree file utility (DI-compliant, protocol-based).
            config: Optional configuration dictionary.
        """
        self.template: Optional[TreeNode] = None
        self.logger = logger
        self.tree_file_utils = tree_file_utils
        self.logger.debug("Validator initialized", validator_id=id(self), tree_file_utils_id=id(tree_file_utils))

    def get_name(self) -> str:
        """Get the name of the validator.
        
        Returns:
            str: The validator name.
        """
        return "directory_tree"

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the validator with template paths.
        
        Args:
            config: Configuration dictionary with template paths.
        """
        if "base_template_path" in config:
            self.logger.debug("Loading template from path", path=config["base_template_path"])
            with open(config["base_template_path"]) as f:
                template_data = yaml.safe_load(f)
                self.template = TreeNode(**template_data)
                self.logger.debug(
                    "Template loaded and injected",
                    template_id=id(self.template),
                    template_hash=hash(str(self.template)),
                    template_root=getattr(self.template, 'root', None),
                )

    def _load_tree_yaml(self, tree_file: Path) -> Optional[dict]:
        """Load and parse a YAML .tree file using the injected utility."""
        return self.tree_file_utils.read_tree_file(str(tree_file))

    def _read_treeignore(self, root: Path) -> list:
        """Read ignore patterns from a .treeignore file at the root, if present, and merge with defaults."""
        patterns = list(DEFAULT_IGNORE_PATTERNS)
        ignore_file = root / ".treeignore"
        if ignore_file.exists():
            with open(ignore_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        return patterns

    def _should_ignore(self, name: str, ignore_patterns: list) -> bool:
        """Return True if name matches any ignore pattern (glob)."""
        for pat in ignore_patterns:
            if fnmatch_mod.fnmatch(name, pat):
                return True
        return False

    def _compare_structure_to_tree(self, actual: TreeNode, expected: TreeNode, result: UnifiedResultModel, parent_path: str = "", ignore_patterns: list = None) -> None:
        """Compare actual directory structure to expected structure in .tree file (TreeNode models only)."""
        if ignore_patterns is None:
            ignore_patterns = []
        if not expected:
            result.messages.append(UnifiedMessageModel(
                summary=".tree model is empty or invalid",
                level="error"
            ))
            result.status = UnifiedStatus.error
            return
        # Filter children by ignore_patterns
        expected_children = [c for c in (expected.children or []) if not self._should_ignore(c.name, ignore_patterns)]
        actual_children = {c.name: c for c in (actual.children or []) if not self._should_ignore(c.name, ignore_patterns)}
        expected_names = set(c.name for c in expected_children)
        actual_names = set(actual_children.keys())
        missing = expected_names - actual_names
        extra = actual_names - expected_names
        for name in missing:
            result.messages.append(UnifiedMessageModel(
                summary=f"Missing required entry in directory tree: {parent_path}/{name}",
                level="error"
            ))
            result.status = UnifiedStatus.error
        for name in extra:
            result.messages.append(UnifiedMessageModel(
                summary=f"Unexpected entry in directory tree: {parent_path}/{name}",
                level="error"
            ))
            result.status = UnifiedStatus.error
        # Recursively validate children
        for expected_child in expected_children:
            cname = expected_child.name
            ctype = expected_child.type
            if cname in actual_children:
                actual_child = actual_children[cname]
                if ctype == "directory" and actual_child.type == "directory":
                    self._compare_structure_to_tree(
                        actual_child,
                        expected_child,
                        result,
                        f"{parent_path}/{cname}",
                        ignore_patterns
                    )
                elif ctype == "file" and actual_child.type == "file":
                    continue  # File exists
                else:
                    result.messages.append(UnifiedMessageModel(
                        summary=f"Type mismatch for {parent_path}/{cname}: expected {ctype}, got {actual_child.type}",
                        level="error"
                    ))
                    result.status = UnifiedStatus.error

    def _build_structure(self, path: Path, ignore_patterns: list = None) -> TreeNode:
        """Build directory structure from path as a TreeNode, skipping ignored directories/files."""
        if ignore_patterns is None:
            ignore_patterns = list(DEFAULT_IGNORE_PATTERNS)
        children = []
        if path.exists():
            for item in sorted(os.listdir(path)):
                if self._should_ignore(item, ignore_patterns):
                    continue
                item_path = path / item
                if item_path.is_dir():
                    children.append(self._build_structure(item_path, ignore_patterns))
                else:
                    children.append(TreeNode(name=item, type="file", children=None))
        return TreeNode(name=path.name, type="directory", children=children)

    def validate(self, target: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> UnifiedResultModel:
        """Validate directory tree structure.
        
        Args:
            target: Path to validate.
            config: Optional configuration dictionary.
            
        Returns:
            UnifiedResultModel: Validation result with errors/warnings.
        """
        if config:
            self.logger.debug("Configuring validator in validate()", config=config)
            self.configure(config)
            
        self.logger.debug(
            "Validating with template",
            template_id=id(self.template),
            template_hash=hash(str(self.template)) if self.template else None,
            template_root=getattr(self.template, 'root', None) if self.template else None,
        )

        path = Path(target)
        result = UnifiedResultModel(
            status=UnifiedStatus.success,
            messages=[]
        )
        
        if not self.template:
            self.logger.warning("No template configured; using fallback/default template", validator_id=id(self))
            result.messages.append(UnifiedMessageModel(
                summary="No template configured",
                level="error"
            ))
            result.status = UnifiedStatus.error
            return result

        # Load .tree file as TreeNode
        tree_file = path / ".tree"
        try:
            expected_tree = self.tree_file_utils.read_tree_file(str(tree_file))
        except ValueError as e:
            result.messages.append(UnifiedMessageModel(
                summary=str(e),
                level="error"
            ))
            result.status = UnifiedStatus.error
            return result
        except Exception as e:
            result.messages.append(UnifiedMessageModel(
                summary=f"Unexpected error loading .tree file: {e}",
                level="error"
            ))
            result.status = UnifiedStatus.error
            return result
        
        if not expected_tree:
            result.messages.append(UnifiedMessageModel(
                summary="No .tree file found or invalid YAML",
                level="error"
            ))
            result.status = UnifiedStatus.error
            return result

        # Read ignore patterns (merge canonical and .treeignore)
        ignore_patterns = self._read_treeignore(path)
        # Always include canonical ignore patterns
        for pat in DEFAULT_IGNORE_PATTERNS:
            if pat not in ignore_patterns:
                ignore_patterns.append(pat)
        
        # Build actual directory structure as TreeNode (pass ignore patterns)
        actual_tree = self._build_structure(path, ignore_patterns)
        
        # Compare structures (TreeNode only)
        self._compare_structure_to_tree(actual_tree, expected_tree, result, "", ignore_patterns)
        
        return result

    def validate_main(self, args: argparse.Namespace) -> UnifiedResultModel:
        """Main validation entry point for CLI usage.
        
        Args:
            args: Command line arguments.
            
        Returns:
            UnifiedResultModel: The validation result object.
        """
        config = {
            "base_template_path": args.base_template,
        }
        result = self.validate(args.root, config)
        if result.status == UnifiedStatus.success:
            self.logger.info("Validation passed")
        else:
            self.logger.error("Validation failed", messages=[m.summary for m in getattr(result, "messages", [])])
        return result

def compute_tree_compliance_state(root_path: Path, tree_file_utils: UtilTreeFileUtils) -> dict:
    """Compute compliance state for a directory tree.
    
    Args:
        root_path: Root path to compute state for.
        tree_file_utils: Tree file utilities.
        
    Returns:
        dict: Compliance state.
    """
    validator = ValidateDirectoryTree(
        resolve_logger(),
        tree_file_utils
    )
    result = validator.validate(root_path)
    
    def safe_serialize(obj):
        if isinstance(obj, (Path, TreeNode)):
            return str(obj)
        return obj
    
    return {
        "status": result.status.value,
        "messages": [m.summary for m in getattr(result, "messages", [])]
    }

def resolve_logger():
    """Resolve logger instance."""
    return structlog.get_logger()

def resolve_tree_file_utils(logger):
    """Resolve tree file utilities instance."""
    # Use fixture in test/CI, else real implementation
    if os.getenv("CI") or os.getenv("TEST"):
        return FIXTURE_REGISTRY.get("tree_file_utils")
    return UtilTreeFileUtils(logger)

def parse_tree_cli_args(argv: Optional[list[str]] = None) -> tuple[str, argparse.Namespace]:
    """
    Parse CLI arguments for tree tools, supporting both positional and --root arguments.
    Returns:
        root_dir: The resolved root directory (str)
        args: The parsed argparse.Namespace
    Raises:
        SystemExit if neither argument is provided.
    """
    parser = argparse.ArgumentParser(description="Validate directory tree structure. You may specify the root directory as a positional argument or with --root. If both are provided, --root takes precedence.")
    parser.add_argument("positional_root", type=str, nargs="?", help="Root directory to validate (positional, optional if --root is used)")
    parser.add_argument("--root", type=str, help="Root directory to validate (optional, takes precedence over positional)")
    parser.add_argument("--base-template", type=str, help="Base template path")
    parser.add_argument("--output-format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args(argv)
    root_dir: Optional[str] = None
    if args.root:
        root_dir = args.root
    elif args.positional_root:
        root_dir = args.positional_root
    else:
        parser.error("You must specify a root directory as a positional argument or with --root.")
    return root_dir, args

def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Directory tree validator CLI.")
    parser.add_argument("--root", required=True, help="Root directory to validate")
    parser.add_argument("--base-template", required=True, help="Path to canonical .tree file")
    parser.add_argument("--output-format", default="text", choices=["text", "json", "yaml"], help="Output format: text, json, yaml")
    args = parser.parse_args(argv)
    logger = resolve_logger()
    tree_file_utils = resolve_tree_file_utils(logger)
    validator = ValidateDirectoryTree(logger, tree_file_utils)
    validator.configure({"base_template_path": args.base_template})
    result = validator.validate(args.root, {})
    formatter = SharedOutputFormatter()
    output = formatter.render_output(result, format_type=args.output_format)
    print(output)
    return 0 if (hasattr(result, 'status') and getattr(result, 'status', UnifiedStatus.error) == UnifiedStatus.success) else 1

if __name__ == "__main__":
    sys.exit(main())

# Register the validator
from foundation.script.validate.validate_registry import ValidatorRegistry

ValidatorRegistry().register(
    name="directory_tree",
    validator_cls=ValidateDirectoryTree,
    meta={
        "name": "directory_tree",
        "version": "v1"
    },
)