from pathlib import Path
import yaml
import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context

from ..models.model_error_code_metadata import ErrorCodeMetadataModel


class ErrorCodeGenerator:
    """Enhanced error code generator with ONEX integration and metadata support"""
    
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.enum_name = f"{node_name.upper().replace('-', '_')}ErrorCode"
        
        # Standard ONEX error categories
        self.standard_categories = {
            "validation": "Input validation and schema errors",
            "processing": "Core processing and business logic errors", 
            "external": "External service and dependency errors",
            "configuration": "Configuration and setup errors",
            "resource": "Resource allocation and management errors",
            "security": "Security and authorization errors",
            "network": "Network and connectivity errors",
            "timeout": "Timeout and performance errors",
            "general": "General purpose errors"
        }
        
        # Exit code mappings following ONEX conventions
        self.exit_code_mappings = {
            "validation": 2,
            "processing": 3,
            "external": 4,
            "configuration": 5,
            "resource": 6,
            "security": 7,
            "network": 8,
            "timeout": 9,
            "general": 1
        }
    
    def extract_error_codes_from_contract(self, contract: dict) -> List[ErrorCodeMetadataModel]:
        """Extract error codes from contract with enhanced metadata"""
        error_codes = []
        error_section = contract.get("error_codes", [])
        
        if isinstance(error_section, list):
            # Simple list format - infer metadata
            for i, code in enumerate(error_section):
                if isinstance(code, str):
                    category = self._infer_category_from_code(code)
                    error_codes.append(ErrorCodeMetadataModel(
                        code=code,
                        number=i + 1,
                        description=self._generate_description_from_code(code),
                        exit_code=self.exit_code_mappings.get(category, 1),
                        category=category
                    ))
                    
        elif isinstance(error_section, dict):
            # Enhanced format with explicit metadata
            for i, (code, metadata) in enumerate(error_section.items()):
                if isinstance(metadata, dict):
                    category = metadata.get("category", self._infer_category_from_code(code))
                    error_codes.append(ErrorCodeMetadataModel(
                        code=code,
                        number=metadata.get("number", i + 1),
                        description=metadata.get("description", self._generate_description_from_code(code)),
                        exit_code=metadata.get("exit_code", self.exit_code_mappings.get(category, 1)),
                        category=category
                    ))
                else:
                    # Simple key-value where value is description
                    category = self._infer_category_from_code(code)
                    error_codes.append(ErrorCodeMetadataModel(
                        code=code,
                        number=i + 1,
                        description=str(metadata) if metadata else self._generate_description_from_code(code),
                        exit_code=self.exit_code_mappings.get(category, 1),
                        category=category
                    ))
        
        return error_codes
    
    def _infer_category_from_code(self, code: str) -> str:
        """Infer error category from error code name"""
        code_lower = code.lower()
        
        # Validation patterns
        if any(pattern in code_lower for pattern in ["validation", "invalid", "schema", "format", "parse"]):
            return "validation"
        
        # Processing patterns
        if any(pattern in code_lower for pattern in ["processing", "execution", "operation", "failed", "error"]):
            return "processing"
        
        # External patterns
        if any(pattern in code_lower for pattern in ["external", "service", "api", "remote", "dependency"]):
            return "external"
        
        # Configuration patterns
        if any(pattern in code_lower for pattern in ["config", "setup", "initialization", "missing"]):
            return "configuration"
        
        # Resource patterns
        if any(pattern in code_lower for pattern in ["resource", "memory", "disk", "quota", "limit"]):
            return "resource"
        
        # Security patterns
        if any(pattern in code_lower for pattern in ["security", "auth", "permission", "access", "forbidden"]):
            return "security"
        
        # Network patterns
        if any(pattern in code_lower for pattern in ["network", "connection", "socket", "http", "tcp"]):
            return "network"
        
        # Timeout patterns
        if any(pattern in code_lower for pattern in ["timeout", "deadline", "expired", "slow"]):
            return "timeout"
        
        return "general"
    
    def _generate_description_from_code(self, code: str) -> str:
        """Generate human-readable description from error code"""
        # Convert SCREAMING_SNAKE_CASE to readable text
        words = code.lower().replace('_', ' ').split()
        
        # Capitalize first word and add context
        if words:
            description = ' '.join(words).capitalize()
            
            # Add contextual suffixes based on patterns
            if any(word in words for word in ["failed", "error", "invalid"]):
                description += " occurred"
            elif any(word in words for word in ["missing", "not", "no"]):
                description += " detected"
            elif any(word in words for word in ["timeout", "expired"]):
                description += " exceeded"
            else:
                description += " error"
                
            return description
        
        return f"Error code: {code}"
    
    def generate_error_codes_file(self, contract_path: Path, output_path: Path) -> None:
        """Generate enhanced error_codes.py file from contract"""
        # Load contract
        with open(contract_path, "r") as f:
            contract = yaml.safe_load(f)
        
        # Extract error codes with metadata
        error_codes = self.extract_error_codes_from_contract(contract)
        
        # Generate file content
        header = self._generate_file_header()
        imports = self._generate_imports()
        enum_class = self._generate_enum_class(error_codes)
        helper_functions = self._generate_helper_functions(error_codes)
        
        content = f"{header}\n{imports}\n\n{enum_class}\n\n{helper_functions}"
        
        # Write file
        with open(output_path, "w") as f:
            f.write(content)
        
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Generated enhanced error_codes.py with {len(error_codes)} error codes for {self.node_name}",
            context=make_log_context(node_id="error_code_generator"),
        )
    
    def _generate_file_header(self) -> str:
        """Generate file header with metadata"""
        return f'''# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml with enhanced ONEX error code integration
# Node: {self.node_name}
# Generated at: {datetime.now().isoformat()}
# To regenerate: run the node_manager error code generation tool'''
    
    def _generate_imports(self) -> str:
        """Generate necessary imports"""
        return '''from enum import Enum
from typing import Dict, Optional

from omnibase.core.core_error_codes import CoreErrorCode
from omnibase.core.core_onex_error import OnexError'''
    
    def _generate_enum_class(self, error_codes: List[ErrorCodeMetadataModel]) -> str:
        """Generate the error code enum class"""
        if not error_codes:
            return f'''class {self.enum_name}(str, Enum):
    """Error codes for {self.node_name} node"""
    # No node-specific error codes defined
    # Use CoreErrorCode for standard ONEX errors
    pass'''
        
        enum_entries = []
        for error_code in error_codes:
            enum_entries.append(f'    {error_code.code} = "{error_code.code}"')
        
        enum_body = "\n".join(enum_entries)
        
        return f'''class {self.enum_name}(str, Enum):
    """Error codes for {self.node_name} node with enhanced metadata"""
{enum_body}'''
    
    def _generate_helper_functions(self, error_codes: List[ErrorCodeMetadataModel]) -> str:
        """Generate helper functions for error handling"""
        if not error_codes:
            return '''# No helper functions needed - use CoreErrorCode utilities'''
        
        # Generate metadata dictionary
        metadata_entries = []
        for error_code in error_codes:
            metadata_entries.append(f'''    {self.enum_name}.{error_code.code}: {{
        "number": {error_code.number},
        "description": "{error_code.description}",
        "exit_code": {error_code.exit_code},
        "category": "{error_code.category}"
    }}''')
        
        metadata_dict = ",\n".join(metadata_entries)
        
        return f'''# Error code metadata for enhanced error handling
ERROR_CODE_METADATA: Dict[{self.enum_name}, Dict[str, any]] = {{
{metadata_dict}
}}


def get_error_metadata(error_code: {self.enum_name}) -> Dict[str, any]:
    """Get metadata for a specific error code"""
    return ERROR_CODE_METADATA.get(error_code, {{}})


def create_onex_error(error_code: {self.enum_name}, message: str, **kwargs) -> OnexError:
    """Create an OnexError with proper metadata"""
    metadata = get_error_metadata(error_code)
    return OnexError(
        message=message,
        error_code=error_code,
        exit_code=metadata.get("exit_code", 1),
        **kwargs
    )


def get_error_category(error_code: {self.enum_name}) -> str:
    """Get the category for an error code"""
    metadata = get_error_metadata(error_code)
    return metadata.get("category", "general")


def get_error_description(error_code: {self.enum_name}) -> str:
    """Get the description for an error code"""
    metadata = get_error_metadata(error_code)
    return metadata.get("description", f"Error code: {{error_code}}")'''


