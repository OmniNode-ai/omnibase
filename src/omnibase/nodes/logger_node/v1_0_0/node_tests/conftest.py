"""
Test configuration and fixtures for logger_node tests.

This module provides shared fixtures and configuration for all logger_node tests,
ensuring protocol-pure, fixture-injected testing patterns.
"""

import pytest
from unittest.mock import Mock

from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry


@pytest.fixture
def protocol_event_bus() -> ProtocolEventBus:
    """
    Provide a protocol-compliant event bus for testing.
    
    Returns:
        InMemoryEventBus instance for protocol-pure testing
    """
    return InMemoryEventBus()


@pytest.fixture
def mock_event_bus() -> Mock:
    """
    Provide a mock event bus for testing event emission.
    
    Returns:
        Mock object that can track event bus calls
    """
    return Mock(spec=ProtocolEventBus)


@pytest.fixture
def handler_registry(protocol_event_bus: ProtocolEventBus) -> FileTypeHandlerRegistry:
    """
    Provide a file type handler registry with all handlers registered.
    
    Args:
        protocol_event_bus: Event bus for protocol-pure logging
        
    Returns:
        FileTypeHandlerRegistry with all available handlers
    """
    registry = FileTypeHandlerRegistry(event_bus=protocol_event_bus)
    registry.register_all_handlers()
    return registry 