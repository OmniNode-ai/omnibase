"""
Canonical ONEX registry for node_manager node.
- Inherits from BaseOnexRegistry for DRY, standards-compliant, context-aware tool injection.
- All canonical tools are registered via CANONICAL_TOOLS; context-aware factories supported.

Usage:
    node_dir = Path(__file__).parent
    registry = RegistryNodeManager(node_dir)
    # Register custom tools as needed
    registry.register_tool('CUSTOM_TOOL', CustomToolClass)
"""

# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical registry for node_manager tools and dependencies
# === /OmniNode:Metadata ===

from typing import Dict, Type, Optional
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocol.protocol_tool import ProtocolTool
from omnibase.protocol.protocol_logger import ProtocolLogger
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.core.core_errors import RegistryErrorCode, RegistryErrorModel, OnexError
from omnibase.nodes.node_manager.v1_0_0.tools.tool_contract_to_model import generate_state_models
from omnibase.nodes.node_manager.v1_0_0.tools.tool_backend_selection import StubBackendSelection
from omnibase.nodes.node_manager.v1_0_0.tools.tool_maintenance import ToolMaintenance
from omnibase.nodes.node_manager.v1_0_0.tools.tool_validation_engine import ToolValidationEngine
from omnibase.nodes.node_manager.v1_0_0.tools.tool_template_engine import ToolTemplateEngine
from omnibase.nodes.node_manager.v1_0_0.tools.tool_cli_commands import ToolCliCommands
from omnibase.nodes.node_manager.v1_0_0.tools.tool_file_generator import ToolFileGenerator
from omnibase.runtimes.onex_runtime.v1_0_0.protocols.protocol_metadata_loader import ProtocolMetadataLoader
from omnibase.nodes.node_manager.v1_0_0.tools.tool_cli_node_parity import ToolCliNodeParity
from omnibase.nodes.node_manager.v1_0_0.tools.tool_schema_conformance import ToolSchemaConformance
from omnibase.nodes.node_manager.v1_0_0.tools.tool_error_code_usage import ToolErrorCodeUsage
from omnibase.nodes.node_manager.v1_0_0.tools.tool_contract_compliance import ToolContractCompliance
from omnibase.nodes.node_manager.v1_0_0.tools.tool_introspection_validity import ToolIntrospectionValidity
from omnibase.nodes.node_manager.v1_0_0.tools.tool_node_discovery import NodeDiscoveryTool
from omnibase.nodes.node_manager.v1_0_0.tools.tool_node_validation import NodeValidationTool
from omnibase.nodes.node_manager.v1_0_0.tools.tool_schema_generator import ToolSchemaGenerator
from omnibase.nodes.node_manager.v1_0_0.tools.tool_standards_compliance_fixer import ToolStandardsComplianceFixer
from omnibase.nodes.node_manager.v1_0_0.tools.tool_parity_validator_with_fixes import ToolParityValidatorWithFixes
from pathlib import Path
from omnibase.registry.base_registry import BaseOnexRegistry
from omnibase.nodes.node_logger.v1_0_0.tools.tool_logger_emit_log_event import ToolLoggerEmitLogEvent
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_scenario_runner import ToolScenarioRunner

# Context-aware factory for metadata loader
def make_metadata_loader_lambda(node_dir):
    from omnibase.runtimes.onex_runtime.v1_0_0.tools.metadata_loader_tool import ToolMetadataLoader
    return lambda: ToolMetadataLoader()
make_metadata_loader_lambda._is_context_factory = True

class RegistryNodeManager(BaseOnexRegistry):
    """
    Canonical registry for pluggable tools in node_manager node.
    Inherits from BaseOnexRegistry for DRY, standards-compliant, context-aware tool injection.
    """
    CANONICAL_TOOLS = {
        "CONTRACT_TO_MODEL": generate_state_models,
        "BACKEND_SELECTION": StubBackendSelection,
        "MAINTENANCE": ToolMaintenance,
        "VALIDATION_ENGINE": ToolValidationEngine,
        "TEMPLATE_ENGINE": ToolTemplateEngine,
        "CLI_COMMANDS": ToolCliCommands,
        "FILE_GENERATOR": ToolFileGenerator,
        "METADATA_LOADER": make_metadata_loader_lambda,
        "CLI_NODE_PARITY": ToolCliNodeParity,
        "SCHEMA_CONFORMANCE": ToolSchemaConformance,
        "ERROR_CODE_USAGE": ToolErrorCodeUsage,
        "CONTRACT_COMPLIANCE": ToolContractCompliance,
        "INTROSPECTION_VALIDITY": ToolIntrospectionValidity,
        "NODE_DISCOVERY": NodeDiscoveryTool,
        "NODE_VALIDATION": NodeValidationTool,
        "SCHEMA_GENERATOR": ToolSchemaGenerator,
        "STANDARDS_COMPLIANCE_FIXER": ToolStandardsComplianceFixer,  # Standards compliance auto-fix tool
        "PARITY_VALIDATOR_WITH_FIXES": ToolParityValidatorWithFixes,  # Enhanced parity validator with fixes
        "tool_logger_emit_log_event": ToolLoggerEmitLogEvent,  # Protocol-compliant logger tool
        "scenario_runner": ToolScenarioRunner,  # Scenario runner tool for protocol-pure architecture
    }

    def __init__(self, node_dir: Path, tool_collection: Optional[dict] = None, logger: Optional[ProtocolLogger] = None, mode: ToolRegistryModeEnum = ToolRegistryModeEnum.REAL):
        self._tools: Dict[str, Type[ProtocolTool]] = {}
        self.mode: ToolRegistryModeEnum = mode
        self.logger: Optional[ProtocolLogger] = logger
        if tool_collection is not None:
            for name, tool_cls in tool_collection.items():
                self.register_tool(name, tool_cls)
        else:
            for name, tool_cls in self.CANONICAL_TOOLS.items():
                self.register_tool(name, tool_cls)

    def set_mode(self, mode: ToolRegistryModeEnum) -> None:
        if mode not in (ToolRegistryModeEnum.REAL, ToolRegistryModeEnum.MOCK):
            if self.logger:
                self.logger.log(f"Invalid registry mode: {mode}")
            raise OnexError(
                message=f"Invalid registry mode: {mode}",
                error_code=RegistryErrorCode.INVALID_MODE
            )
        self.mode = mode
        if self.logger:
            self.logger.log(f"Registry mode set to: {mode}")

    def set_logger(self, logger: Optional[ProtocolLogger]) -> None:
        self.logger = logger

    def register_tool(self, key: str, tool_cls: Type[ProtocolTool]) -> None:
        if key in self._tools:
            if self.logger:
                self.logger.log(f"Duplicate tool registration: {key}")
            raise OnexError(
                message=f"Tool '{key}' is already registered.",
                error_code=RegistryErrorCode.DUPLICATE_TOOL
            )
        self._tools[key] = tool_cls
        if self.logger:
            self.logger.log(f"Registered tool: {key}")

    def get_tool(self, key: str) -> Optional[Type[ProtocolTool]]:
        tool = self._tools.get(key)
        if tool is None:
            if self.logger:
                self.logger.log(f"Tool not found: {key}")
            return None
        return tool

    def list_tools(self) -> Dict[str, Type[ProtocolTool]]:
        return dict(self._tools)

# Usage: instantiate and inject as needed; do not use singletons. 