def tool_generate_error_codes(contract_path: Path, output_path: Path, node_name: str) -> None:
    """
    Generate enhanced error_codes.py file from contract.yaml with ONEX integration.
    
    Args:
        contract_path: Path to the contract.yaml file
        output_path: Path to write the generated error_codes.py file
        node_name: Name of the node for proper enum naming
    """
    generator = ErrorCodeGenerator(node_name)
    generator.generate_error_codes_file(contract_path, output_path)


def tool_validate_error_codes(error_codes_path: Path, contract_path: Path) -> bool:
    """
    Validate that error_codes.py is in sync with contract.yaml.
    
    Args:
        error_codes_path: Path to the error_codes.py file
        contract_path: Path to the contract.yaml file
        
    Returns:
        True if in sync, False otherwise
    """
    # Load contract
    with open(contract_path, "r") as f:
        contract = yaml.safe_load(f)
    
    # Extract expected error codes
    expected_codes = set()
    error_section = contract.get("error_codes", [])
    
    if isinstance(error_section, list):
        expected_codes = set(error_section)
    elif isinstance(error_section, dict):
        expected_codes = set(error_section.keys())
    
    # Parse existing error_codes.py
    if not error_codes_path.exists():
        return len(expected_codes) == 0
    
    with open(error_codes_path, "r") as f:
        content = f.read()
    
    # Extract actual error codes from enum
    actual_codes = set()
    for line in content.split('\n'):
        match = re.match(r'\s+(\w+)\s*=\s*"(\w+)"', line)
        if match:
            actual_codes.add(match.group(1))
    
    is_in_sync = expected_codes == actual_codes
    
    emit_log_event_sync(
        LogLevelEnum.INFO if is_in_sync else LogLevelEnum.WARNING,
        f"Error codes validation: {'in sync' if is_in_sync else 'out of sync'} - Expected: {len(expected_codes)}, Actual: {len(actual_codes)}",
        context=make_log_context(node_id="error_code_validator"),
    )
    
    return is_in_sync 