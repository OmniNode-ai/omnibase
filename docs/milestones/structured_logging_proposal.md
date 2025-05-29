<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode Team
created_at: '2025-05-28T12:40:26.583876'
description: Stamped by ONEX
entrypoint: python://structured_logging_proposal.md
hash: e43bbbf08fbf31b41be9892208ac467f854739d7bfc14f08b3dbe690a991d08b
last_modified_at: '2025-05-29T11:50:15.051246+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: structured_logging_proposal.md
namespace: omnibase.structured_logging_proposal
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: d93bbf58-51b7-43da-b8d7-11b5763ddffd
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# Structured Logging Infrastructure Proposal

> **Status:** Proposal  
> **Milestone:** M1 - Structured Logging & Centralized Config  
> **Author:** ONEX Team  
> **Date:** 2025-05-26  

## Executive Summary

This proposal outlines the implementation of structured logging infrastructure that routes all internal ONEX logging through the Logger Node as side effects, following the functional monadic architecture principles. The solution bridges existing Python `logging` calls and `print()` statements to the ONEX event system while maintaining backward compatibility and providing centralized configuration.

## Current State Analysis

### Logging Patterns Found in Codebase

1. **Print Statements (35+ instances)**
   - CLI output and user feedback
   - Debug information in development tools
   - Status messages in scripts and demos
   - Examples: `scripts/lint_error_codes.py`, `examples/telemetry_demo.py`, CLI commands

2. **Python Logging Module (35+ files)**
   - Internal debugging and error reporting
   - Configuration in `conftest.py`, CLI tools, node implementations
   - Examples: `src/omnibase/nodes/*/node.py`, runtime components, core modules

3. **Event System (Already Implemented)**
   - `ProtocolEventBus` with `InMemoryEventBus` implementation
   - `OnexEvent` schema with telemetry event types
   - Logger Node that processes `LoggerInputState` objects

### The Gap

Current logging infrastructure doesn't route through the Logger Node. The functional architecture treats **logs as side effects** that should be captured and managed by the Logger Node, but existing code bypasses this system.

## Architectural Solution

### Core Principle: Logs as Side Effects

Following the functional monadic architecture, we completely replace all print() statements and Python logging with structured events that route through the Logger Node:

```python
# Current (bypasses Logger Node)
logging.info("Processing file: %s", filename)
print("✅ Operation completed")

# Clean Replacement (routes through Logger Node as side effect)
emit_log_event(LogLevel.INFO, "Processing file", {"filename": filename})
emit_log_event(LogLevel.INFO, "✅ Operation completed")
```

**No Backward Compatibility Needed**: The Logger Node handles all output formatting, so we can cleanly replace all logging patterns without maintaining compatibility layers.

### Architecture Components

#### 1. Structured Logging Utilities

```python
def emit_log_event(
    level: LogLevel,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    node_id: Optional[str] = None
) -> None:
    """Emit a structured log event that will be processed by Logger Node."""
    event_bus = get_global_event_bus()
    
    event = OnexEvent(
        event_type=OnexEventTypeEnum.STRUCTURED_LOG,
        node_id=node_id or _get_calling_module(),
        correlation_id=correlation_id,
        metadata={
            "log_level": level.value,
            "message": message,
            "context": context or {},
            "timestamp": time.time(),
            "module": _get_calling_module(),
            "function": _get_calling_function(),
            "line": _get_calling_line()
        }
    )
    
    event_bus.publish(event)

def structured_print(message: str, level: LogLevel = LogLevel.INFO, **context) -> None:
    """Replacement for print() that routes through Logger Node."""
    emit_log_event(level, message, context)
```

#### 2. Logger Node Integration

