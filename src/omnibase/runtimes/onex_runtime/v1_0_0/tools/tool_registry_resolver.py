from typing import Optional, Type
import yaml
import os
from omnibase.constants import GET_ACTIVE_REGISTRY_CONFIG_METHOD, NO_REGISTRY_TOOLS_ERROR_MSG, CONFIG_KEY, REGISTRY_TOOLS_KEY
from omnibase.protocol.protocol_registry_resolver import ProtocolRegistryResolver
from omnibase.protocol.protocol_registry import ProtocolRegistry
from omnibase.core.core_errors import OnexError, CoreErrorCode
from omnibase.model.model_scenario import ScenarioConfigModel
from omnibase.model.model_registry_resolution import ModelRegistryResolutionContext, ModelRegistryResolutionResult
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.enums.enum_dependency_mode import DependencyModeEnum
from omnibase.tools.tool_factories import get_tool_factory_registry
import inspect
from pathlib import Path

class RegistryResolverTool(ProtocolRegistryResolver):
    def resolve_registry(
        self,
        registry_class: type,
        scenario_path: Optional[Path] = None,
        logger: Optional[object] = None,
        fallback_tools: Optional[dict] = None,
        force_dependency_mode: Optional[DependencyModeEnum] = None,
    ) -> ProtocolRegistry:
        if scenario_path and scenario_path.exists():
            with open(scenario_path, "r") as f:
                scenario_yaml = yaml.unsafe_load(f)
            config = scenario_yaml.get(CONFIG_KEY, scenario_yaml)
            
            # Parse scenario config using proper model
            scenario_config = ScenarioConfigModel(**config)
            
            # Create resolution context
            context = ModelRegistryResolutionContext(
                scenario_path=scenario_path,
                dependency_mode=scenario_config.dependency_mode,
                external_services=scenario_config.external_services,
                force_dependency_mode=force_dependency_mode,
                node_dir=scenario_path.parent.parent if scenario_path else None
            )
            
            # Log resolved dependency mode for audit trail
            effective_mode = context.get_effective_dependency_mode()
            if logger:
                logger.log(f"[RegistryResolver] Resolved dependency_mode: {effective_mode}")
                if context.external_services and effective_mode.is_real():
                    logger.log(f"[RegistryResolver] External services config: {list(context.external_services.keys())}")
            
            # Get registry tools
            registry_tools = None
            if hasattr(config, GET_ACTIVE_REGISTRY_CONFIG_METHOD) and getattr(config, 'registry_configs', None):
                registry_tools = config.get_active_registry_config().tools
            elif getattr(config, REGISTRY_TOOLS_KEY, None):
                registry_tools = getattr(config, REGISTRY_TOOLS_KEY)
            elif isinstance(config.get(REGISTRY_TOOLS_KEY), dict):
                registry_tools = config[REGISTRY_TOOLS_KEY]
            else:
                raise OnexError(CoreErrorCode.MISSING_REQUIRED_PARAMETER, NO_REGISTRY_TOOLS_ERROR_MSG)
            
            context.registry_tools = registry_tools
            
            # === Apply Tool Factory Pattern ===
            final_tools = self._apply_dependency_mode_tools(context, logger)
            
            # Inspect registry_class signature for node_dir and dependency_mode support
            sig = inspect.signature(registry_class)
            params = list(sig.parameters.values())
            param_names = [p.name for p in params]
            
            kwargs = {
                "tool_collection": final_tools,
                "logger": logger
            }
            
            if "node_dir" in param_names:
                kwargs["node_dir"] = context.node_dir
                
            if "dependency_mode" in param_names:
                kwargs["dependency_mode"] = effective_mode
                
            if "external_services" in param_names:
                kwargs["external_services"] = context.external_services
                
            return registry_class(**kwargs)
        else:
            # No scenario path - use fallback behavior
            sig = inspect.signature(registry_class)
            params = list(sig.parameters.values())
            param_names = [p.name for p in params]
            
            kwargs = {"logger": logger}
            
            if "node_dir" in param_names:
                if scenario_path:
                    kwargs["node_dir"] = scenario_path.parent.parent
                else:
                    kwargs["node_dir"] = None
                
            registry = registry_class(**kwargs)
            if fallback_tools:
                for key, tool in fallback_tools.items():
                    registry.register_tool(key, tool)
            return registry
    
    def _apply_dependency_mode_tools(
        self, 
        context: ModelRegistryResolutionContext,
        logger: Optional[object] = None
    ) -> dict:
        """Apply tool factory pattern based on dependency mode."""
        effective_mode = context.get_effective_dependency_mode()
        if logger:
            logger.log(f"[RegistryResolver] Applying tools for dependency_mode: {effective_mode}")
        
        # Get the tool factory registry
        factory_registry = get_tool_factory_registry(logger)
        
        # Process each tool through the factory system
        final_tools = {}
        for tool_key, original_tool in context.registry_tools.items():
            try:
                # Try to create tool using factory
                external_service_config = context.get_external_service(tool_key)
                factory_tool = factory_registry.create_tool(
                    tool_key, effective_mode, external_service_config, logger
                )
                final_tools[tool_key] = factory_tool
                if logger:
                    logger.log(f"[RegistryResolver] Factory resolved {tool_key}: {effective_mode} -> {factory_tool.__name__}")
            except Exception as e:
                # If factory can't handle this tool, use original
                final_tools[tool_key] = original_tool
                if logger:
                    logger.log(f"[RegistryResolver] Factory passthrough {tool_key}: {original_tool} (reason: {e})")
        
        return final_tools

registry_resolver_tool = RegistryResolverTool() 