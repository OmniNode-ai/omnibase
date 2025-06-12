# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-06-12T10:30:00.000000'
# description: Smart log formatter with context-aware formatting levels
# entrypoint: python://tool_smart_log_formatter
# hash: auto-generated
# last_modified_at: '2025-06-12T10:30:00.000000'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: tool_smart_log_formatter.py
# namespace: python://omnibase.nodes.node_logger.v1_0_0.tools.tool_smart_log_formatter
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: auto-generated
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
Smart Log Formatter for ONEX Structured Logging.

Implements the 4-level smart formatting system:
- MINIMAL: Essential info only (TRACE/DEBUG default)
- READABLE: Human-friendly business events (INFO/WARN default)  
- DETAILED: Multi-line structured for errors (ERROR default)
- STRUCTURED: Full JSON for machine processing (on-demand)

Features:
- Context-aware format selection based on environment
- Anti-pattern prevention (no JSON clutter)
- Complex object summarization
- Runtime format switching capabilities
- Environment variable configuration
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from omnibase.enums import LogLevelEnum
from omnibase.model.model_log_entry import LogContextModel

from ..models.logger_output_config import LoggerOutputConfig


class SmartLogFormatEnum:
    """Smart formatting levels for structured logging."""
    MINIMAL = "minimal"
    READABLE = "readable" 
    DETAILED = "detailed"
    STRUCTURED = "structured"  # JSON