```python
class StructuredLoggingAdapter:
    """Subscribes to log events and routes them through Logger Node."""
    
    def __init__(self, event_bus: ProtocolEventBus, logger_node_runner: Callable):
        self.event_bus = event_bus
        self.logger_node_runner = logger_node_runner
        self.event_bus.subscribe(self._handle_log_event)
    
    def _handle_log_event(self, event: OnexEvent) -> None:
        """Process log events through Logger Node."""
        if event.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            # Convert event to LoggerInputState
            input_state = LoggerInputState(
                version="1.0.0",
                log_level=LogLevel(event.metadata["log_level"]),
                message=event.metadata["message"],
                context=event.metadata.get("context", {}),
                correlation_id=event.correlation_id
            )
            
            # Process through Logger Node
            self.logger_node_runner(input_state)
```

#### 3. Logger Node Output Formatting

```python
@dataclass
class LoggerOutputConfig:
    """Configuration for Logger Node output formatting."""
    
    # Output format based on context
    format: OutputFormat = OutputFormat.HUMAN_READABLE  # CLI context
    # format: OutputFormat = OutputFormat.JSON  # Production context
    # format: OutputFormat = OutputFormat.VERBOSE  # Development context
    
    targets: List[str] = field(default_factory=lambda: ["stdout"])
    include_correlation_ids: bool = True
    include_context: bool = True
    
    def format_log_message(self, event: OnexEvent) -> str:
        """Format log message based on configuration."""
        if self.format == OutputFormat.HUMAN_READABLE:
            return event.metadata["message"]  # Simple CLI output
        elif self.format == OutputFormat.JSON:
            return json.dumps(event.model_dump())  # Structured output
        elif self.format == OutputFormat.VERBOSE:
            return f"[{event.node_id}] {event.metadata['message']} | {event.metadata.get('context', {})}"
```

#### 4. Centralized Configuration System

```python
@dataclass
class OnexLoggingConfig:
    """Centralized configuration for ONEX logging system."""
    
    # Logger Node configuration
    default_output_format: OutputFormat = OutputFormat.JSON
    log_level: LogLevel = LogLevel.INFO
    enable_correlation_ids: bool = True
    
    # Event bus configuration
    event_bus_type: str = "memory"  # "memory", "redis", "nats", etc.
    
    # Output configuration
    output_targets: List[str] = field(default_factory=lambda: ["stdout"])
    log_file_path: Optional[str] = None
    
    # Environment variable overrides
    @classmethod
    def from_environment(cls) -> 'OnexLoggingConfig':
        """Load configuration with environment variable overrides."""
        return cls(
            default_output_format=OutputFormat(
                os.environ.get("ONEX_LOG_FORMAT", "json")
            ),
            log_level=LogLevel(
                os.environ.get("ONEX_LOG_LEVEL", "info")
            ),
            enable_correlation_ids=os.environ.get(
                "ONEX_ENABLE_CORRELATION_IDS", "true"
            ).lower() == "true",
            event_bus_type=os.environ.get("ONEX_EVENT_BUS_TYPE", "memory"),
            output_targets=os.environ.get(
                "ONEX_LOG_TARGETS", "stdout"
            ).split(","),
            log_file_path=os.environ.get("ONEX_LOG_FILE_PATH")
        )

def setup_structured_logging(config: Optional[OnexLoggingConfig] = None) -> None:
    """Initialize the structured logging system."""
    config = config or OnexLoggingConfig.from_environment()
    
    # Create event bus
    event_bus = _create_event_bus(config.event_bus_type)
    
    # Set up Logger Node adapter
    logging_adapter = StructuredLoggingAdapter(event_bus, _get_logger_node_runner(config))
    
    # Store global references for emit_log_event() to use
    _set_global_event_bus(event_bus)
    _set_global_config(config)
    
    # Disable Python logging entirely - everything goes through ONEX
    logging.disable(logging.CRITICAL)

### System Flow Diagram

```
[Application Code]
        ↓
[emit_log_event() - replaces ALL print() and logging calls]
        ↓
[ProtocolEventBus]
        ↓
[StructuredLoggingAdapter]
        ↓
