from typing import Protocol, List
from pathlib import Path

from ..v1_0_0.models.model_validation_issue import ValidationIssueModel
from ..v1_0_0.models.model_template_validation_result import TemplateValidationResultModel
from ..v1_0_0.models.model_fix_result import FixResultModel
from ..v1_0_0.models.model_generation_result import GenerationResultModel


class IntrospectionGeneratorProtocol(Protocol):
    """Protocol for introspection generation tools"""
    
    def generate_introspection(self, contract_path: Path, output_path: Path) -> GenerationResultModel:
        """
        Generate introspection.py from contract.yaml with complete metadata extraction.
        
        Args:
            contract_path: Path to the contract.yaml file
            output_path: Path to write the generated introspection.py file
            
        Returns:
            Generation result with success status and file information
        """
        ...


class ErrorCodeGeneratorProtocol(Protocol):
    """Protocol for error code generation tools"""
    
    def generate_error_codes(self, contract_path: Path, output_path: Path, node_name: str) -> GenerationResultModel:
        """
        Generate error_codes.py from contract.yaml with ONEX integration.
        
        Args:
            contract_path: Path to the contract.yaml file
            output_path: Path to write the generated error_codes.py file
            node_name: Name of the node for proper enum naming
            
        Returns:
            Generation result with success status and file information
        """
        ...
    
    def validate_error_codes(self, error_codes_path: Path, contract_path: Path) -> bool:
        """
        Validate that error_codes.py is in sync with contract.yaml.
        
        Args:
            error_codes_path: Path to the error_codes.py file
            contract_path: Path to the contract.yaml file
            
        Returns:
            True if in sync, False otherwise
        """
        ...


class TemplateValidatorProtocol(Protocol):
    """Protocol for template validation tools"""
    
    def validate_template(self, node_dir: Path, node_name: str, node_version: str = "1.0.0") -> TemplateValidationResultModel:
        """
        Validate a node directory for template copy-paste errors and inconsistencies.
        
        Args:
            node_dir: Path to the node directory
            node_name: Expected node name
            node_version: Expected node version
            
        Returns:
            Template validation result with comprehensive metrics
        """
        ...
    
    def fix_template_issues(self, node_dir: Path, issues: List[ValidationIssueModel]) -> FixResultModel:
        """
        Automatically fix template issues where possible.
        
        Args:
            node_dir: Path to the node directory
            issues: List of validation issues to fix
            
        Returns:
            Fix operation result with metrics
        """
        ...


class CodeGeneratorProtocol(Protocol):
    """Unified protocol for all code generation operations"""
    
    def generate_all(self, node_dir: Path, node_name: str, node_version: str = "1.0.0") -> GenerationResultModel:
        """
        Generate all code artifacts for a node (introspection, error codes, etc.).
        
        Args:
            node_dir: Path to the node directory
            node_name: Name of the node
            node_version: Version of the node
            
        Returns:
            Comprehensive generation result
        """
        ...
    
    def validate_all(self, node_dir: Path, node_name: str, node_version: str = "1.0.0") -> TemplateValidationResultModel:
        """
        Validate all generated code artifacts for a node.
        
        Args:
            node_dir: Path to the node directory
            node_name: Name of the node
            node_version: Version of the node
            
        Returns:
            Comprehensive validation result
        """
        ...
    
    def regenerate_if_needed(self, node_dir: Path, node_name: str, node_version: str = "1.0.0") -> GenerationResultModel:
        """
        Regenerate code artifacts only if they are out of sync or missing.
        
        Args:
            node_dir: Path to the node directory
            node_name: Name of the node
            node_version: Version of the node
            
        Returns:
            Generation result indicating what was regenerated
        """
        ... 