class ToolSmartLogFormatter:
    """
    Smart log formatter implementing context-aware formatting with 4 levels.
    
    Prevents JSON clutter by defaulting to human-readable formats while
    preserving structured data capabilities when explicitly needed.
    """

    def __init__(self, config: Optional[LoggerOutputConfig] = None):
        """
        Initialize the smart formatter.
        
        Args:
            config: Logger output configuration
        """
        self.config = config or LoggerOutputConfig()
        
    def format_log_event(
        self,
        level: LogLevelEnum,
        event_type: str,
        message: str,
        context: Optional[LogContextModel] = None,
        data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> str:
        """
        Format a log event using smart context-aware formatting.
        
        Args:
            level: Log level
            event_type: Type of log event
            message: Primary log message
            context: Log context model
            data: Additional structured data
            correlation_id: Correlation ID for tracing
            
        Returns:
            Formatted log string
        """
        # Determine effective format based on context
        format_type = self._get_effective_format(level, event_type, data or {})
        
        # Prepare data for formatting
        log_data = self._prepare_log_data(
            level, event_type, message, context, data, correlation_id
        )
        
        # Apply appropriate formatting
        if format_type == SmartLogFormatEnum.MINIMAL:
            return self._format_minimal(level, event_type, log_data)
        elif format_type == SmartLogFormatEnum.READABLE:
            return self._format_readable(level, event_type, log_data)
        elif format_type == SmartLogFormatEnum.DETAILED:
            return self._format_detailed(level, event_type, log_data)
        elif format_type == SmartLogFormatEnum.STRUCTURED:
            return self._format_structured(level, event_type, log_data)
        else:
            # Fallback to readable
            return self._format_readable(level, event_type, log_data)

    def _get_effective_format(
        self, level: LogLevelEnum, event_type: str, data: Dict[str, Any]
    ) -> str:
        """
        Determine the best format based on context and environment.
        
        Args:
            level: Log level
            event_type: Event type
            data: Log data
            
        Returns:
            Format type to use
        """
        # Check for CI/automated context
        if os.getenv("CI") or os.getenv("AUTOMATED_TESTING"):
            return SmartLogFormatEnum.STRUCTURED
        
        # Check for production context
        if os.getenv("ENVIRONMENT") == "production":
            return os.getenv("ONEX_LOG_FORMAT_PRODUCTION", SmartLogFormatEnum.STRUCTURED)
        
        # Check for debugging specific correlation ID
        debug_correlations = os.getenv("ONEX_DEBUG_CORRELATIONS", "").split(",")
        if data.get("correlation_id") in debug_correlations:
            return SmartLogFormatEnum.DETAILED
        
        # Check per-level override
        level_format = os.getenv(f"ONEX_LOG_FORMAT_{level.name}", None)
        if level_format:
            return level_format
        
        # Check global format override
        global_format = os.getenv("ONEX_LOG_FORMAT", None)
        if global_format:
            return global_format
        
        # Use level-based defaults
        if level in (LogLevelEnum.TRACE, LogLevelEnum.DEBUG):
            return SmartLogFormatEnum.MINIMAL
        elif level in (LogLevelEnum.INFO, LogLevelEnum.WARNING):
            return SmartLogFormatEnum.READABLE
        elif level in (LogLevelEnum.ERROR, LogLevelEnum.CRITICAL):
            return SmartLogFormatEnum.DETAILED
        else:
            return SmartLogFormatEnum.READABLE

    def _prepare_log_data(
        self,
        level: LogLevelEnum,
        event_type: str,
        message: str,
        context: Optional[LogContextModel],
        data: Optional[Dict[str, Any]],
        correlation_id: Optional[str],
    ) -> Dict[str, Any]:
        """
        Prepare structured data for formatting.
        
        Args:
            level: Log level
            event_type: Event type
            message: Log message
            context: Log context
            data: Additional data
            correlation_id: Correlation ID
            
        Returns:
            Prepared log data dictionary
        """
        log_data = {
            "level": level.name,
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id or "no-id",
        }
        
        # Add context data if available
        if context:
            log_data.update({
                "function": context.calling_function,
                "module": context.calling_module,
                "line": context.calling_line,
                "node_id": context.node_id,
            })
        
        # Add additional data
        if data:
            log_data.update(data)
        
        return log_data

    def _format_minimal(
        self, level: LogLevelEnum, event_type: str, data: Dict[str, Any]
    ) -> str:
        """
        Minimal format for high-volume logs (TRACE/DEBUG default).
        
        Format: [LEVEL] → function() [correlation_id]
        """
        correlation_id = data.get("correlation_id", "no-id")
        
        if event_type == "function_entry":
            function = data.get("function", "unknown")
            return f"[{level.name}] → {function}() [{correlation_id}]"
        elif event_type == "function_exit":
            function = data.get("function", "unknown")
            duration = data.get("execution_time_ms", 0)
            success = "success" if data.get("success", True) else "failed"
            return f"[{level.name}] ← {function}() {duration}ms {success} [{correlation_id}]"
        elif event_type == "function_exception":
            function = data.get("function", "unknown")
            exception_type = data.get("exception_type", "Exception")
            return f"[{level.name}] ✗ {function}() {exception_type} [{correlation_id}]"
        else:
            # Generic minimal format
            return f"[{level.name}] {event_type} [{correlation_id}]"

    def _format_readable(
        self, level: LogLevelEnum, event_type: str, data: Dict[str, Any]
    ) -> str:
        """
        Human-friendly format for business events (INFO/WARN default).
        
        Format: [LEVEL] Business event description [correlation_id]
        """
        correlation_id = data.get("correlation_id", "no-id")
        
        if event_type == "node_execution_start":
            node_type = data.get("node_type", "unknown")
            execution_mode = data.get("execution_mode", "unknown")
            return f"[{level.name}] Node execution started: {node_type} ({execution_mode} mode) [{correlation_id}]"
        
        elif event_type == "node_execution_complete":
            node_type = data.get("node_type", "unknown")
            execution_time = data.get("execution_time_ms", 0) / 1000
            success = data.get("success", True)
            status = "completed" if success else "failed"
            return f"[{level.name}] Node execution {status}: {node_type} ({execution_time:.1f}s) [{correlation_id}]"
        
        elif event_type == "scenario_execution_complete":
            scenario_id = data.get("scenario_id", "unknown")
            steps_completed = data.get("steps_completed", 0)
            steps_failed = data.get("steps_failed", 0)
            execution_time = data.get("execution_time_ms", 0) / 1000
            return f"[{level.name}] Scenario complete: {scenario_id} ({steps_completed} steps, {steps_failed} failed, {execution_time:.1f}s) [{correlation_id}]"
        
        elif event_type == "event_bus_fallback":
            attempted = data.get("attempted_bus", "unknown")
            fallback = data.get("fallback_bus", "unknown")
            error = data.get("error_message", "unknown error")
            return f"[{level.name}] Event bus fallback: {attempted} → {fallback} ({error}) [{correlation_id}]"
        
        elif event_type == "performance_threshold_exceeded":
            operation = data.get("operation_name", "unknown")
            execution_time = data.get("execution_time_ms", 0) / 1000
            threshold = data.get("threshold_ms", 0) / 1000
            return f"[{level.name}] Performance threshold exceeded: {operation} {execution_time:.1f}s > {threshold:.1f}s [{correlation_id}]"
        
        else:
            # Generic readable format
            message = data.get("message", event_type)
            key_info = self._extract_key_fields(data)
            if key_info:
                return f"[{level.name}] {message}: {key_info} [{correlation_id}]"
            else:
                return f"[{level.name}] {message} [{correlation_id}]"

    def _format_detailed(
        self, level: LogLevelEnum, event_type: str, data: Dict[str, Any]
    ) -> str:
        """
        Multi-line detailed format for errors and debugging (ERROR default).
        
        Format: Multi-line structured but human-readable
        """
        correlation_id = data.get("correlation_id", "no-id")
        lines = [f"[{level.name}] {event_type}"]
        
        # Add key fields in structured but readable format
        for key, value in data.items():
            if key not in ["level", "event_type", "timestamp", "correlation_id"]:
                if isinstance(value, (dict, list)):
                    # Avoid JSON clutter - summarize complex objects
                    lines.append(f"        {key.title()}: {self._summarize_complex_value(value)}")
                else:
                    lines.append(f"        {key.title()}: {value}")
        
        lines.append(f"        Correlation: {correlation_id}")
        return "\n".join(lines)

    def _format_structured(
        self, level: LogLevelEnum, event_type: str, data: Dict[str, Any]
    ) -> str:
        """
        Full JSON format for machine processing (on-demand only).
        
        Format: Complete JSON with all structured data
        """
        return json.dumps(data, default=str, separators=(',', ':'))

    def _extract_key_fields(self, data: Dict[str, Any]) -> str:
        """
        Extract key fields for readable format display.
        
        Args:
            data: Log data dictionary
            
        Returns:
            String representation of key fields
        """
        key_fields = []
        
        # Common key fields to display
        priority_fields = [
            "node_type", "execution_mode", "scenario_id", "operation_name",
            "tool_name", "error_type", "status", "count", "duration_ms"
        ]
        
        for field in priority_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if field == "duration_ms":
                    # Convert to seconds for readability
                    value = f"{value/1000:.1f}s"
                key_fields.append(f"{field}={value}")
        
        return ", ".join(key_fields)

    def _summarize_complex_value(self, value: Union[Dict, List]) -> str:
        """
        Summarize complex values to avoid JSON clutter.
        
        Args:
            value: Complex value to summarize
            
        Returns:
            Human-readable summary
        """
        if isinstance(value, dict):
            if len(value) <= 3:
                return str(value)
            else:
                keys = list(value.keys())[:3]
                items = [f"{k}: {value[k]}" for k in keys]
                return f"{{{', '.join(items)}, ...}} ({len(value)} items)"
        elif isinstance(value, list):
            if len(value) <= 3:
                return str(value)
            else:
                items = [str(v) for v in value[:3]]
                return f"[{', '.join(items)}, ...] ({len(value)} items)"
        else:
            return str(value)


def set_temporary_log_format(format_type: str, duration_seconds: int = 300) -> None:
    """
    Temporarily change log format for debugging.
    
    Args:
        format_type: Format to use (minimal, readable, detailed, structured)
        duration_seconds: How long to use this format
    """
    import threading
    
    original_format = os.environ.get("ONEX_LOG_FORMAT", "readable")
    os.environ["ONEX_LOG_FORMAT"] = format_type
    
    def restore_format():
        os.environ["ONEX_LOG_FORMAT"] = original_format
    
    threading.Timer(duration_seconds, restore_format).start()


def enable_debug_correlation(correlation_id: str, duration_seconds: int = 600) -> None:
    """
    Enable detailed logging for specific correlation ID.
    
    Args:
        correlation_id: Correlation ID to debug
        duration_seconds: How long to enable debug logging
    """
    import threading
    
    debug_correlations = os.environ.get("ONEX_DEBUG_CORRELATIONS", "").split(",")
    debug_correlations.append(correlation_id)
    os.environ["ONEX_DEBUG_CORRELATIONS"] = ",".join(filter(None, debug_correlations))
    
    def remove_debug_correlation():
        current = os.environ.get("ONEX_DEBUG_CORRELATIONS", "").split(",")
        updated = [c for c in current if c != correlation_id]
        os.environ["ONEX_DEBUG_CORRELATIONS"] = ",".join(updated)
    
    threading.Timer(duration_seconds, remove_debug_correlation).start()


def create_smart_formatter(
    config: Optional[LoggerOutputConfig] = None,
) -> ToolSmartLogFormatter:
    """
    Factory function to create a smart log formatter.
    
    Args:
        config: Optional logger output configuration
        
    Returns:
        Configured smart log formatter
    """
    return ToolSmartLogFormatter(config) 