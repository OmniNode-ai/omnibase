from pathlib import Path
import yaml
import re
from typing import List, Dict, Any, Set, Tuple

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums.log_level import LogLevelEnum, SeverityLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context

from ..models.model_validation_issue import ValidationIssueModel
from ..models.model_template_validation_result import TemplateValidationResultModel
from ..models.model_fix_result import FixResultModel
from ..enums.enum_issue_type import EnumIssueType


class TemplateValidator:
    """Validates generated files for template copy-paste errors and inconsistencies"""
    
    def __init__(self, node_name: str, node_version: str):
        self.node_name = node_name
        self.node_version = node_version
        self.issues: List[ValidationIssueModel] = []
        
        # Common template artifacts that should be replaced
        self.template_artifacts = {
            "template-node",
            "template-node", 
            "template-node",
            "template-node",
            "node_template",
            "NodeTemplate",
            "NODE_TEMPLATE",
            "node-template",
            "example_node",
            "ExampleNode",
            "EXAMPLE_NODE",
            "example-node"
        }
        
        # File patterns to validate
        self.validation_patterns = {
            "node.onex.yaml": self._validate_node_metadata,
            "contract.yaml": self._validate_contract,
            "README.md": self._validate_readme,
            "introspection.py": self._validate_introspection,
            "node.py": self._validate_node_implementation,
            "error_codes.py": self._validate_error_codes,
            "state.py": self._validate_state_models
        }
    
    def validate_node_directory(self, node_dir: Path) -> List[ValidationIssueModel]:
        """Validate all files in a node directory for template artifacts"""
        self.issues = []
        
        # Validate versioned directory
        version_dir = node_dir / f"v{self.node_version.replace('.', '_')}"
        if not version_dir.exists():
            self.issues.append(ValidationIssueModel(
                file_path=str(version_dir),
                line_number=0,
                issue_type=EnumIssueType.MISSING_DIRECTORY,
                description=f"Version directory {version_dir.name} not found",
                severity=SeverityLevelEnum.ERROR,
                suggested_fix=f"Create directory: {version_dir}"
            ))
            return self.issues
        
        # Validate specific files
        for file_pattern, validator in self.validation_patterns.items():
            file_path = version_dir / file_pattern
            if file_path.exists():
                validator(file_path)
        
        # Validate all Python files for template artifacts
        for py_file in version_dir.rglob("*.py"):
            self._validate_python_file(py_file)
        
        # Validate all YAML files for template artifacts
        for yaml_file in version_dir.rglob("*.yaml"):
            self._validate_yaml_file(yaml_file)
        
        # Validate all Markdown files for template artifacts
        for md_file in version_dir.rglob("*.md"):
            self._validate_markdown_file(md_file)
        
        return self.issues
    
    def _validate_node_metadata(self, file_path: Path):
        """Validate node.onex.yaml for template artifacts"""
        try:
            with open(file_path, "r") as f:
                content = f.read()
                metadata = yaml.safe_load(content)
            
            # Check for template artifacts in metadata
            if metadata.get("node_name") != self.node_name:
                self.issues.append(ValidationIssueModel(
                    file_path=str(file_path),
                    line_number=self._find_line_number(content, "node_name"),
                    issue_type=EnumIssueType.INCORRECT_NODE_NAME,
                    description=f"Node name '{metadata.get('node_name')}' does not match expected '{self.node_name}'",
                    severity=SeverityLevelEnum.ERROR,
                    suggested_fix=f"Change node_name to: {self.node_name}"
                ))
            
            # Check for template artifacts in any field
            self._check_content_for_artifacts(str(file_path), content)
            
        except Exception as e:
            self.issues.append(ValidationIssueModel(
                file_path=str(file_path),
                line_number=0,
                issue_type=EnumIssueType.PARSE_ERROR,
                description=f"Failed to parse YAML: {e}",
                severity=SeverityLevelEnum.ERROR
            ))
    
    def _validate_contract(self, file_path: Path):
        """Validate contract.yaml for template artifacts"""
        try:
            with open(file_path, "r") as f:
                content = f.read()
                contract = yaml.safe_load(content)
            
            # Check node name in contract
            if contract.get("node_name") != self.node_name:
                self.issues.append(ValidationIssueModel(
                    file_path=str(file_path),
                    line_number=self._find_line_number(content, "node_name"),
                    issue_type=EnumIssueType.INCORRECT_NODE_NAME,
                    description=f"Contract node_name '{contract.get('node_name')}' does not match expected '{self.node_name}'",
                    severity=SeverityLevelEnum.ERROR,
                    suggested_fix=f"Change node_name to: {self.node_name}"
                ))
            
            # Check for template artifacts
            self._check_content_for_artifacts(str(file_path), content)
            
        except Exception as e:
            self.issues.append(ValidationIssueModel(
                file_path=str(file_path),
                line_number=0,
                issue_type=EnumIssueType.PARSE_ERROR,
                description=f"Failed to parse contract: {e}",
                severity=SeverityLevelEnum.ERROR
            ))
    
    def _validate_readme(self, file_path: Path):
        """Validate README.md for template artifacts"""
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for proper node name in title
        if f"# {self.node_name}" not in content and f"# {self.node_name.replace('_', ' ').title()}" not in content:
            self.issues.append(ValidationIssueModel(
                file_path=str(file_path),
                line_number=1,
                issue_type=EnumIssueType.INCORRECT_TITLE,
                description=f"README title should reference '{self.node_name}'",
                severity=SeverityLevelEnum.WARNING,
                suggested_fix=f"Update title to include: {self.node_name}"
            ))
        
        self._check_content_for_artifacts(str(file_path), content)
    
    def _validate_introspection(self, file_path: Path):
        """Validate introspection.py for template artifacts"""
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for TODO comments (should be eliminated)
        todo_lines = [i+1 for i, line in enumerate(content.split('\n')) if 'TODO' in line]
        for line_num in todo_lines:
            self.issues.append(ValidationIssueModel(
                file_path=str(file_path),
                line_number=line_num,
                issue_type=EnumIssueType.TODO_FOUND,
                description="TODO comment found in generated introspection",
                severity=SeverityLevelEnum.WARNING,
                suggested_fix="Complete the TODO or regenerate introspection"
            ))
        
        self._check_content_for_artifacts(str(file_path), content)
    
    def _validate_node_implementation(self, file_path: Path):
        """Validate node.py for template artifacts"""
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for proper class naming
        expected_class = f"{self.node_name.title().replace('_', '')}Node"
        if f"class {expected_class}" not in content:
            self.issues.append(ValidationIssueModel(
                file_path=str(file_path),
                line_number=self._find_line_number(content, "class "),
                issue_type=EnumIssueType.INCORRECT_CLASS_NAME,
                description=f"Expected class name '{expected_class}' not found",
                severity=SeverityLevelEnum.WARNING,
                suggested_fix=f"Ensure main class is named: {expected_class}"
            ))
        
        self._check_content_for_artifacts(str(file_path), content)
    
    def _validate_error_codes(self, file_path: Path):
        """Validate error_codes.py for template artifacts"""
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for proper enum naming
        expected_enum = f"{self.node_name.upper()}ErrorCode"
        if f"class {expected_enum}" not in content:
            self.issues.append(ValidationIssueModel(
                file_path=str(file_path),
                line_number=self._find_line_number(content, "class "),
                issue_type=EnumIssueType.INCORRECT_ENUM_NAME,
                description=f"Expected error code enum '{expected_enum}' not found",
                severity=SeverityLevelEnum.WARNING,
                suggested_fix=f"Ensure error code enum is named: {expected_enum}"
            ))
        
        self._check_content_for_artifacts(str(file_path), content)
    
    def _validate_state_models(self, file_path: Path):
        """Validate state.py for template artifacts"""
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for proper model naming
        expected_input = f"{self.node_name.title().replace('_', '')}InputState"
        expected_output = f"{self.node_name.title().replace('_', '')}OutputState"
        
        if f"class {expected_input}" not in content:
            self.issues.append(ValidationIssueModel(
                file_path=str(file_path),
                line_number=self._find_line_number(content, "InputState"),
                issue_type=EnumIssueType.INCORRECT_MODEL_NAME,
                description=f"Expected input model '{expected_input}' not found",
                severity=SeverityLevelEnum.WARNING,
                suggested_fix=f"Ensure input model is named: {expected_input}"
            ))
        
        if f"class {expected_output}" not in content:
            self.issues.append(ValidationIssueModel(
                file_path=str(file_path),
                line_number=self._find_line_number(content, "OutputState"),
                issue_type=EnumIssueType.INCORRECT_MODEL_NAME,
                description=f"Expected output model '{expected_output}' not found",
                severity=SeverityLevelEnum.WARNING,
                suggested_fix=f"Ensure output model is named: {expected_output}"
            ))
        
        self._check_content_for_artifacts(str(file_path), content)
    
    def _validate_python_file(self, file_path: Path):
        """Validate any Python file for template artifacts"""
        with open(file_path, "r") as f:
            content = f.read()
        
        self._check_content_for_artifacts(str(file_path), content)
    
    def _validate_yaml_file(self, file_path: Path):
        """Validate any YAML file for template artifacts"""
        with open(file_path, "r") as f:
            content = f.read()
        
        self._check_content_for_artifacts(str(file_path), content)
    
    def _validate_markdown_file(self, file_path: Path):
        """Validate any Markdown file for template artifacts"""
        with open(file_path, "r") as f:
            content = f.read()
        
        self._check_content_for_artifacts(str(file_path), content)
    
    def _check_content_for_artifacts(self, file_path: str, content: str):
        """Check content for template artifacts"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for artifact in self.template_artifacts:
                if artifact in line:
                    # Skip if it's in a comment explaining the template
                    if any(comment_marker in line for comment_marker in ['#', '//', '<!--', '"""', "'''"]):
                        continue
                    
                    self.issues.append(ValidationIssueModel(
                        file_path=file_path,
                        line_number=i + 1,
                        issue_type=EnumIssueType.TEMPLATE_ARTIFACT,
                        description=f"Template artifact '{artifact}' found in line: {line.strip()}",
                        severity=SeverityLevelEnum.ERROR,
                        suggested_fix=f"Replace '{artifact}' with appropriate value for {self.node_name}"
                    ))
    
    def _find_line_number(self, content: str, search_term: str) -> int:
        """Find line number containing search term"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if search_term in line:
                return i + 1
        return 0


def tool_validate_template(node_dir: Path, node_name: str, node_version: str = "1.0.0") -> TemplateValidationResultModel:
    """
    Validate a node directory for template copy-paste errors and inconsistencies.
    
    Args:
        node_dir: Path to the node directory
        node_name: Expected node name
        node_version: Expected node version
        
    Returns:
        Template validation result with comprehensive metrics
    """
    validator = TemplateValidator(node_name, node_version)
    issues = validator.validate_node_directory(node_dir)
    
    # Calculate metrics
    error_count = len([i for i in issues if i.severity == SeverityLevelEnum.ERROR])
    warning_count = len([i for i in issues if i.severity == SeverityLevelEnum.WARNING])
    info_count = len([i for i in issues if i.severity == SeverityLevelEnum.INFO])
    
    # Count total files checked (rough estimate)
    version_dir = node_dir / f"v{node_version.replace('.', '_')}"
    total_files = len(list(version_dir.rglob("*.py"))) + len(list(version_dir.rglob("*.yaml"))) + len(list(version_dir.rglob("*.md")))
    
    result = TemplateValidationResultModel(
        issues=issues,
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
        total_files_checked=total_files,
        node_name=node_name,
        validation_passed=(error_count == 0)
    )
    
    # Log validation results
    if issues:
        emit_log_event_sync(
            LogLevelEnum.WARNING if error_count == 0 else LogLevelEnum.ERROR,
            f"Template validation completed for {node_name}: {error_count} errors, {warning_count} warnings",
            context=make_log_context(node_id="template_validator"),
        )
    else:
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Template validation passed for {node_name}: no issues found",
            context=make_log_context(node_id="template_validator"),
        )
    
    return result


def tool_fix_template_issues(node_dir: Path, issues: List[ValidationIssueModel]) -> FixResultModel:
    """
    Automatically fix template issues where possible.
    
    Args:
        node_dir: Path to the node directory
        issues: List of validation issues to fix
        
    Returns:
        Fix operation result with metrics
    """
    fixed_count = 0
    failed_fixes = []
    
    for issue in issues:
        if issue.issue_type == EnumIssueType.TEMPLATE_ARTIFACT and issue.suggested_fix:
            try:
                file_path = Path(issue.file_path)
                if file_path.exists():
                    with open(file_path, "r") as f:
                        content = f.read()
                    
                    # Apply simple replacements
                    for artifact in ["template-node", "template-node", "template-node"]:
                        if artifact in content:
                            replacement = issue.suggested_fix.split("'")[1] if "'" in issue.suggested_fix else "node_manager"
                            content = content.replace(artifact, replacement)
                            fixed_count += 1
                    
                    with open(file_path, "w") as f:
                        f.write(content)
                        
            except Exception as e:
                failed_fixes.append(f"{issue.file_path}: {e}")
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"Failed to fix issue in {issue.file_path}: {e}",
                    context=make_log_context(node_id="template_validator"),
                )
    
    result = FixResultModel(
        fixed_count=fixed_count,
        failed_fixes=failed_fixes,
        success=(len(failed_fixes) == 0),
        node_name=str(node_dir.name),
        total_issues_processed=len(issues)
    )
    
    if fixed_count > 0:
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Automatically fixed {fixed_count} template issues",
            context=make_log_context(node_id="template_validator"),
        )
    
    return result 