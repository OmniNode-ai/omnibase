# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: tree_validator.py
# version: 1.0.0
# uuid: 2373519e-45f2-4482-aa89-82db455fd9ad
# author: OmniNode Team
# created_at: 2025-05-24T12:02:47.580707
# last_modified_at: 2025-05-24T16:13:11.912144
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e39476f4fe9e6e1ec5da06a2b66975592ea85122475c90bae788aab6a84f82d7
# entrypoint: python@tree_validator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.tree_validator
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
ONEX Tree Validator - Node-local version using shared tree generator logic and canonical models.
Implements ProtocolOnextreeValidator for standards compliance and extensibility.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml

from omnibase.core.error_codes import CoreErrorCode, OnexError
from omnibase.model.model_onextree_validation import (
    OnextreeTreeNode,
    OnextreeValidationError,
    OnextreeValidationResultModel,
    OnextreeValidationWarning,
    ValidationErrorCodeEnum,
    ValidationStatusEnum,
)

from ..protocol.protocol_onextree_validator import ProtocolOnextreeValidator
from .tree_generator_engine import TreeGeneratorEngine


class OnextreeValidator(ProtocolOnextreeValidator):
    """
    Canonical implementation of ProtocolOnextreeValidator.
    Validates .onextree files against actual directory contents using shared engine logic and canonical models.
    """

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.engine = TreeGeneratorEngine()

    def validate_onextree_file(
        self, onextree_path: Path, root_directory: Path
    ) -> OnextreeValidationResultModel:
        """
        Validate a .onextree manifest file against the actual directory structure.
        Returns a canonical OnextreeValidationResultModel.
        """
        errors: List[OnextreeValidationError] = []
        warnings: List[OnextreeValidationWarning] = []
        if not onextree_path.exists():
            errors.append(
                OnextreeValidationError(
                    code=ValidationErrorCodeEnum.MISSING_FILE,
                    message=f".onextree file not found: {onextree_path}",
                    path=str(onextree_path),
                )
            )
            return OnextreeValidationResultModel(
                status=ValidationStatusEnum.FAILURE,
                errors=errors,
                warnings=warnings,
                summary=".onextree file missing",
            )
        if not root_directory.exists():
            errors.append(
                OnextreeValidationError(
                    code=ValidationErrorCodeEnum.MISSING_FILE,
                    message=f"Root directory not found: {root_directory}",
                    path=str(root_directory),
                )
            )
            return OnextreeValidationResultModel(
                status=ValidationStatusEnum.FAILURE,
                errors=errors,
                warnings=warnings,
                summary="Root directory missing",
            )
        try:
            tree_data = self._load_onextree_file(onextree_path)
            actual_tree = self.engine.scan_directory_structure(root_directory)
            # Convert dicts to canonical tree node models
            tree_model = OnextreeTreeNode.model_validate(tree_data)
            actual_tree_model = OnextreeTreeNode.model_validate(actual_tree)
            self._validate_tree_structure(tree_model, actual_tree_model, errors)
            self._validate_file_completeness(tree_model, actual_tree_model, errors)
            self._validate_file_types(tree_model, actual_tree_model, errors)
            status = (
                ValidationStatusEnum.SUCCESS
                if not errors
                else ValidationStatusEnum.FAILURE
            )
            summary = (
                "Validation passed" if not errors else f"{len(errors)} error(s) found"
            )
            return OnextreeValidationResultModel(
                status=status,
                errors=errors,
                warnings=warnings,
                summary=summary,
                tree=tree_model,
            )
        except Exception as e:
            errors.append(
                OnextreeValidationError(
                    code=ValidationErrorCodeEnum.UNKNOWN,
                    message=f"Validation failed with exception: {str(e)}",
                )
            )
            return OnextreeValidationResultModel(
                status=ValidationStatusEnum.FAILURE,
                errors=errors,
                warnings=warnings,
                summary="Validation failed with exception",
            )

    def _load_onextree_file(self, onextree_path: Path) -> Dict[str, Any]:
        with open(onextree_path, "r", encoding="utf-8") as f:
            if onextree_path.suffix.lower() == ".json":
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise OnexError(
                f"Expected dict at root of {onextree_path}, got {type(data).__name__}",
                CoreErrorCode.INVALID_PARAMETER,
            )
        return data

    def _extract_all_file_paths(
        self, node: OnextreeTreeNode, current_path: str
    ) -> Set[str]:
        paths: Set[str] = set()
        node_path = f"{current_path}/{node.name}" if current_path else node.name
        paths.add(node_path)
        if node.type == "directory" and node.children:
            for child in node.children:
                paths.update(self._extract_all_file_paths(child, node_path))
        return paths

    def _validate_tree_structure(
        self,
        tree: OnextreeTreeNode,
        actual_tree: OnextreeTreeNode,
        errors: List[OnextreeValidationError],
    ) -> None:
        if tree.name != actual_tree.name:
            errors.append(
                OnextreeValidationError(
                    code=ValidationErrorCodeEnum.STRUCTURE_MISMATCH,
                    message=f"Root node name mismatch: {tree.name} vs {actual_tree.name}",
                    path=tree.name,
                )
            )
        if tree.type != actual_tree.type:
            errors.append(
                OnextreeValidationError(
                    code=ValidationErrorCodeEnum.STRUCTURE_MISMATCH,
                    message=f"Root node type mismatch: {tree.type} vs {actual_tree.type}",
                    path=tree.name,
                )
            )

    def _validate_file_completeness(
        self,
        tree: OnextreeTreeNode,
        actual_tree: OnextreeTreeNode,
        errors: List[OnextreeValidationError],
    ) -> None:
        tree_files = self._extract_all_file_paths(tree, "")
        actual_files = self._extract_all_file_paths(actual_tree, "")
        missing_files = actual_files - tree_files
        for missing_file in missing_files:
            errors.append(
                OnextreeValidationError(
                    code=ValidationErrorCodeEnum.MISSING_FILE,
                    message=f"File exists in directory but missing from .onextree: {missing_file}",
                    path=missing_file,
                )
            )
        extra_files = tree_files - actual_files
        for extra_file in extra_files:
            errors.append(
                OnextreeValidationError(
                    code=ValidationErrorCodeEnum.EXTRA_FILE,
                    message=f"File exists in .onextree but not in directory: {extra_file}",
                    path=extra_file,
                )
            )

    def _validate_file_types(
        self,
        tree: OnextreeTreeNode,
        actual_tree: OnextreeTreeNode,
        errors: List[OnextreeValidationError],
    ) -> None:
        def compare_types(
            node1: OnextreeTreeNode, node2: OnextreeTreeNode, path: str
        ) -> None:
            if node1.type != node2.type:
                errors.append(
                    OnextreeValidationError(
                        code=ValidationErrorCodeEnum.TYPE_MISMATCH,
                        message=f"Type mismatch at {path}: {node1.type} vs {node2.type}",
                        path=path,
                    )
                )
            if node1.type == "directory" and node1.children and node2.children:
                children1 = {c.name: c for c in node1.children}
                children2 = {c.name: c for c in node2.children}
                for name in set(children1) & set(children2):
                    compare_types(children1[name], children2[name], f"{path}/{name}")

        compare_types(tree, actual_tree, tree.name)

    def print_results(self, result: OnextreeValidationResultModel) -> None:
        """
        Print validation results in a human-readable format.
        """
        if result.warnings:
            print("WARNINGS:")
            for warning in result.warnings:
                print(f"  ⚠️  {warning.message}")
            print()
        if result.errors:
            print("ERRORS:")
            for error in result.errors:
                print(f"  ❌ {error.code}: {error.message}")
            print()
        else:
            print("✅ .onextree validation passed")
        if result.summary:
            print(result.summary)

    def get_exit_code(self, result: OnextreeValidationResultModel) -> int:
        """
        Map validation result to CLI exit code (0=success, 1=failure).
        """
        return 1 if result.status == ValidationStatusEnum.FAILURE else 0