[Logger Node - handles all output formatting]
        ↓
[Output Targets: CLI (human-readable), Production (JSON), Development (verbose)]
```

### Sample Log Event Schema

```json
{
  "event_type": "STRUCTURED_LOG",
  "node_id": "telemetry_demo",
  "correlation_id": "abc123",
  "metadata": {
    "log_level": "INFO",
    "message": "Processing started",
    "context": {
      "filename": "data.json"
    },
    "module": "demo",
    "function": "run",
    "line": 42,
    "timestamp": 1716749012.543
  }
}
```

## Implementation Plan

### Phase 1: Core Infrastructure (1 day)

1. **Create structured logging utilities**
   - `emit_log_event()` function
   - `StructuredLoggingAdapter` class  
   - `OnexLoggingConfig` dataclass
   - Context extraction utilities (`_get_calling_module()`, etc.)

2. **Add new event type**
   - Add `STRUCTURED_LOG` to `OnexEventTypeEnum`
   - Update event schema documentation

3. **Create configuration module**
   - `src/omnibase/core/structured_logging.py`
   - Environment variable support following existing patterns
   - Integration with existing Logger Node

### Phase 2: Logger Node Output Formatting (1 day)

1. **Extend Logger Node**
   - Add output format configuration (human-readable, JSON, verbose)
   - Context-aware formatting based on environment
   - Multiple output target support

2. **Global setup function**
   - `setup_structured_logging()` in core module
   - Integration with existing initialization code
   - Disable Python logging entirely

### Phase 3: Clean Replacement (2 days)

1. **Replace all print() statements**
   - CLI tools and user-facing output
   - Debug information in development tools
   - Status messages in scripts and demos

2. **Replace all logging calls**
   - Core modules and node implementations
   - Error reporting and critical paths
   - Remove Python logging imports

### Phase 4: Testing & Documentation (1 day)

1. **Comprehensive test suite**
   - Unit tests for all components
   - Integration tests with Logger Node
   - Performance impact assessment

2. **Developer documentation**
   - Usage guide for `emit_log_event()`
   - Configuration reference
   - Output format examples

## Migration Strategy

### Immediate Actions

1. **Replace critical print statements**
   ```python
   # Before
   print(f"❌ Found {len(violations)} error code violations:")
   
   # After  
   structured_print(
       f"Found {len(violations)} error code violations",
       level=LogLevel.ERROR,
       violation_count=len(violations)
   )
   ```

2. **Convert logging calls**
   ```python
   # Before
   logging.error(f"Error getting file creation date for {path}: {e}")
   
   # After
   emit_log_event(
       LogLevel.ERROR,
       "Error getting file creation date",
       context={"path": str(path), "error": str(e)}
   )
   ```

### Clean Replacement Benefits

- **Architectural Purity**: All output flows through Logger Node as intended
- **Zero Complexity**: No compatibility layers or handlers to maintain
- **Better Observability**: Even CLI output gets correlation IDs and structured context
- **Single Configuration**: All output formatting controlled by Logger Node
- **Consistent Patterns**: One way to emit logs across entire codebase

## Configuration Examples

### Environment Variables

```bash
# Logger Node configuration
export ONEX_LOG_FORMAT=json
export ONEX_LOG_LEVEL=info
export ONEX_ENABLE_CORRELATION_IDS=true

# Output configuration  
export ONEX_LOG_TARGETS=stdout,file
export ONEX_LOG_FILE_PATH=/var/log/onex/application.log

# Event bus configuration
export ONEX_EVENT_BUS_TYPE=memory
```

### Configuration File (`logging_config.yaml`)

```yaml
# ONEX Structured Logging Configuration
logger_node:
  default_output_format: json
  log_level: info
  enable_correlation_ids: true

event_bus:
  type: memory
  
output:
  targets:
    - stdout
    - file
  file_path: /var/log/onex/application.log
  
