from pathlib import Path
from typing import List
from datetime import datetime

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context

from ..models.model_validation_issue import ValidationIssueModel
from ..models.model_template_validation_result import TemplateValidationResultModel
from ..models.model_fix_result import FixResultModel
from ..models.model_generation_result import GenerationResultModel
from ...protocols.protocol_code_generator import (
    IntrospectionGeneratorProtocol,
    ErrorCodeGeneratorProtocol,
    TemplateValidatorProtocol,
    CodeGeneratorProtocol
)
from .tool_generate_introspection import tool_generate_introspection
from .tool_generate_error_codes import tool_generate_error_codes, tool_validate_error_codes
from .tool_template_validator import tool_validate_template, tool_fix_template_issues


class UnifiedCodeGenerator:
    """Unified code generator implementing all generation protocols"""
    
    def __init__(self):
        self.generation_history: List[GenerationResultModel] = []
    
    def generate_introspection(self, contract_path: Path, output_path: Path) -> GenerationResultModel:
        """Generate introspection.py with result tracking"""
        start_time = datetime.now()
        errors = []
        warnings = []
        files_generated = []
        
        try:
            # Call the existing tool
            tool_generate_introspection(contract_path, output_path)
            files_generated.append(str(output_path))
            success = True
        except Exception as e:
            errors.append(f"Introspection generation failed: {e}")
            success = False
        
        result = GenerationResultModel(
            success=success,
            files_generated=files_generated,
            files_modified=[],
            errors=errors,
            warnings=warnings,
            generation_time=start_time,
            node_name=contract_path.parent.parent.name,
            operation_type="introspection",
            total_operations=1
        )
        
        self.generation_history.append(result)
        return result
    
    def generate_error_codes(self, contract_path: Path, output_path: Path, node_name: str) -> GenerationResultModel:
        """Generate error_codes.py with result tracking"""
        start_time = datetime.now()
        errors = []
        warnings = []
        files_generated = []
        
        try:
            # Call the existing tool
            tool_generate_error_codes(contract_path, output_path, node_name)
            files_generated.append(str(output_path))
            success = True
        except Exception as e:
            errors.append(f"Error code generation failed: {e}")
            success = False
        
        result = GenerationResultModel(
            success=success,
            files_generated=files_generated,
            files_modified=[],
            errors=errors,
            warnings=warnings,
            generation_time=start_time,
            node_name=node_name,
            operation_type="error_codes",
            total_operations=1
        )
        
        self.generation_history.append(result)
        return result
    
    def validate_error_codes(self, error_codes_path: Path, contract_path: Path) -> bool:
        """Validate error codes sync status"""
        return tool_validate_error_codes(error_codes_path, contract_path)
    
    def validate_template(self, node_dir: Path, node_name: str, node_version: str = "1.0.0") -> TemplateValidationResultModel:
        """Validate template with enhanced result tracking"""
        return tool_validate_template(node_dir, node_name, node_version)
    
    def fix_template_issues(self, node_dir: Path, issues: List[ValidationIssueModel]) -> FixResultModel:
        """Fix template issues with result tracking"""
        return tool_fix_template_issues(node_dir, issues)
    
    def generate_all(self, node_dir: Path, node_name: str, node_version: str = "1.0.0") -> GenerationResultModel:
        """Generate all code artifacts for a node"""
        start_time = datetime.now()
        all_errors = []
        all_warnings = []
        all_files_generated = []
        all_files_modified = []
        operations_completed = 0
        
        version_dir = node_dir / f"v{node_version.replace('.', '_')}"
        contract_path = version_dir / "contract.yaml"
        
        # Generate introspection
        introspection_result = self.generate_introspection(
            contract_path, 
            version_dir / "introspection.py"
        )
        all_errors.extend(introspection_result.errors)
        all_warnings.extend(introspection_result.warnings)
        all_files_generated.extend(introspection_result.files_generated)
        operations_completed += 1
        
        # Generate error codes
        error_codes_result = self.generate_error_codes(
            contract_path,
            version_dir / "error_codes.py",
            node_name
        )
        all_errors.extend(error_codes_result.errors)
        all_warnings.extend(error_codes_result.warnings)
        all_files_generated.extend(error_codes_result.files_generated)
        operations_completed += 1
        
        # Validate template
        validation_result = self.validate_template(node_dir, node_name, node_version)
        if validation_result.error_count > 0:
            all_warnings.append(f"Template validation found {validation_result.error_count} errors")
        
        # Auto-fix template issues if any
        if validation_result.issues:
            fix_result = self.fix_template_issues(node_dir, validation_result.issues)
            if fix_result.success:
                all_files_modified.extend([issue.file_path for issue in validation_result.issues[:fix_result.fixed_count]])
                operations_completed += 1
        
        overall_success = len(all_errors) == 0
        
        result = GenerationResultModel(
            success=overall_success,
            files_generated=all_files_generated,
            files_modified=all_files_modified,
            errors=all_errors,
            warnings=all_warnings,
            generation_time=start_time,
            node_name=node_name,
            operation_type="generate_all",
            total_operations=operations_completed
        )
        
        emit_log_event_sync(
            LogLevelEnum.INFO if overall_success else LogLevelEnum.ERROR,
            f"Code generation completed for {node_name}: {operations_completed} operations, {len(all_files_generated)} files generated, {len(all_errors)} errors",
            context=make_log_context(node_id="unified_code_generator"),
        )
        
        self.generation_history.append(result)
        return result
    
    def validate_all(self, node_dir: Path, node_name: str, node_version: str = "1.0.0") -> TemplateValidationResultModel:
        """Validate all generated code artifacts"""
        # For now, this primarily focuses on template validation
        # Can be extended to include error code sync validation, etc.
        validation_result = self.validate_template(node_dir, node_name, node_version)
        
        # Add error code sync validation
        version_dir = node_dir / f"v{node_version.replace('.', '_')}"
        error_codes_path = version_dir / "error_codes.py"
        contract_path = version_dir / "contract.yaml"
        
        if error_codes_path.exists() and contract_path.exists():
            is_in_sync = self.validate_error_codes(error_codes_path, contract_path)
            if not is_in_sync:
                # Add a synthetic validation issue for out-of-sync error codes
                from ..enums.enum_issue_type import EnumIssueType
                from omnibase.enums.log_level import SeverityLevelEnum
                
                sync_issue = ValidationIssueModel(
                    file_path=str(error_codes_path),
                    line_number=1,
                    issue_type=EnumIssueType.PARSE_ERROR,  # Reusing existing enum
                    description="Error codes are out of sync with contract.yaml",
                    severity=SeverityLevelEnum.WARNING,
                    suggested_fix="Regenerate error codes from contract"
                )
                validation_result.issues.append(sync_issue)
                validation_result.warning_count += 1
        
        return validation_result
    
    def regenerate_if_needed(self, node_dir: Path, node_name: str, node_version: str = "1.0.0") -> GenerationResultModel:
        """Regenerate code artifacts only if needed"""
        start_time = datetime.now()
        errors = []
        warnings = []
        files_generated = []
        operations_completed = 0
        
        version_dir = node_dir / f"v{node_version.replace('.', '_')}"
        contract_path = version_dir / "contract.yaml"
        
        # Check if introspection needs regeneration
        introspection_path = version_dir / "introspection.py"
        if not introspection_path.exists() or self._file_needs_update(introspection_path, contract_path):
            result = self.generate_introspection(contract_path, introspection_path)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
            files_generated.extend(result.files_generated)
            operations_completed += 1
        
        # Check if error codes need regeneration
        error_codes_path = version_dir / "error_codes.py"
        if not error_codes_path.exists() or not self.validate_error_codes(error_codes_path, contract_path):
            result = self.generate_error_codes(contract_path, error_codes_path, node_name)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
            files_generated.extend(result.files_generated)
            operations_completed += 1
        
        success = len(errors) == 0
        
        result = GenerationResultModel(
            success=success,
            files_generated=files_generated,
            files_modified=[],
            errors=errors,
            warnings=warnings,
            generation_time=start_time,
            node_name=node_name,
            operation_type="regenerate_if_needed",
            total_operations=operations_completed
        )
        
        if operations_completed > 0:
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"Regenerated {operations_completed} artifacts for {node_name}",
                context=make_log_context(node_id="unified_code_generator"),
            )
        
        self.generation_history.append(result)
        return result
    
    def _file_needs_update(self, target_file: Path, source_file: Path) -> bool:
        """Check if target file needs update based on source file modification time"""
        if not target_file.exists():
            return True
        
        if not source_file.exists():
            return False
        
        return source_file.stat().st_mtime > target_file.stat().st_mtime
    
    def get_generation_history(self) -> List[GenerationResultModel]:
        """Get history of all generation operations"""
        return self.generation_history.copy()
    
    def clear_history(self) -> None:
        """Clear generation history"""
        self.generation_history.clear()


# Convenience functions that use the unified generator
_generator = UnifiedCodeGenerator()

def tool_generate_all_code(node_dir: Path, node_name: str, node_version: str = "1.0.0") -> GenerationResultModel:
    """Generate all code artifacts for a node using the unified generator"""
    return _generator.generate_all(node_dir, node_name, node_version)

def tool_validate_all_code(node_dir: Path, node_name: str, node_version: str = "1.0.0") -> TemplateValidationResultModel:
    """Validate all code artifacts for a node using the unified generator"""
    return _generator.validate_all(node_dir, node_name, node_version)

def tool_regenerate_if_needed(node_dir: Path, node_name: str, node_version: str = "1.0.0") -> GenerationResultModel:
    """Regenerate code artifacts only if needed using the unified generator"""
    return _generator.regenerate_if_needed(node_dir, node_name, node_version) 