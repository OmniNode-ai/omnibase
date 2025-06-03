from omnibase.model.model_log_entry import LogContextModel
from omnibase.model.model_log_entry import LogMarkdownRowModel
import inspect
from datetime import datetime
import json
from omnibase.enums.log_level import LogLevelEnum
from omnibase.model.model_node_metadata import LogFormat

_log_format = LogFormat.JSON

def set_log_format(fmt):
    global _log_format
    if isinstance(fmt, LogFormat):
        _log_format = fmt
    elif isinstance(fmt, str):
        try:
            _log_format = LogFormat(fmt.lower())
        except ValueError:
            _log_format = LogFormat.JSON
    else:
        _log_format = LogFormat.JSON

def get_log_format():
    global _log_format
    return _log_format

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

_markdown_header_printed = False
_markdown_col_widths = [5, 7, 8, 4, 9]  # initial: Level, Message, Function, Line, Timestamp
_markdown_col_names = ["Level", "Message", "Function", "Line", "Timestamp"]
_markdown_max_message_width = 100
_markdown_log_buffer = []  # Buffer for markdown log rows

def _truncate(s, width):
    s = str(s)
    return s if len(s) <= width else s[:width-1] + "…"

def _update_markdown_col_widths(row):
    global _markdown_col_widths
    for i, val in enumerate(row):
        val_len = len(str(val))
        if i == 1:  # message col
            val_len = min(val_len, _markdown_max_message_width)
        if val_len > _markdown_col_widths[i]:
            _markdown_col_widths[i] = val_len

def _format_markdown_row(row):
    global _markdown_col_widths
    padded = []
    for i, val in enumerate(row):
        width = _markdown_col_widths[i]
        if i == 1:  # message col
            val = _truncate(val, _markdown_max_message_width)
        padded.append(str(val).ljust(width))
    return "| " + " | ".join(padded) + " |"

def emit_log_event_sync(level: LogLevelEnum, message, context):
    import json, yaml, csv, io
    fmt = get_log_format() if 'get_log_format' in globals() else 'json'
    log_event = {
        "level": level.value if hasattr(level, 'value') else str(level),
        "message": message,
        "context": context.model_dump() if hasattr(context, 'model_dump') else dict(context),
    }
    if fmt == LogFormat.JSON:
        print(json.dumps(log_event, indent=2))
    elif fmt == LogFormat.TEXT:
        print(f"[{log_event['level'].upper()}] {log_event['message']}\nContext: {log_event['context']}")
    elif fmt == LogFormat.KEY_VALUE:
        kv = ' '.join(f"{k}={v}" for k, v in log_event.items())
        print(kv)
    elif fmt == LogFormat.MARKDOWN:
        emoji = log_level_emoji(level)
        func = context.calling_function
        line = context.calling_line
        # Remove microseconds from timestamp
        timestamp = context.timestamp.split(".")[0] if "." in context.timestamp else context.timestamp
        log_level_str = (level.value.upper() if hasattr(level, 'value') else str(level).upper())
        print(f"{timestamp} {emoji} {log_level_str} {message} | {func}:{line}")
    elif fmt == LogFormat.YAML:
        print(yaml.dump(log_event, sort_keys=False))
    elif fmt == LogFormat.CSV:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=log_event.keys())
        writer.writeheader()
        writer.writerow(log_event)
        print(output.getvalue().strip())
    else:
        print(json.dumps(log_event, indent=2))

def log_level_emoji(level):
    # Use the enum value for mapping if available, else fallback to str(level)
    key = level.value.lower() if hasattr(level, 'value') else str(level).lower()
    mapping = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "trace": "🔍",
        "debug": "🛠️",
        "success": "✅",
        "skipped": "⏭️",
        "fixed": "🛠️",
        "partial": "🟠",
        "unknown": "❓",
        "critical": "🛑",
    }
    return mapping.get(key, key)

def _flush_markdown_log_buffer():
    pass

def flush_markdown_log_buffer():
    pass 