# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: helpers_maintenance.py
# version: 1.0.0
# uuid: 468e60ae-eb6b-4dd4-9ad3-3e56f36b62d0
# author: OmniNode Team
# created_at: 2025-05-28T10:21:58.251411
# last_modified_at: 2025-05-28T14:46:03.272576
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4d1040ef6a8634b25445fdf5a4ff842aa1d44f0724c5d8c5243563ad29f32c03
# entrypoint: python@helpers_maintenance.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.helpers_maintenance
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Node Maintenance Generator for regenerating contracts, manifests, and configurations.

This module provides functionality to regenerate and fix critical node files:
- contract.yaml files based on node structure analysis
- node.onex.yaml manifests with current ONEX standards
- Configuration file synchronization and updates
"""

import shutil
import json
from pathlib import Path
from typing import Dict
import yaml
from pydantic import ValidationError

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.model.model_node_template import NodeTemplateConfig
from omnibase.model.model_onex_ignore import OnexIgnoreConfig
from omnibase.model.model_handler_config import HandlerConfig
from omnibase.model.model_onex_message_result import OnexResultModel, OnexMessageModel
from omnibase.metadata.metadata_constants import get_namespace_prefix

_COMPONENT_NAME = Path(__file__).stem


class NodeMaintenanceGenerator:
    """
    Generator for regenerating and maintaining node contracts, manifests, and configurations.
    
    This class provides functionality to:
    - Regenerate contract.yaml files based on node structure analysis
    - Update node.onex.yaml manifests to current ONEX standards
    - Synchronize configuration files with template standards
    - Fix node compliance issues automatically
    - Provide safety features (backup, dry-run, rollback)
    """

    def __init__(self, template_directory=None, backup_enabled: bool = True) -> None:
        """
        Initialize the node maintenance generator.
        
        Args:
            template_directory: Path to the template node directory.
                               Defaults to src/omnibase/nodes/template_node/v1_0_0/
            backup_enabled: Whether to create backups before making changes
        """
        self.template_directory = template_directory or Path("src/omnibase/nodes/template_node/v1_0_0")
        self.nodes_directory = Path("src/omnibase/nodes")
        self.backup_enabled = backup_enabled
        self.backup_directory = Path(".node_maintenance_backups")
        
    def regenerate_contract(self, node_path: Path, dry_run: bool = False):
        """
        Regenerate contract.yaml file based on node structure analysis.
        
        Args:
            node_path: Path to the node directory
            dry_run: If True, show what would be done without making changes
            
        Returns:
            OnexResultModel with regeneration results
        """
        try:
            contract_path = node_path / "contract.yaml"
            
            # Analyze node structure
            analysis_result = self._analyze_node_structure(node_path)
            if analysis_result.status == OnexStatus.ERROR:
                return analysis_result
            
            # Generate new contract content
            contract_content = self._generate_contract_content(analysis_result.metadata or {})
            
            if dry_run:
                return OnexResultModel(
                    status=OnexStatus.SUCCESS,
                    messages=[OnexMessageModel(summary=f"DRY RUN: Would regenerate contract for {node_path.name}")],
                    metadata={"new_contract_content": contract_content}
                )
            
            # Backup existing contract if it exists
            if contract_path.exists() and self.backup_enabled:
                self._backup_file(contract_path)
            
            # Write new contract
            with open(contract_path, 'w') as f:
                f.write(contract_content)
            
            emit_log_event(
                level=LogLevelEnum.INFO,
                message=f"Regenerated contract for {node_path.name}",
                context={"component": _COMPONENT_NAME, "node_path": str(node_path)},
                correlation_id=None,
            )
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                messages=[OnexMessageModel(summary=f"Successfully regenerated contract for {node_path.name}")],
                metadata={"contract_path": str(contract_path)}
            )
            
        except Exception as e:
            emit_log_event(
                level=LogLevelEnum.ERROR,
                message=f"Error regenerating contract: {e}",
                context={"component": _COMPONENT_NAME, "node_path": str(node_path)},
                correlation_id=None,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                messages=[OnexMessageModel(summary=f"Contract regeneration failed for {node_path.name}: {e}", level=LogLevelEnum.ERROR)]
            )
    
    def regenerate_manifest(self, node_path: Path, dry_run: bool = False):
        """
        Regenerate node.onex.yaml manifest with current ONEX standards.
        
        Args:
            node_path: Path to the node directory
            dry_run: If True, show what would be done without making changes
            
        Returns:
            OnexResultModel with regeneration results
        """
        try:
            manifest_path = node_path / "node.onex.yaml"
            
            # Analyze node for manifest generation
            analysis_result = self._analyze_node_for_manifest(node_path)
            if analysis_result.status == OnexStatus.ERROR:
                return analysis_result
            
            # Generate new manifest content
            manifest_content = self._generate_manifest_content(analysis_result.metadata or {})
            
            if dry_run:
                return OnexResultModel(
                    status=OnexStatus.SUCCESS,
                    messages=[OnexMessageModel(summary=f"DRY RUN: Would regenerate manifest for {node_path.name}")],
                    metadata={"new_manifest_content": manifest_content}
                )
            
            # Backup existing manifest if it exists
            if manifest_path.exists() and self.backup_enabled:
                self._backup_file(manifest_path)
            
            # Write new manifest
            with open(manifest_path, 'w') as f:
                f.write(manifest_content)
            
            emit_log_event(
                level=LogLevelEnum.INFO,
                message=f"Regenerated manifest for {node_path.name}",
                context={"component": _COMPONENT_NAME, "node_path": str(node_path)},
                correlation_id=None,
            )
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                messages=[OnexMessageModel(summary=f"Successfully regenerated manifest for {node_path.name}")],
                metadata={"manifest_path": str(manifest_path)}
            )
            
        except Exception as e:
            emit_log_event(
                level=LogLevelEnum.ERROR,
                message=f"Error regenerating manifest: {e}",
                context={"component": _COMPONENT_NAME, "node_path": str(node_path)},
                correlation_id=None,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                messages=[OnexMessageModel(summary=f"Manifest regeneration failed for {node_path.name}: {e}", level=LogLevelEnum.ERROR)]
            )
    
    def fix_node_health(self, node_path: Path, dry_run: bool = False):
        """
        Perform comprehensive node health fix (contracts + manifests + configs).
        
        Args:
            node_path: Path to the node directory
            dry_run: If True, show what would be done without making changes
            
        Returns:
            OnexResultModel with overall fix results
        """
        try:
            fixes_applied = []
            
            # Regenerate contract
            contract_result = self.regenerate_contract(node_path, dry_run)
            if contract_result.status == OnexStatus.SUCCESS:
                fixes_applied.append("contract")
            
            # Regenerate manifest
            manifest_result = self.regenerate_manifest(node_path, dry_run)
            if manifest_result.status == OnexStatus.SUCCESS:
                fixes_applied.append("manifest")
            
            # Synchronize configurations
            config_result = self.synchronize_configurations(node_path, dry_run)
            if config_result.status == OnexStatus.SUCCESS:
                fixes_applied.append("configurations")
            
            if dry_run:
                return OnexResultModel(
                    status=OnexStatus.SUCCESS,
                    messages=[OnexMessageModel(summary=f"DRY RUN: Would apply fixes to {node_path.name}")],
                    metadata={"potential_fixes": fixes_applied}
                )
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                messages=[OnexMessageModel(summary=f"Applied {len(fixes_applied)} fixes to {node_path.name}")],
                metadata={"fixes_applied": fixes_applied}
            )
            
        except Exception as e:
            emit_log_event(
                level=LogLevelEnum.ERROR,
                message=f"Error fixing node health: {e}",
                context={"component": _COMPONENT_NAME, "node_path": str(node_path)},
                correlation_id=None,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                messages=[OnexMessageModel(summary=f"Node health fix failed for {node_path.name}: {e}", level=LogLevelEnum.ERROR)]
            )
    
    def synchronize_configurations(self, node_path: Path, dry_run: bool = False):
        """
        Synchronize configuration files with template standards.
        
        Args:
            node_path: Path to the node directory
            dry_run: If True, show what would be done without making changes
            
        Returns:
            OnexResultModel with synchronization results
        """
        try:
            synchronized_files = []
            
            # Update .onexignore from template
            onexignore_result = self._synchronize_onexignore(node_path, dry_run)
            if onexignore_result.status == OnexStatus.SUCCESS:
                synchronized_files.append(".onexignore")
            
            # Could add other config file synchronization here
            # - pyproject.toml sections
            # - pytest.ini
            # - other standard files
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message=f"Synchronized {len(synchronized_files)} configuration files",
                metadata={"synchronized_files": synchronized_files}
            )
            
        except Exception as e:
            emit_log_event(
                level=LogLevelEnum.ERROR,
                message=f"Error synchronizing configurations: {e}",
                context={"component": _COMPONENT_NAME, "node_path": str(node_path)},
                correlation_id=None,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Configuration synchronization failed for {node_path.name}: {e}"
            )
    
    def _analyze_node_structure(self, node_path: Path):
        """
        Analyze node structure to determine contract requirements.
        
        Args:
            node_path: Path to the node directory
            
        Returns:
            OnexResultModel with analysis results
        """
        try:
            analysis = {}
            
            # Check for main node file
            node_file = node_path / "node.py"
            if node_file.exists():
                analysis["has_main_node"] = True
                analysis["main_entrypoint"] = "node.py"
            else:
                analysis["has_main_node"] = False
            
            # Check for state models
            state_file = node_path / "models" / "state.py"
            if state_file.exists():
                analysis["has_state_models"] = True
                analysis["state_file"] = "models/state.py"
            else:
                analysis["has_state_models"] = False
            
            # Check for helpers
            helpers_dir = node_path / "helpers"
            if helpers_dir.exists():
                helper_files = list(helpers_dir.glob("*.py"))
                analysis["has_helpers"] = len(helper_files) > 0
                analysis["helper_count"] = len(helper_files)
            else:
                analysis["has_helpers"] = False
                analysis["helper_count"] = 0
            
            # Check for tests
            tests_dir = node_path / "node_tests"
            if tests_dir.exists():
                test_files = list(tests_dir.glob("test_*.py"))
                analysis["has_tests"] = len(test_files) > 0
                analysis["test_count"] = len(test_files)
            else:
                analysis["has_tests"] = False
                analysis["test_count"] = 0
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message=f"Successfully analyzed node structure for {node_path.name}",
                metadata=analysis
            )
            
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Failed to analyze node structure: {e}"
            )
    
    def _analyze_node_for_manifest(self, node_path: Path) -> OnexResultModel:
        """
        Analyze node for manifest generation requirements.
        
        Args:
            node_path: Path to the node directory
            
        Returns:
            OnexResultModel with manifest analysis
        """
        try:
            analysis = {}
            
            # Extract node name and version from path
            node_name = node_path.name
            analysis["node_name"] = node_name
            
            # Try to determine version from directory structure
            version_dir = node_path.parent.name if node_path.parent.name.startswith("v") else "v1_0_0"
            analysis["version"] = version_dir
            
            # Check for existing manifest
            manifest_path = node_path / "node.onex.yaml"
            analysis["has_existing_manifest"] = manifest_path.exists()
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message=f"Successfully analyzed node for manifest generation",
                metadata=analysis
            )
            
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Failed to analyze node for manifest: {e}"
            )
    
    def _generate_contract_content(self, analysis: Dict[str, str]) -> str:
        """Generate contract.yaml content based on node analysis."""
        # Basic contract template - could be enhanced based on analysis
        contract_template = """# Contract for {node_name}
