from typing import Dict, Any, Type, Protocol, Optional, runtime_checkable
from abc import ABC, abstractmethod
import inspect
from omnibase.enums.enum_dependency_mode import DependencyModeEnum
from omnibase.model.model_external_service_config import ModelExternalServiceConfig
from omnibase.protocol.protocol_tool import ProtocolTool
from omnibase.protocol.protocol_logger import ProtocolLogger
from omnibase.core.core_errors import OnexError, CoreErrorCode


@runtime_checkable
class ProtocolToolFactory(Protocol):
    """
    Protocol for tool factories that create real vs mock tools based on dependency mode.
    Enables conditional dependency injection for external services.
    """
    
    def create_tool(
        self, 
        tool_key: str, 
        dependency_mode: DependencyModeEnum,
        external_service_config: Optional[ModelExternalServiceConfig] = None,
        logger: Optional[ProtocolLogger] = None
    ) -> Type[ProtocolTool]:
        """Create a tool instance based on dependency mode and configuration."""
        ...
    
    def supports_tool(self, tool_key: str) -> bool:
        """Check if this factory can create the specified tool."""
        ...
    
    def validate_tool_compatibility(
        self, 
        real_tool: Type[ProtocolTool], 
        mock_tool: Type[ProtocolTool]
    ) -> list[str]:
        """Validate that real and mock tools have compatible interfaces."""
        ...


class BaseToolFactory(ABC):
    """
    Abstract base class for tool factories.
    Provides common functionality for real vs mock tool creation.
    """
    
    def __init__(self, logger: Optional[ProtocolLogger] = None):
        self.logger = logger
        self._real_tools: Dict[str, Type[ProtocolTool]] = {}
        self._mock_tools: Dict[str, Type[ProtocolTool]] = {}
        self._registered_tools: set[str] = set()
    
    def register_tool_pair(
        self, 
        tool_key: str, 
        real_tool: Type[ProtocolTool], 
        mock_tool: Type[ProtocolTool]
    ) -> None:
        """Register a real/mock tool pair."""
        # Validate tool compatibility
        compatibility_issues = self.validate_tool_compatibility(real_tool, mock_tool)
        if compatibility_issues and self.logger:
            for issue in compatibility_issues:
                self.logger.log(f"[ToolFactory] Warning: {issue}")
        
        self._real_tools[tool_key] = real_tool
        self._mock_tools[tool_key] = mock_tool
        self._registered_tools.add(tool_key)
        
        if self.logger:
            self.logger.log(f"[ToolFactory] Registered tool pair: {tool_key}")
    
    def create_tool(
        self, 
        tool_key: str, 
        dependency_mode: DependencyModeEnum,
        external_service_config: Optional[ModelExternalServiceConfig] = None,
        logger: Optional[ProtocolLogger] = None
    ) -> Type[ProtocolTool]:
        """Create a tool based on dependency mode."""
        if not self.supports_tool(tool_key):
            raise OnexError(
                f"Tool '{tool_key}' not supported by this factory",
                CoreErrorCode.INVALID_PARAMETER
            )
        
        if dependency_mode.is_real():
            tool_class = self._real_tools[tool_key]
            if logger:
                logger.log(f"[ToolFactory] Creating real tool: {tool_key} -> {tool_class.__name__}")
        else:
            tool_class = self._mock_tools[tool_key]
            if logger:
                logger.log(f"[ToolFactory] Creating mock tool: {tool_key} -> {tool_class.__name__}")
        
        return tool_class
    
    def supports_tool(self, tool_key: str) -> bool:
        """Check if this factory can create the specified tool."""
        return tool_key in self._registered_tools
    
    def validate_tool_compatibility(
        self, 
        real_tool: Type[ProtocolTool], 
        mock_tool: Type[ProtocolTool]
    ) -> list[str]:
        """Validate that real and mock tools have compatible interfaces."""
        issues = []
        
        # Get method signatures for both tools
        real_methods = inspect.getmembers(real_tool, predicate=inspect.ismethod)
        mock_methods = inspect.getmembers(mock_tool, predicate=inspect.ismethod)
        
        real_method_names = {name for name, _ in real_methods}
        mock_method_names = {name for name, _ in mock_methods}
        
        # Check for missing methods
        missing_in_mock = real_method_names - mock_method_names
        missing_in_real = mock_method_names - real_method_names
        
        for method in missing_in_mock:
            issues.append(f"Method '{method}' exists in real tool but not in mock tool")
        
        for method in missing_in_real:
            issues.append(f"Method '{method}' exists in mock tool but not in real tool")
        
        # Check signature compatibility for common methods
        common_methods = real_method_names & mock_method_names
        for method_name in common_methods:
            real_method = getattr(real_tool, method_name)
            mock_method = getattr(mock_tool, method_name)
            
            try:
                real_sig = inspect.signature(real_method)
                mock_sig = inspect.signature(mock_method)
                
                if real_sig != mock_sig:
                    issues.append(
                        f"Method '{method_name}' has different signatures: "
                        f"real={real_sig}, mock={mock_sig}"
                    )
            except (ValueError, TypeError):
                # Skip signature comparison for methods that can't be inspected
                continue
        
        return issues


