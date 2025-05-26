# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_structured_logging.py
# version: 1.0.0
# uuid: 9081eba4-9001-4525-93ee-5e17329c3abe
# author: OmniNode Team
# created_at: 2025-05-26T16:02:10.291491
# last_modified_at: 2025-05-26T20:03:27.496072
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: ca4bd51cf9c5f8262ead9c11a2f614782e5deff5211481fb65017d44eda6d05c
# entrypoint: python@test_structured_logging.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_structured_logging
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Simplified test suite for ONEX structured logging infrastructure.

This test suite focuses on the core functionality without complex mocking
that causes mypy issues.
"""

import os
from io import StringIO
from unittest.mock import Mock, patch

from omnibase.core.structured_logging import (
    OnexLoggingConfig,
    StructuredLoggingAdapter,
    emit_log_event,
    reset_structured_logging,
    setup_structured_logging,
    structured_print,
)
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)


class TestOnexLoggingConfig:
    """Test suite for OnexLoggingConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = OnexLoggingConfig()

        assert config.log_level == LogLevelEnum.INFO
        assert config.include_caller_info is True
        assert config.include_timestamps is True
        assert config.enable_correlation_ids is True

    def test_from_environment_defaults(self) -> None:
        """Test configuration from environment with default values."""
        with patch.dict(os.environ, {}, clear=True):
            config = OnexLoggingConfig.from_environment()

            assert config.log_level == LogLevelEnum.INFO
            assert config.include_caller_info is True
            assert config.include_timestamps is True
            assert config.enable_correlation_ids is True


class TestStructuredLoggingAdapter:
    """Test suite for StructuredLoggingAdapter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.event_bus = InMemoryEventBus()
        self.config = OnexLoggingConfig()
        self.adapter = StructuredLoggingAdapter(self.config, self.event_bus)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        reset_structured_logging()

    def test_adapter_initialization(self) -> None:
        """Test adapter initializes correctly."""
        assert self.adapter.config == self.config
        assert self.adapter.event_bus == self.event_bus

    def test_adapter_subscribes_to_log_events(self) -> None:
        """Test adapter subscribes to events."""
        # Verify subscription was registered
        assert len(self.event_bus._subscribers) == 1
        assert self.adapter._handle_log_event in self.event_bus._subscribers


class TestEmitLogEvent:
    """Test suite for emit_log_event function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        reset_structured_logging()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        reset_structured_logging()

    def test_emit_log_event_auto_initialization(self) -> None:
        """Test emit_log_event auto-initializes structured logging."""
        # Mock the setup function to verify it's called
        with patch(
            "omnibase.core.structured_logging.setup_structured_logging"
        ) as mock_setup:
            emit_log_event(LogLevelEnum.INFO, "test message")
            mock_setup.assert_called_once()

    def test_emit_log_event_fallback_no_event_bus(self) -> None:
        """Test emit_log_event fallback when event bus is not available."""
        # Reset to ensure no structured logging is set up
        reset_structured_logging()

        # Prevent auto-initialization by mocking setup_structured_logging
        with patch(
            "omnibase.core.structured_logging.setup_structured_logging"
        ) as mock_setup:
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                emit_log_event(LogLevelEnum.ERROR, "test error message")

                # Should have called setup but still failed due to no event bus
                mock_setup.assert_called_once()
                stderr_output = mock_stderr.getvalue()
                # The fallback message includes the enum representation
                assert "[FALLBACK]" in stderr_output
                assert "test error message" in stderr_output


class TestStructuredPrint:
    """Test suite for structured_print function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        reset_structured_logging()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        reset_structured_logging()

    def test_structured_print_basic(self) -> None:
        """Test structured_print with basic arguments."""
        # Mock emit_log_event to verify it's called correctly
        with patch("omnibase.core.structured_logging.emit_log_event") as mock_emit:
            structured_print("Hello", "world", 123)

            mock_emit.assert_called_once()
            args, kwargs = mock_emit.call_args
            assert args[0] == LogLevelEnum.INFO  # Default level
            assert args[1] == "Hello world 123"  # Joined message


class TestSetupStructuredLogging:
    """Test suite for setup_structured_logging function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        reset_structured_logging()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        reset_structured_logging()

    def test_setup_with_defaults(self) -> None:
        """Test setup with default configuration."""
        setup_structured_logging()

        # Verify global state is set
        from omnibase.core.structured_logging import _global_adapter, _global_event_bus

        assert _global_adapter is not None
        assert _global_event_bus is not None

    def test_setup_disables_python_logging(self) -> None:
        """Test that setup disables Python logging."""
        import logging

        # Ensure Python logging is enabled initially
        logging.disable(logging.NOTSET)
        # Set root logger level to INFO to ensure it's enabled for INFO messages
        logging.getLogger().setLevel(logging.INFO)
        assert logging.getLogger().isEnabledFor(logging.INFO)

        with patch.object(
            StructuredLoggingAdapter, "_get_logger_node_runner"
        ) as mock_runner:
            mock_runner.return_value = Mock()
            setup_structured_logging()

            # Python logging should now be disabled
            assert not logging.getLogger().isEnabledFor(logging.CRITICAL)


class TestResetStructuredLogging:
    """Test suite for reset_structured_logging function."""

    def test_reset_clears_global_state(self) -> None:
        """Test reset clears global state."""
        # Set up structured logging first
        setup_structured_logging()

        # Verify it's set up
        from omnibase.core.structured_logging import _global_adapter, _global_event_bus

        assert _global_adapter is not None
        assert _global_event_bus is not None

        # Reset and verify it's cleared
        reset_structured_logging()
        from omnibase.core.structured_logging import _global_adapter, _global_event_bus

        assert _global_adapter is None
        assert _global_event_bus is None

    def test_reset_re_enables_python_logging(self) -> None:
        """Test reset_structured_logging re-enables Python logging."""
        import logging

        # Set up structured logging (which disables Python logging)
        with patch.object(
            StructuredLoggingAdapter, "_get_logger_node_runner"
        ) as mock_runner:
            mock_runner.return_value = Mock()
            setup_structured_logging()

            # Python logging should now be disabled
            assert not logging.getLogger().isEnabledFor(logging.CRITICAL)

            # Reset structured logging
            reset_structured_logging()

            # Python logging should be re-enabled
            assert logging.getLogger().isEnabledFor(logging.CRITICAL)


class TestIntegrationWithLoggerNode:
    """Integration tests with the Logger Node."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        reset_structured_logging()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        reset_structured_logging()

    @patch("omnibase.nodes.logger_node.v1_0_0.node.run_logger_node")
    def test_end_to_end_logging_flow(self, mock_logger_node: Mock) -> None:
        """Test complete logging flow from emit_log_event to Logger Node."""
        # Mock Logger Node response
        mock_logger_node.return_value = Mock()

        # Set up structured logging
        event_bus = InMemoryEventBus()
        setup_structured_logging(event_bus=event_bus)

        # Emit a log event
        emit_log_event(LogLevelEnum.INFO, "Integration test message")

        # Verify Logger Node was called
        assert mock_logger_node.called