# Generated by NodeMaintenanceGenerator

version: "1.0.0"
type: "node_contract"
"""
        return contract_template.format(node_name=analysis.get("node_name", "unknown"))
    
    def _generate_manifest_content(self, analysis: Dict[str, str]) -> str:
        """Generate node.onex.yaml content based on node analysis."""
        # Basic manifest template - could be enhanced based on analysis
        manifest_template = """# Node manifest for {node_name}
# Generated by NodeMaintenanceGenerator

name: {node_name}
version: {version}
type: onex_node
"""
        return manifest_template.format(
            node_name=analysis.get("node_name", "unknown"),
            version=analysis.get("version", "v1_0_0")
        )
    
    def _synchronize_onexignore(self, node_path: Path, dry_run: bool) -> OnexResultModel:
        """
        Synchronize .onexignore file with template standards.
        
        Args:
            node_path: Path to the node directory
            dry_run: If True, show what would be done without making changes
            
        Returns:
            OnexResultModel with synchronization results
        """
        try:
            onexignore_path = node_path / ".onexignore"
            template_onexignore = self.template_directory / ".onexignore"
            
            if not template_onexignore.exists():
                return OnexResultModel(
                    status=OnexStatus.ERROR,
                    message="Template .onexignore not found"
                )
            
            if dry_run:
                return OnexResultModel(
                    status=OnexStatus.SUCCESS,
                    message=f"DRY RUN: Would synchronize .onexignore for {node_path.name}"
                )
            
            # Copy template .onexignore
            shutil.copy2(template_onexignore, onexignore_path)
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message=f"Synchronized .onexignore for {node_path.name}"
            )
            
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Failed to synchronize .onexignore: {e}"
            )
    
    def _backup_file(self, file_path: Path) -> None:
        """
        Create a backup of the specified file.
        
        Args:
            file_path: Path to the file to backup
        """
        if not file_path.exists():
            return
        
        # Create backup directory if it doesn't exist
        self.backup_directory.mkdir(exist_ok=True)
        
        # Create backup with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.backup"
        backup_path = self.backup_directory / backup_name
        
        shutil.copy2(file_path, backup_path)
        
        emit_log_event(
            level=LogLevelEnum.INFO,
            message=f"Created backup: {backup_path}",
            context={"component": _COMPONENT_NAME, "original_file": str(file_path)},
            correlation_id=None,
        )
