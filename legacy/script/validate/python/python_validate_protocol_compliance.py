# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_protocol_compliance"
# namespace: "omninode.tools.python_validate_protocol_compliance"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.dev"
# description: "Validates protocol compliance in Python code"
# === OmniNode:Tool_Metadata ===

import ast
import os
import re
import logging
from typing import Dict, List, Optional, Set, Tuple

from foundation.template.python.python_test_base_validator import PythonTestProtocolValidate
from foundation.model.model_validate_error import (
    ValidateMessageModel,
    ValidateResultModel,
)
from foundation.model.model_validate import ValidateStatus
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.protocol.protocol_validate_async import ProtocolValidateAsync
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.protocol.protocol_validate_metadata_block import ProtocolValidateMetadataBlock
from foundation.protocol.protocol_cli import ProtocolCLI
from foundation.protocol.protocol_cli_tool import ProtocolCLITool
from foundation.protocol.protocol_test import ProtocolTest
from foundation.protocol.protocol_tool import ProtocolTool
from foundation.protocol.protocol_testable_cli import ProtocolTestableCLI
from foundation.protocol.protocol_validator_registry import ProtocolValidatorRegistry
from foundation.protocol.protocol_registry import RegistryProtocol
from foundation.protocol.protocol_orchestrator import OrchestratorProtocol
from foundation.protocol.protocol_output_formatter import OutputFormatterProtocol
from foundation.protocol.protocol_process_runner import ProcessRunnerProtocol
from foundation.protocol.protocol_repository import ProtocolRepository
from foundation.protocol.protocol_stamper import ProtocolStamper
from foundation.protocol.protocol_stamper_ignore import ProtocolStamperIgnore
from foundation.protocol.protocol_vcs_client import VCSClientProtocol
from foundation.protocol.protocol_yaml_utils import ProtocolYamlUtils
from foundation.protocol.protocol_file_utils import ProtocolFileUtils
from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.protocol.protocol_log_entry import ProtocolLogEntry
from foundation.protocol.protocol_database import ProtocolDatabase
from foundation.script.validate.validate_registry import validate_registry

"""
Validator to check protocol compliance.
Validates that protocol implementations follow the required interface.
"""

def find_protocol_imports(tree: ast.AST) -> Set[str]:
    """Find protocol imports in AST."""
    protocols = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "foundation.protocol":
            for name in node.names:
                if name.name.startswith("Protocol"):
                    protocols.add(name.name)
    return protocols


def find_protocol_implementations(tree: ast.AST) -> Dict[str, List[str]]:
    """Find protocol implementations in AST."""
    implementations = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id.startswith("Protocol"):
                    implementations[node.name] = [base.id]
    return implementations


def get_method_args(method_def: ast.FunctionDef) -> Dict[str, bool]:
    """Get method arguments and their optional status."""
    args = {}
    
    # Handle positional arguments
    defaults = [None] * (len(method_def.args.args) - len(method_def.args.defaults)) + list(method_def.args.defaults)
    for arg, default in zip(method_def.args.args, defaults):
        args[arg.arg] = default is not None
    
    # Handle keyword-only arguments
    if method_def.args.kwonlyargs:
        kw_defaults = method_def.args.kw_defaults
        for arg, default in zip(method_def.args.kwonlyargs, kw_defaults):
            args[arg.arg] = default is not None
    
    return args


def check_method_compliance(method_def: ast.FunctionDef, required_args: Dict[str, bool]) -> List[str]:
    """Check method compliance with required arguments."""
    errors = []
    actual_args = get_method_args(method_def)
    
    # Check for missing required arguments
    for arg_name, is_optional in required_args.items():
        if arg_name not in actual_args:
            errors.append(f"Missing required argument '{arg_name}'")
        elif actual_args[arg_name] != is_optional:
            if is_optional:
                errors.append(f"Argument '{arg_name}' should be optional")
            else:
                errors.append(f"Argument '{arg_name}' should be required")
    
    return errors


def check_class_compliance(class_def: ast.ClassDef, protocol_name: str, required_methods: Dict[str, Dict[str, bool]]) -> List[str]:
    """Check class compliance with protocol requirements."""
    errors = []
    
    # Find all method names and their definitions
    method_defs = {}
    for node in ast.walk(class_def):
        if isinstance(node, ast.FunctionDef):
            method_defs[node.name] = node
    
    # Check for missing methods
    for method_name, required_args in required_methods.items():
        if method_name not in method_defs:
            errors.append(f"Missing required method '{method_name}' from {protocol_name}")
        else:
            method_errors = check_method_compliance(method_defs[method_name], required_args)
            for error in method_errors:
                errors.append(f"Method '{method_name}' from {protocol_name}: {error}")
    
    return errors


class ProtocolComplianceValidator(ProtocolValidateMetadataBlock):
    """Validator to check protocol compliance."""
    
    def __init__(self):
        """Initialize the validator."""
        self.name = "protocol_compliance"
        self.description = "Validates that protocol implementations follow the required interface"
        self.logger = logging.getLogger(__name__)
    
    def validate(self, target: str, config: Optional[Dict] = None) -> ValidateResultModel:
        """Validate protocol compliance in a Python file."""
        self.logger.info(f"Validating protocol compliance for {target}")
        errors = []
        try:
            with open(target, "r") as f:
                content = f.read()
            tree = ast.parse(content)
            
            # Find protocol imports
            imported_protocols = find_protocol_imports(tree)
            self.logger.info(f"Found imported protocols: {imported_protocols}")
            
            # Find protocol implementations
            implementations = find_protocol_implementations(tree)
            self.logger.info(f"Found protocol implementations: {implementations}")
            
            # Check each implementation
            for class_name, protocols in implementations.items():
                for protocol in protocols:
                    if protocol not in imported_protocols:
                        error_msg = f"Class {class_name} implements {protocol} but it's not imported"
                        self.logger.error(error_msg)
                        errors.append(error_msg)
                    
                    # Check method compliance regardless of import status
                    if protocol == "ProtocolValidateMetadataBlock":
                        required_methods = {
                            "validate": {"target": False, "config": True},
                            "get_name": {}
                        }
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef) and node.name == class_name:
                                method_errors = check_class_compliance(node, protocol, required_methods)
                                for error in method_errors:
                                    self.logger.error(error)
                                errors.extend(method_errors)
        except Exception as e:
            error_msg = f"Error processing {target}: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        
        messages = [ValidateMessageModel(message=error) for error in errors]
        status = ValidateStatus.VALID if not errors else ValidateStatus.INVALID
        self.logger.info(f"Protocol compliance validation {'passed' if status == ValidateStatus.VALID else 'failed'} for {target}")
        return ValidateResultModel(
            messages=messages,
            status=status
        )
    
    def get_name(self) -> str:
        """Get the name of the validator."""
        return self.name


# Register the validator
validate_registry.register(
    name="protocol_compliance",
    validator_cls=ProtocolComplianceValidator,
    meta={
        "name": "protocol_compliance",
        "group": "protocol",
        "description": "Validates that protocol implementations follow the required interface",
        "version": "v1",
    }) 