class EventBusToolFactory(BaseToolFactory):
    """
    Tool factory for event bus backends (Kafka, InMemory, etc.).
    Provides conditional injection of real vs mock event bus implementations.
    """
    
    def __init__(self, logger: Optional[ProtocolLogger] = None):
        super().__init__(logger)
        self._register_default_event_bus_tools()
    
    def _register_default_event_bus_tools(self) -> None:
        """Register default event bus tool pairs."""
        # Import here to avoid circular dependencies
        try:
            from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import KafkaEventBus
            from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
            
            self.register_tool_pair("event_bus", KafkaEventBus, InMemoryEventBus)
            self.register_tool_pair("kafka", KafkaEventBus, InMemoryEventBus)
            self.register_tool_pair("inmemory", InMemoryEventBus, InMemoryEventBus)
            
        except ImportError as e:
            if self.logger:
                self.logger.log(f"[EventBusToolFactory] Warning: Could not import event bus tools: {e}")


class ToolFactoryRegistry:
    """
    Registry for managing multiple tool factories.
    Enables extensible tool creation for different service types.
    """
    
    def __init__(self, logger: Optional[ProtocolLogger] = None):
        self.logger = logger
        self._factories: Dict[str, ProtocolToolFactory] = {}
        self._register_default_factories()
    
    def _register_default_factories(self) -> None:
        """Register default tool factories."""
        self.register_factory("event_bus", EventBusToolFactory(self.logger))
    
    def register_factory(self, service_type: str, factory: ProtocolToolFactory) -> None:
        """Register a tool factory for a specific service type."""
        self._factories[service_type] = factory
        if self.logger:
            self.logger.log(f"[ToolFactoryRegistry] Registered factory for service type: {service_type}")
    
    def create_tool(
        self,
        tool_key: str,
        dependency_mode: DependencyModeEnum,
        external_service_config: Optional[ModelExternalServiceConfig] = None,
        logger: Optional[ProtocolLogger] = None
    ) -> Type[ProtocolTool]:
        """Create a tool using the appropriate factory."""
        # Try to find a factory that supports this tool
        for service_type, factory in self._factories.items():
            if factory.supports_tool(tool_key):
                return factory.create_tool(
                    tool_key, dependency_mode, external_service_config, logger
                )
        
        # If no factory found, raise error
        raise OnexError(
            f"No factory found for tool '{tool_key}'. Available factories: {list(self._factories.keys())}",
            CoreErrorCode.INVALID_PARAMETER
        )
    
    def get_supported_tools(self) -> Dict[str, list[str]]:
        """Get all tools supported by registered factories."""
        supported = {}
        for service_type, factory in self._factories.items():
            if hasattr(factory, '_registered_tools'):
                supported[service_type] = list(factory._registered_tools)
        return supported


# Global registry instance
_global_tool_factory_registry: Optional[ToolFactoryRegistry] = None


def get_tool_factory_registry(logger: Optional[ProtocolLogger] = None) -> ToolFactoryRegistry:
    """Get the global tool factory registry instance."""
    global _global_tool_factory_registry
    if _global_tool_factory_registry is None:
        _global_tool_factory_registry = ToolFactoryRegistry(logger)
    return _global_tool_factory_registry 