# Plugin-specific logging
plugins:
  stamper_node:
    log_level: debug
    output_format: yaml
```

## Benefits

### Architectural Alignment

1. **Functional Purity**: Logging becomes explicit side effect managed by Logger Node
2. **Centralized Processing**: All logs flow through single processing pipeline
3. **Structured Data**: Rich context and correlation IDs for observability
4. **Event-Driven**: Integrates with existing ONEX event system

### Operational Benefits

1. **Unified Format**: Consistent structured output across all components
2. **Correlation Tracking**: Request tracing across node boundaries
3. **Flexible Output**: Multiple formats and targets via Logger Node
4. **Configuration Management**: Centralized config with environment overrides

### Developer Experience

1. **Simple API**: Single `emit_log_event()` function for all logging needs
2. **Context-Aware Output**: Logger Node formats output based on environment (CLI, production, development)
3. **Rich Context**: Structured logging with automatic metadata and correlation IDs
4. **Debugging Support**: Full context and traceability for all log events
5. **Consistent Patterns**: One logging approach across entire ONEX ecosystem

## Success Criteria

### M1 Completion Requirements

- [ ] Core structured logging utilities implemented (`emit_log_event()`, `StructuredLoggingAdapter`)
- [ ] Configuration system with environment variable support
- [ ] Logger Node extended with output formatting capabilities
- [ ] Complete replacement of all print() statements and logging calls
- [ ] Python logging disabled entirely
- [ ] Comprehensive test coverage
- [ ] Developer documentation complete

### Validation Tests

1. **Functional Tests**
   - Python logging calls route through Logger Node
   - Structured events contain proper metadata
   - Configuration overrides work correctly
   - Correlation IDs propagate properly

2. **Integration Tests**
   - End-to-end logging flow from source to output
   - Multiple output formats and targets
   - Performance impact within acceptable limits
   - Backward compatibility maintained

3. **Replacement Tests**
   - All print() statements successfully replaced
   - All logging calls successfully replaced
   - Output formatting works correctly in different contexts

## Risk Mitigation

### Performance Concerns

- **Async Processing**: Event bus handles logging asynchronously
- **Buffering**: Batch log events to reduce overhead
- **Sampling**: Configurable log sampling for high-volume scenarios
- **Fallback**: Direct output if Logger Node unavailable
- **Rate Limiting & Queue Batching**: Introduce batch publishing and throttling for high-volume log emitters.
- **Async Decoupling**: Ensure Logger Node can process logs off the main thread or from a background task queue.

### Implementation Risks

- **Complete Replacement**: All logging patterns changed at once
- **Testing Coverage**: Comprehensive testing required for all output scenarios
- **Performance Impact**: Event bus routing adds minimal latency
- **Configuration Management**: Proper environment-based configuration needed

## Future Enhancements

### M2 Considerations

1. **Remote Logging**: Integration with external log aggregation systems
2. **Log Analytics**: Built-in log analysis and alerting capabilities  
3. **Performance Optimization**: Advanced buffering and batching strategies
4. **Plugin Ecosystem**: Third-party logging plugins and formatters
5. Logger Node Externalization: Allow the Logger Node to run as a dedicated service for scalability.
6. CLI Output Modes: Toggle between structured JSON output and human-readable CLI messages in development tools.

### Advanced Features

1. **Log Sampling**: Intelligent sampling for high-volume scenarios
2. **Log Compression**: Efficient storage and transmission
3. **Real-time Analytics**: Live log analysis and dashboards
4. **Compliance Features**: Audit trails and retention policies
5. Logger Node Externalization: Allow the Logger Node to run as a dedicated service for scalability.
6. CLI Output Modes: Toggle between structured JSON output and human-readable CLI messages in development tools.

---

This proposal provides a comprehensive solution for implementing structured logging infrastructure that aligns with ONEX functional architecture principles while providing practical migration paths and operational benefits.
