import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Set
import ast

from omnibase.enums.log_level import SeverityLevelEnum
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent
from omnibase.nodes.node_manager.v1_0_0.protocols.protocol_standards_compliance_fixer import ProtocolStandardsComplianceFixer
from omnibase.nodes.node_manager.v1_0_0.models.model_standards_fix_result import (
    ModelStandardsFixResult,
    ModelStandardsFixOperation
)
from omnibase.nodes.node_manager.v1_0_0.enums.enum_issue_type import EnumIssueType
from omnibase.nodes.node_manager.v1_0_0.enums.enum_fix_operation_type import EnumFixOperationType
from omnibase.nodes.node_manager.v1_0_0.tools.tool_template_validator import TemplateValidator


class ToolStandardsComplianceFixer(ProtocolStandardsComplianceFixer):
    """Tool for automatically fixing standards compliance violations."""
    
    def __init__(self, logger_tool: ProtocolLoggerEmitLogEvent):
        if logger_tool is None:
            raise RuntimeError("Logger tool must be provided via DI or registry (protocol-pure).")
        self.logger_tool = logger_tool
        # Initialize template validator with default values - will be updated per target
        self.template_validator = None
        
        # ONEX naming conventions
        self.file_prefixes = {
            'models': 'model_',
            'enums': 'enum_',
            'protocols': 'protocol_',
            'tools': 'tool_',
            'handlers': 'handler_',
            'utils': 'utils_',
            'core': 'core_',
            'cli': 'cli_',
            'test': 'test_'
        }
        
        # Template artifacts to remove
        self.template_artifacts = {
            'template_node',
            'TemplateNode',
            'TEMPLATE_NODE',
            'template-node',
            'Template Node'
        }
    
    def fix_standards_violations(
        self,
        target_path: Path,
        dry_run: bool = True,
        fix_types: Optional[List[EnumFixOperationType]] = None,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """Fix all standards compliance violations in target path."""
        operations = []
        errors = []
        warnings = []
        
        try:
            # Initialize template validator with inferred node information
            node_name, node_version = self._infer_node_info(target_path)
            self.template_validator = TemplateValidator(node_name, node_version)
            
            # Run template validation first to identify issues (optional - for information only)
            try:
                validation_issues = self.template_validator.validate_node_directory(target_path)
            except Exception:
                validation_issues = []
            
            # Fix template artifacts
            template_fix_result = self.fix_template_artifacts(target_path, dry_run, create_backups)
            operations.extend(template_fix_result.operations)
            errors.extend(template_fix_result.errors)
            warnings.extend(template_fix_result.warnings)
            
            # Fix naming conventions
            naming_fix_result = self.fix_naming_conventions(target_path, dry_run, create_backups)
            operations.extend(naming_fix_result.operations)
            errors.extend(naming_fix_result.errors)
            warnings.extend(naming_fix_result.warnings)
            
            # Fix file organization
            org_fix_result = self.fix_file_organization(target_path, dry_run, create_backups)
            operations.extend(org_fix_result.operations)
            errors.extend(org_fix_result.errors)
            warnings.extend(org_fix_result.warnings)
            
            # Calculate summary statistics
            total_attempted = len(operations)
            successful = len([op for op in operations if not any(str(op.file_path) in error for error in errors)])
            failed = len(errors)
            skipped = total_attempted - successful - failed
            
            success = len(errors) == 0
            summary = f"Fixed {successful}/{total_attempted} standards violations"
            if dry_run:
                summary = f"[DRY RUN] Would fix {successful}/{total_attempted} standards violations"
            
            return ModelStandardsFixResult(
                success=success,
                total_fixes_attempted=total_attempted,
                fixes_successful=successful,
                fixes_failed=failed,
                fixes_skipped=skipped,
                operations=operations,
                errors=errors,
                warnings=warnings,
                summary=summary,
                dry_run=dry_run
            )
            
        except Exception as e:
            return ModelStandardsFixResult(
                success=False,
                total_fixes_attempted=0,
                fixes_successful=0,
                fixes_failed=1,
                fixes_skipped=0,
                operations=[],
                errors=[f"Failed to fix standards violations: {str(e)}"],
                warnings=[],
                summary=f"Standards compliance fixing failed: {str(e)}",
                dry_run=dry_run
            )
    
    def fix_template_artifacts(
        self,
        target_path: Path,
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """Fix template artifacts in target path."""
        operations = []
        errors = []
        warnings = []
        
        try:
            if target_path.is_file():
                files_to_process = [target_path]
            else:
                files_to_process = list(target_path.rglob("*.py")) + list(target_path.rglob("*.yaml")) + list(target_path.rglob("*.md"))
            
            for file_path in files_to_process:
                try:
                    if not file_path.exists():
                        continue
                        
                    content = file_path.read_text(encoding='utf-8')
                    original_content = content
                    
                    # Replace template artifacts
                    for artifact in self.template_artifacts:
                        if artifact in content:
                            # Determine appropriate replacement based on context
                            replacement = self._get_template_replacement(artifact, file_path)
                            content = content.replace(artifact, replacement)
                    
                    # Only proceed if changes were made
                    if content != original_content:
                        operation = ModelStandardsFixOperation(
                            issue_type=EnumIssueType.TEMPLATE_ARTIFACT,
                            severity=SeverityLevelEnum.ERROR,
                            file_path=file_path,
                            description=f"Remove template artifacts from {file_path.name}",
                            old_value="Contains template artifacts",
                            new_value="Template artifacts removed"
                        )
                        
                        if not dry_run:
                            # Create backup if requested
                            if create_backups:
                                backup_path = self.create_backup(file_path)
                                operation.backup_created = backup_path is not None
                                operation.backup_path = backup_path
                            
                            # Write updated content
                            file_path.write_text(content, encoding='utf-8')
                        
                        operations.append(operation)
                        
                except Exception as e:
                    errors.append(f"Failed to fix template artifacts in {file_path}: {str(e)}")
            
            successful = len(operations)
            summary = f"Fixed template artifacts in {successful} files"
            if dry_run:
                summary = f"[DRY RUN] Would fix template artifacts in {successful} files"
            
            return ModelStandardsFixResult(
                success=len(errors) == 0,
                total_fixes_attempted=len(operations),
                fixes_successful=successful,
                fixes_failed=len(errors),
                fixes_skipped=0,
                operations=operations,
                errors=errors,
                warnings=warnings,
                summary=summary,
                dry_run=dry_run
            )
            
        except Exception as e:
            return ModelStandardsFixResult(
                success=False,
                total_fixes_attempted=0,
                fixes_successful=0,
                fixes_failed=1,
                fixes_skipped=0,
                operations=[],
                errors=[f"Failed to fix template artifacts: {str(e)}"],
                warnings=[],
                summary=f"Template artifact fixing failed: {str(e)}",
                dry_run=dry_run
            )
    
    def fix_naming_conventions(
        self,
        target_path: Path,
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """Fix naming convention violations in target path."""
        operations = []
        errors = []
        warnings = []
        
        try:
            if target_path.is_file():
                files_to_check = [target_path]
            else:
                files_to_check = list(target_path.rglob("*.py"))
            
            for file_path in files_to_check:
                try:
                    # Check file naming conventions
                    parent_dir = file_path.parent.name
                    file_name = file_path.name
                    
                    # Determine expected prefix based on parent directory
                    expected_prefix = self.file_prefixes.get(parent_dir)
                    
                    if expected_prefix and not file_name.startswith(expected_prefix) and not file_name.startswith('__'):
                        # Suggest new name with proper prefix
                        new_name = expected_prefix + file_name
                        new_path = file_path.parent / new_name
                        
                        operation = ModelStandardsFixOperation(
                            issue_type=EnumIssueType.NAMING_CONVENTION,
                            severity=SeverityLevelEnum.WARNING,
                            file_path=file_path,
                            description=f"Add {expected_prefix} prefix to {file_name}",
                            old_value=file_name,
                            new_value=new_name
                        )
                        
                        if not dry_run:
                            # Create backup if requested
                            if create_backups:
                                backup_path = self.create_backup(file_path)
                                operation.backup_created = backup_path is not None
                                operation.backup_path = backup_path
                            
                            # Rename file
                            file_path.rename(new_path)
                            
                            # Update imports in other files
                            self._update_imports_for_renamed_file(file_path, new_path, target_path)
                        
                        operations.append(operation)
                    
                    # Check class naming within files
                    if file_path.suffix == '.py':
                        class_fixes = self._fix_class_naming_in_file(file_path, dry_run, create_backups)
                        operations.extend(class_fixes)
                        
                except Exception as e:
                    errors.append(f"Failed to fix naming conventions in {file_path}: {str(e)}")
            
            successful = len(operations)
            summary = f"Fixed naming conventions in {successful} items"
            if dry_run:
                summary = f"[DRY RUN] Would fix naming conventions in {successful} items"
            
            return ModelStandardsFixResult(
                success=len(errors) == 0,
                total_fixes_attempted=len(operations),
                fixes_successful=successful,
                fixes_failed=len(errors),
                fixes_skipped=0,
                operations=operations,
                errors=errors,
                warnings=warnings,
                summary=summary,
                dry_run=dry_run
            )
            
        except Exception as e:
            return ModelStandardsFixResult(
                success=False,
                total_fixes_attempted=0,
                fixes_successful=0,
                fixes_failed=1,
                fixes_skipped=0,
                operations=[],
                errors=[f"Failed to fix naming conventions: {str(e)}"],
                warnings=[],
                summary=f"Naming convention fixing failed: {str(e)}",
                dry_run=dry_run
            )
    
    def fix_file_organization(
        self,
        target_path: Path,
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """Fix file organization issues."""
        operations = []
        errors = []
        warnings = []
        
        try:
            if target_path.is_file():
                files_to_check = [target_path]
            else:
                files_to_check = list(target_path.rglob("*.py"))
            
            for file_path in files_to_check:
                try:
                    # Check if models are in the right directory
                    if file_path.name.startswith('model_') and file_path.parent.name != 'models':
                        models_dir = file_path.parent / 'models'
                        if not models_dir.exists():
                            models_dir.mkdir(exist_ok=True)
                        
                        new_path = models_dir / file_path.name
                        
                        operation = ModelStandardsFixOperation(
                            issue_type=EnumIssueType.FILE_ORGANIZATION,
                            severity=SeverityLevelEnum.WARNING,
                            file_path=file_path,
                            description=f"Move model file to models/ directory",
                            old_value=str(file_path.relative_to(target_path)),
                            new_value=str(new_path.relative_to(target_path))
                        )
                        
                        if not dry_run:
                            if create_backups:
                                backup_path = self.create_backup(file_path)
                                operation.backup_created = backup_path is not None
                                operation.backup_path = backup_path
                            
                            shutil.move(str(file_path), str(new_path))
                            self._update_imports_for_moved_file(file_path, new_path, target_path)
                        
                        operations.append(operation)
                    
                    # Check if enums are in the right directory
                    elif file_path.name.startswith('enum_') and file_path.parent.name != 'enums':
                        enums_dir = file_path.parent / 'enums'
                        if not enums_dir.exists():
                            enums_dir.mkdir(exist_ok=True)
                        
                        new_path = enums_dir / file_path.name
                        
                        operation = ModelStandardsFixOperation(
                            issue_type=EnumIssueType.FILE_ORGANIZATION,
                            severity=SeverityLevelEnum.WARNING,
                            file_path=file_path,
                            description=f"Move enum file to enums/ directory",
                            old_value=str(file_path.relative_to(target_path)),
                            new_value=str(new_path.relative_to(target_path))
                        )
                        
                        if not dry_run:
                            if create_backups:
                                backup_path = self.create_backup(file_path)
                                operation.backup_created = backup_path is not None
                                operation.backup_path = backup_path
                            
                            shutil.move(str(file_path), str(new_path))
                            self._update_imports_for_moved_file(file_path, new_path, target_path)
                        
                        operations.append(operation)
                        
                except Exception as e:
                    errors.append(f"Failed to fix file organization for {file_path}: {str(e)}")
            
            successful = len(operations)
            summary = f"Fixed file organization for {successful} files"
            if dry_run:
                summary = f"[DRY RUN] Would fix file organization for {successful} files"
            
            return ModelStandardsFixResult(
                success=len(errors) == 0,
                total_fixes_attempted=len(operations),
                fixes_successful=successful,
                fixes_failed=len(errors),
                fixes_skipped=0,
                operations=operations,
                errors=errors,
                warnings=warnings,
                summary=summary,
                dry_run=dry_run
            )
            
        except Exception as e:
            return ModelStandardsFixResult(
                success=False,
                total_fixes_attempted=0,
                fixes_successful=0,
                fixes_failed=1,
                fixes_skipped=0,
                operations=[],
                errors=[f"Failed to fix file organization: {str(e)}"],
                warnings=[],
                summary=f"File organization fixing failed: {str(e)}",
                dry_run=dry_run
            )
    
    def validate_and_fix(
        self,
        target_path: Path,
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """Run validation and automatically fix detected issues."""
        return self.fix_standards_violations(target_path, dry_run, None, create_backups)
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """Create a backup of the specified file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup_{timestamp}")
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            return None
    
    def restore_from_backup(self, backup_path: Path, original_path: Path) -> bool:
        """Restore a file from its backup."""
        try:
            shutil.copy2(backup_path, original_path)
            return True
        except Exception:
            return False
    
    def _get_template_replacement(self, artifact: str, file_path: Path) -> str:
        """Get appropriate replacement for template artifact based on context."""
        # Try to infer node name from file path
        node_name = "node"
        
        # Look for node directory pattern
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part.endswith('_node') and i < len(parts) - 1:
                node_name = part
                break
        
        # Convert template artifacts to appropriate replacements
        if artifact == 'template_node':
            return node_name
        elif artifact == 'TemplateNode':
            return ''.join(word.capitalize() for word in node_name.split('_'))
        elif artifact == 'TEMPLATE_NODE':
            return node_name.upper()
        elif artifact == 'template-node':
            return node_name.replace('_', '-')
        elif artifact == 'Template Node':
            return node_name.replace('_', ' ').title()
        
        return node_name
    
    def _fix_class_naming_in_file(self, file_path: Path, dry_run: bool, create_backups: bool) -> List[ModelStandardsFixOperation]:
        """Fix class naming conventions within a Python file."""
        operations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    
                    # Check if enum classes start with "Enum"
                    if file_path.parent.name == 'enums' and not class_name.startswith('Enum'):
                        new_name = f"Enum{class_name}"
                        
                        operation = ModelStandardsFixOperation(
                            issue_type=EnumIssueType.NAMING_CONVENTION,
                            severity=SeverityLevelEnum.WARNING,
                            file_path=file_path,
                            description=f"Add Enum prefix to class {class_name}",
                            old_value=class_name,
                            new_value=new_name
                        )
                        
                        if not dry_run:
                            # Replace class name in content
                            content = re.sub(
                                rf'\bclass\s+{re.escape(class_name)}\b',
                                f'class {new_name}',
                                content
                            )
                            
                            if create_backups:
                                backup_path = self.create_backup(file_path)
                                operation.backup_created = backup_path is not None
                                operation.backup_path = backup_path
                            
                            file_path.write_text(content, encoding='utf-8')
                        
                        operations.append(operation)
                        
        except Exception:
            # If AST parsing fails, skip this file
            pass
        
        return operations
    
    def _update_imports_for_renamed_file(self, old_path: Path, new_path: Path, search_root: Path):
        """Update import statements when a file is renamed."""
        try:
            # Find all Python files that might import the renamed file
            for py_file in search_root.rglob("*.py"):
                if py_file == old_path or py_file == new_path:
                    continue
                
                try:
                    content = py_file.read_text(encoding='utf-8')
                    old_module = self._path_to_module_name(old_path, search_root)
                    new_module = self._path_to_module_name(new_path, search_root)
                    
                    if old_module in content:
                        updated_content = content.replace(old_module, new_module)
                        py_file.write_text(updated_content, encoding='utf-8')
                        
                except Exception:
                    continue
                    
        except Exception:
            pass
    
    def _update_imports_for_moved_file(self, old_path: Path, new_path: Path, search_root: Path):
        """Update import statements when a file is moved."""
        self._update_imports_for_renamed_file(old_path, new_path, search_root)
    
    def _path_to_module_name(self, file_path: Path, root_path: Path) -> str:
        """Convert file path to Python module name."""
        try:
            relative_path = file_path.relative_to(root_path)
            module_parts = list(relative_path.parts[:-1])  # Exclude filename
            module_parts.append(relative_path.stem)  # Add filename without extension
            return '.'.join(module_parts)
        except Exception:
            return str(file_path.stem)
    
    def _infer_node_info(self, target_path: Path) -> tuple[str, str]:
        """Infer node name and version from target path."""
        try:
            # Look for node directory pattern
            parts = target_path.parts
            node_name = "unknown_node"
            node_version = "1.0.0"
            
            # Find node name from path
            for i, part in enumerate(parts):
                if part.endswith('_node') and i < len(parts) - 1:
                    node_name = part
                    # Look for version directory
                    if i + 1 < len(parts) and parts[i + 1].startswith('v'):
                        version_part = parts[i + 1]
                        # Convert v1_0_0 to 1.0.0
                        if version_part.startswith('v') and '_' in version_part:
                            node_version = version_part[1:].replace('_', '.')
                    break
            
            # If target_path itself is a node directory
            if target_path.name.endswith('_node'):
                node_name = target_path.name
                # Look for version subdirectories
                for child in target_path.iterdir():
                    if child.is_dir() and child.name.startswith('v'):
                        version_part = child.name
                        if version_part.startswith('v') and '_' in version_part:
                            node_version = version_part[1:].replace('_', '.')
                        break
            
            return node_name, node_version
            
        except Exception:
            return "unknown_node", "1.0.0" 