from omnibase.model.model_log_entry import LogContextModel
import inspect
from datetime import datetime
import json
from omnibase.enums.log_level import LogLevelEnum

def make_log_context(node_id=None, correlation_id=None, **extra):
    """
    Create a standards-compliant LogContextModel with all required fields auto-populated.
    Optionally pass node_id, correlation_id, and any extra fields as kwargs.
    """
    frame = inspect.currentframe().f_back
    return LogContextModel(
        calling_module=frame.f_globals.get("__name__", "<unknown>"),
        calling_function=frame.f_code.co_name,
        calling_line=frame.f_lineno,
        timestamp=datetime.utcnow().isoformat(),
        node_id=node_id,
        correlation_id=correlation_id,
        **extra
    )

def emit_log_event_sync(level: LogLevelEnum, message, context: LogContextModel):
    """
    Emit a log event synchronously. For local/dev, print as JSON to stdout.
    """
    log_event = {
        "level": level.value if hasattr(level, 'value') else str(level),
        "message": message,
        "context": context.model_dump() if hasattr(context, 'model_dump') else dict(context),
    }
    print(json.dumps(log_event, indent=2)) 