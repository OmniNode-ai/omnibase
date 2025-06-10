from typing import Optional, Type
import yaml
import os
from omnibase.constants import GET_ACTIVE_REGISTRY_CONFIG_METHOD, NO_REGISTRY_TOOLS_ERROR_MSG, CONFIG_KEY, REGISTRY_TOOLS_KEY
from omnibase.protocol.protocol_registry_resolver import ProtocolRegistryResolver
from omnibase.protocol.protocol_registry import ProtocolRegistry
from omnibase.core.errors import OnexError, CoreErrorCode

class RegistryResolverTool(ProtocolRegistryResolver):
    def resolve_registry(
        self,
        registry_class: type,
        scenario_path: Optional[str] = None,
        logger: Optional[object] = None,
        fallback_tools: Optional[dict] = None,
    ) -> ProtocolRegistry:
        if scenario_path and os.path.exists(scenario_path):
            with open(scenario_path, "r") as f:
                scenario_yaml = yaml.unsafe_load(f)
            config = scenario_yaml.get(CONFIG_KEY, scenario_yaml)
            registry_tools = None
            if hasattr(config, GET_ACTIVE_REGISTRY_CONFIG_METHOD) and getattr(config, 'registry_configs', None):
                registry_tools = config.get_active_registry_config().tools
            elif getattr(config, REGISTRY_TOOLS_KEY, None):
                registry_tools = getattr(config, REGISTRY_TOOLS_KEY)
            elif isinstance(config.get(REGISTRY_TOOLS_KEY), dict):
                registry_tools = config[REGISTRY_TOOLS_KEY]
            else:
                raise OnexError(CoreErrorCode.MISSING_REQUIRED_PARAMETER, NO_REGISTRY_TOOLS_ERROR_MSG)
            return registry_class(tool_collection=registry_tools, logger=logger)
        else:
            registry = registry_class(logger=logger)
            if fallback_tools:
                for key, tool in fallback_tools.items():
                    registry.register_tool(key, tool)
            return registry

registry_resolver_tool = RegistryResolverTool() 