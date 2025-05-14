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
from foundation.model.model_validate import ValidationResult, ValidateStatus
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

output_writer = OutputWriter()

class ValidateDirectoryTree(ProtocolValidate):
    """Validates directory tree structure against canonical paths and flexible directories."""

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
        """Load and parse a YAML .tree file using the injected utility (always, even if not on disk)."""
        return self.tree_file_utils.read_tree_file(str(tree_file))

    def _read_treeignore(self, root: Path) -> list:
        """Read ignore patterns from a .treeignore file at the root, if present."""
        ignore_file = root / ".treeignore"
        patterns = []
        if ignore_file.exists():
            with open(ignore_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        return patterns

    def _should_ignore(self, name: str, ignore_patterns: list) -> bool:
        """Return True if name matches any ignore pattern."""
        for pat in ignore_patterns:
            if fnmatch_mod.fnmatch(name, pat):
                return True
        return False

    def _compare_structure_to_tree(self, structure: DirectoryTreeStructure, tree_yaml: dict, result: ValidationResult, parent_path: str = "", ignore_patterns: list = None) -> None:
        if ignore_patterns is None:
            ignore_patterns = []
        if not tree_yaml:
            result.errors.append(".tree YAML is empty or invalid")
            result.is_valid = False
            result.status = ValidateStatus.INVALID
            return
        expected_children = tree_yaml.get("children", [])
        actual_children = structure.children if hasattr(structure, "children") else {}
        # Filter actual and expected by ignore_patterns
        filtered_actual = {k: v for k, v in actual_children.items() if not self._should_ignore(k, ignore_patterns)}
        filtered_expected = [child for child in expected_children if child and not self._should_ignore(child["name"], ignore_patterns)]
        expected_names = set(child["name"] for child in filtered_expected if child)
        actual_names = set(filtered_actual.keys())
        missing = expected_names - actual_names
        extra = actual_names - expected_names
        for name in missing:
            result.errors.append(f"Missing required entry in directory tree: {parent_path}/{name}")
            result.is_valid = False
            result.status = ValidateStatus.INVALID
        for name in extra:
            result.errors.append(f"Unexpected entry in directory tree: {parent_path}/{name}")
            result.is_valid = False
            result.status = ValidateStatus.INVALID
        for child in filtered_expected:
            if not child:
                continue
            cname = child["name"]
            ctype = child["type"]
            if cname in filtered_actual:
                if ctype == "directory" and filtered_actual[cname]:
                    self._compare_structure_to_tree(filtered_actual[cname], child, result, parent_path + "/" + cname, ignore_patterns)
                elif ctype == "file" and filtered_actual[cname] is None:
                    continue  # File exists
                elif ctype == "directory" and not filtered_actual[cname]:
                    continue
                else:
                    result.errors.append(f"Type mismatch for {parent_path}/{cname}: expected {ctype}")
                    result.is_valid = False
                    result.status = ValidateStatus.INVALID

    def validate(self, target: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate directory tree structure.
        
        Args:
            target: Path to validate.
            config: Optional configuration dictionary.
            
        Returns:
            ValidationResult: Validation result with errors/warnings.
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
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            version="0.1.0",
            metadata={},
            aggregated=[],
            status=ValidateStatus.VALID
        )
        
        if not self.template:
            self.logger.warning("No template configured; using fallback/default template", validator_id=id(self))
            result.errors.append("No template configured")
            result.is_valid = False
            result.status = ValidateStatus.INVALID
            return result

        # Try to load .tree structure from injected utility
        tree_file = path / ".tree"
        tree_yaml = self._load_tree_yaml(tree_file)
        if tree_yaml:
            structure = self._tree_yaml_to_structure(tree_yaml, str(path))
        else:
            # Fallback: build from file system
            structure = self._build_structure(path)

        # Validate against template
        self._validate_structure(structure, self.template, result)
        
        # Fallback discovery: check for .tree file and apply policy
        ignore_patterns = self._read_treeignore(path)
        if tree_yaml:
            self._compare_structure_to_tree(structure, tree_yaml, result, parent_path=str(path), ignore_patterns=ignore_patterns)
        else:
            policy_path = Path(config.get("tree_policy_path", "")) if config else None
            policy = None
            if policy_path and policy_path.exists():
                with open(policy_path) as f:
                    policy = yaml.safe_load(f)
            msg = ".tree file missing; using fallback discovery per policy."
            self.logger.warning(msg)
            result.warnings.append(msg)
            result.metadata["fallback"] = True
            if policy and policy.get("log_fallback", True):
                result.metadata["fallback_policy"] = policy
        
        # Log the parsed .tree structure
        self.logger.debug("Parsed .tree structure", tree_structure=tree_yaml)
        # Generate the actual directory structure
        actual_tree = self.tree_file_utils.directory_to_tree_template(str(path))
        self.logger.debug("Actual directory structure", actual_tree=actual_tree.model_dump() if hasattr(actual_tree, "model_dump") else actual_tree)
        # Compute and log hashes
        parsed_hash = self.tree_file_utils.compute_tree_hash(tree_yaml)
        actual_hash = self.tree_file_utils.compute_tree_hash(actual_tree.model_dump() if hasattr(actual_tree, "model_dump") else actual_tree)
        self.logger.debug("Computed hashes", parsed_hash=parsed_hash, actual_hash=actual_hash)
        
        return result

    def _tree_yaml_to_structure(self, tree_yaml: dict, root_path: str) -> DirectoryTreeStructure:
        """Convert .tree YAML structure to DirectoryTreeStructure recursively."""
        def build(node, current_path):
            children = {}
            for child in node.get("children", []):
                name = child["name"]
                ctype = child["type"]
                child_path = os.path.join(current_path, name)
                if ctype == "directory":
                    children[name] = build(child, child_path)
                else:
                    children[name] = None
            return DirectoryTreeStructure(path=current_path, children=children)
        return build(tree_yaml, root_path)

    def validate_main(self, args: argparse.Namespace) -> ValidationResult:
        """Main validation entry point for CLI usage.
        
        Args:
            args: Command line arguments.
            
        Returns:
            ValidationResult: The validation result object.
        """
        config = {
            "base_template_path": args.base_template,
            "container_template_path": args.container_template,
            "deny_unlisted": args.deny_unlisted,
        }
        result = self.validate(args.root, config)
        if result.is_valid:
            self.logger.info("Validation passed")
        else:
            self.logger.error("Validation failed", errors=result.errors)
        return result

    def _build_structure(self, path: Path) -> DirectoryTreeStructure:
        """Build directory structure from path.
        
        Args:
            path: Path to build structure from.
            
        Returns:
            DirectoryTreeStructure: Directory structure.
        """
        children = {}
        if path.exists():
            for item in os.listdir(path):
                item_path = path / item
                if item_path.is_dir():
                    children[item] = self._build_structure(item_path)
                else:
                    children[item] = None
        return DirectoryTreeStructure(
            path=str(path),
            children=children
        )

    def _validate_structure(
        self,
        structure: DirectoryTreeStructure,
        template: TreeNode,
        result: ValidationResult
    ) -> None:
        """Validate directory structure against template.
        
        Args:
            structure: Directory structure to validate.
            template: Template to validate against.
            result: Validation result to update.
        """
        self.logger.debug(
            "_validate_structure called",
            template_id=id(template),
            template_hash=hash(str(template)),
            template_root=getattr(template, 'root', None),
        )
        self.logger.debug("Validating structure", structure=structure, template=template)
        
        # Check canonical paths
        for canonical_path in template.canonical_paths:
            path_parts = canonical_path.path.split("/")
            current = structure
            
            for part in path_parts:
                if part == "**":
                    # Recursively check all subdirectories
                    self._validate_recursive(
                        current,
                        canonical_path,
                        template.rules,
                        result
                    )
                    break
                elif part == "*":
                    # Check all immediate children
                    for child_name, child in current.children.items():
                        if child:  # Directory
                            self._validate_directory(
                                child_name,
                                canonical_path,
                                template.rules,
                                result
                            )
                        else:  # File
                            self._validate_file(
                                child_name,
                                canonical_path,
                                template.rules,
                                result
                            )
                    break
                else:
                    # Check specific path
                    if part not in current.children:
                        result.errors.append(f"Missing required path: {part}")
                        result.is_valid = False
                        result.status = ValidateStatus.INVALID
                        break
                    current = current.children[part]

        # Check validation rules
        for rule in template.validation_rules:
            if rule.required:
                found = False
                # Check test files in test directory
                test_dir = None
                current = structure
                self.logger.debug("Looking for test files", current=current.children)
                for part in ["src", "foundation", "test"]:
                    if part in current.children:
                        current = current.children[part]
                        self.logger.debug(f"Found {part}", children=current.children)
                        if part == "test":
                            test_dir = current
                    else:
                        self.logger.debug(f"Missing {part}")
                        break

                if test_dir:
                    self.logger.debug("Found test directory", files=test_dir.children)
                    for child_name in test_dir.children:
                        self.logger.debug("Checking file", file=child_name, pattern=rule.pattern)
                        if fnmatch(child_name, rule.pattern):
                            found = True
                            break

                if not found:
                    result.errors.append(
                        f"Missing required file matching pattern: {rule.pattern}"
                    )
                    result.is_valid = False
                    result.status = ValidateStatus.INVALID

    def _validate_recursive(
        self,
        structure: DirectoryTreeStructure,
        canonical_path: CanonicalPath,
        rules: DirectoryTreeRules,
        result: ValidationResult
    ) -> None:
        """Recursively validate directory structure.
        
        Args:
            structure: Directory structure to validate.
            canonical_path: Canonical path to validate against.
            rules: Validation rules.
            result: Validation result to update.
        """
        for child_name, child in structure.children.items():
            if child:  # Directory
                self._validate_directory(
                    child_name,
                    canonical_path,
                    rules,
                    result
                )
                self._validate_recursive(
                    child,
                    canonical_path,
                    rules,
                    result
                )
            else:  # File
                self._validate_file(
                    child_name,
                    canonical_path,
                    rules,
                    result
                )

    def _validate_directory(
        self,
        name: str,
        canonical_path: CanonicalPath,
        rules: DirectoryTreeRules,
        result: ValidationResult
    ) -> None:
        """Validate directory name.
        
        Args:
            name: Directory name.
            canonical_path: Canonical path to validate against.
            rules: Validation rules.
            result: Validation result to update.
        """
        if name in rules.allow_flexible:
            return

        valid = False
        for pattern in canonical_path.allowed_dirs:
            if fnmatch(name, pattern.pattern):
                valid = True
                break

        if not valid and rules.deny_unlisted:
            result.errors.append(f"Invalid directory name: {name}")
            result.is_valid = False
            result.status = ValidateStatus.INVALID

    def _validate_file(
        self,
        name: str,
        canonical_path: CanonicalPath,
        rules: DirectoryTreeRules,
        result: ValidationResult
    ) -> None:
        """Validate file name.
        
        Args:
            name: File name.
            canonical_path: Canonical path to validate against.
            rules: Validation rules.
            result: Validation result to update.
        """
        valid = False
        for pattern in canonical_path.allowed_files:
            if fnmatch(name, pattern.pattern):
                valid = True
                break

        if not valid and rules.deny_unlisted:
            result.errors.append(f"Invalid file name: {name}")
            result.is_valid = False
            result.status = ValidateStatus.INVALID


def compute_tree_compliance_state(root_path: Path, tree_file_utils: UtilTreeFileUtils) -> dict:
    """
    Compute the compliance state of the .tree file for CI/automation.
    Returns a dict with keys: state, tree_hash, details.
    All values must be JSON serializable.
    """
    tree_path = root_path / ".tree"
    if not tree_path.exists():
        return {"state": "missing", "tree_hash": None, "details": ".tree file is missing"}
    try:
        tree_data = tree_file_utils.read_tree_file(str(tree_path))
        # Build current structure from disk
        current_tree = directory_to_tree_template(str(root_path))
        # Ensure current_tree is a tree_sync.TreeNode instance
        if isinstance(current_tree, dict):
            current_tree = TreeNode.parse_obj(current_tree)
        # Compute hash for both
        file_hash = tree_data["metadata"].get("tree_hash")
        current_hash = tree_file_utils.compute_tree_hash(current_tree)
        if file_hash == current_hash:
            return {"state": "valid", "tree_hash": file_hash, "details": "Tree file matches directory"}
        else:
            return {"state": "stale", "tree_hash": file_hash, "details": "Tree file does not match directory"}
    except Exception as e:
        def safe_serialize(obj):
            if hasattr(obj, 'serialize'):
                obj = obj.serialize()
            if isinstance(obj, dict):
                import json
                return json.dumps(obj)
            return str(obj)
        details = str(e)
        if hasattr(e, 'args') and e.args:
            details = ", ".join(safe_serialize(arg) for arg in e.args)
        return {"state": "error", "tree_hash": None, "details": details}


def resolve_logger():
    return structlog.get_logger("validate.directory_tree.cli")

def resolve_tree_file_utils(logger):
    # Use fixture in test/CI, else real implementation
    if os.environ.get("TESTING") == "1" or os.environ.get("CI") == "1":
        # Import locally to avoid circular import at module level
        from foundation.fixture.fixture_registry import FIXTURE_REGISTRY
        return FIXTURE_REGISTRY.get_fixture("tree_file_utils_fixture")
    return UtilTreeFileUtils(logger)

def main(argv: Optional[List[str]] = None) -> int:
    import argparse, sys
    # --- CRITICAL: Configure structlog before any logger is created ---
    # This ensures all loggers use the correct configuration and prevents log output from polluting stdout in JSON mode.
    parser = argparse.ArgumentParser(description="Validate directory tree structure.\n\nWhen --output-format json is set, the CLI emits a single JSON object with keys: state, tree_hash, details, is_valid, errors, warnings, metadata, status.\nThe 'state' key is always present and reflects compliance state: valid, stale, missing, or error.\n")
    parser.add_argument("--root", default=".", help="Root directory to validate")
    parser.add_argument(
        "--base-template",
        default="base_template.yaml",
        help="Base template file"
    )
    parser.add_argument(
        "--container-template",
        default="container_template.yaml",
        help="Container template file"
    )
    parser.add_argument(
        "--deny-unlisted",
        action="store_true",
        help="Deny paths not listed in canonical paths"
    )
    parser.add_argument(
        "--auto-regenerate",
        action="store_true",
        help="Automatically regenerate .tree file if missing (no prompt)"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Run in CI/batch mode (non-interactive, fail fast, structured output)"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (never prompt, fail if input missing)"
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Exit immediately on first error (for batch mode)"
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json (for CI/automation)"
    )
    args = parser.parse_args(argv)

    # Ensure all standard logging goes to stderr
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, force=True)

    # Reconfigure structlog to log to stderr if output-format is json
    if args.output_format == "json":
        structlog.configure(
            processors=[structlog.processors.JSONRenderer()],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        # Prevent log propagation to parent loggers (which may have stdout handlers)
        root_logger = logging.getLogger()
        root_logger.propagate = False
        structlog_logger = logging.getLogger("validate.directory_tree.cli")
        structlog_logger.propagate = False

    # Remove any StreamHandler that writes to sys.stdout from the root logger
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        if isinstance(handler, logging.StreamHandler) and getattr(handler, 'stream', None) is sys.stdout:
            root_logger.removeHandler(handler)

    logger = resolve_logger()
    logger.info("START CLI")
    tree_file_utils = resolve_tree_file_utils(logger)
    logger.debug("Instantiating ValidateDirectoryTree in CLI", validator_class=str(ValidateDirectoryTree), logger_id=id(logger), tree_file_utils_id=id(tree_file_utils))
    validator = ValidateDirectoryTree(logger, tree_file_utils)
    logger.debug("Configuring validator in CLI", base_template=args.base_template)
    validator.configure({"base_template_path": args.base_template})
    logger.debug("Validator configured in CLI", template_id=id(validator.template), template_hash=hash(str(validator.template)) if validator.template else None, template_root=getattr(validator.template, 'root', None) if validator.template else None)
    root_path = Path(args.root)
    tree_path = root_path / ".tree"
    non_interactive = args.ci or args.non_interactive or not sys.stdin.isatty()
    # Log the loaded template for debugging
    if os.path.exists(args.base_template):
        with open(args.base_template) as f:
            template_content = f.read()
        logger.debug("Loaded base_template.yaml", path=args.base_template, content=template_content)
    # Always compute compliance state for json output
    compliance = compute_tree_compliance_state(root_path, tree_file_utils)
    # If .tree file is missing, handle as before
    if not tree_path.exists():
        if args.auto_regenerate:
            logger.info(".tree file missing; auto-regenerating...")
            structure = validator._build_structure(root_path)
            tree_file_utils.write_tree_file(str(tree_path), structure)
            logger.info(".tree file generated.")
        elif non_interactive:
            logger.error(".tree file is required for canonical discovery. Exiting (non-interactive mode).")
            logger.info("END CLI")
            if args.output_format == "json":
                output = {**compliance, "is_valid": False, "errors": [".tree file is required for canonical discovery"], "warnings": [], "metadata": {}, "status": "invalid"}
                sys.stderr.flush()
                output_writer.write_json(output)
            return 1
        else:
            resp = input(".tree file is missing. Generate it now? [y/N]: ").strip().lower()
            if resp == "y":
                logger.info("Generating .tree file...")
                structure = validator._build_structure(root_path)
                tree_file_utils.write_tree_file(str(tree_path), structure)
                logger.info(".tree file generated.")
            else:
                logger.error(".tree file is required for canonical discovery. Exiting.")
                logger.info("END CLI")
                if args.output_format == "json":
                    output = {**compliance, "is_valid": False, "errors": [".tree file is required for canonical discovery"], "warnings": [], "metadata": {}, "status": "invalid"}
                    sys.stderr.flush()
                    output_writer.write_json(output)
                return 1
    result = validator.validate_main(args)
    # Unify output: always emit compliance state + validation result fields
    if args.output_format == "json":
        output = {
            **compliance,
            "is_valid": getattr(result, "is_valid", False),
            "errors": getattr(result, "errors", []),
            "warnings": getattr(result, "warnings", []),
            "metadata": getattr(result, "metadata", {}),
            "status": str(getattr(result, "status", None)),
        }
        sys.stderr.flush()
        output_writer.write_json(output)
    else:
        logger.info(str(result))
    logger.info("END CLI")
    return 0 if getattr(result, "is_valid", False) else 1

if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    sys.exit(main())

# Register the validator
from foundation.script.validate.validate_registry import ValidatorRegistry

ValidatorRegistry().register(
    name="directory_tree",
    validator_cls=ValidateDirectoryTree,
    meta={
        "name": "directory_tree",
        "version": "v1",
        "group": "structure",
        "description": "Validates directory tree structure against canonical paths and flexible directories.",
    },
)