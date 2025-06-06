import inspect
import json
from datetime import datetime

from omnibase.enums.log_level import LogLevelEnum
from omnibase.model.model_log_entry import LogContextModel, LogMarkdownRowModel
from omnibase.model.model_node_metadata import LogFormat

try:
    from omnibase.utils.json_encoder import OmniJSONEncoder
except ImportError:
    # Fallback for dev: define a minimal OmniJSONEncoder here
    import datetime
    import json
    import uuid

    class OmniJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, uuid.UUID):
                return str(obj)
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            return super().default(obj)


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
        **extra,
    )


_markdown_header_printed = False
_markdown_col_widths = [
    5,
    7,
    8,
    4,
    9,
]  # initial: Level, Message, Function, Line, Timestamp
_markdown_col_names = ["Level", "Message", "Function", "Line", "Timestamp"]
_markdown_max_message_width = 100


def _truncate(s, width):
    s = str(s)
    return s if len(s) <= width else s[: width - 1] + "…"


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


def _extract_log_summary(msg):
    """
    Extract a concise summary string from a dict or JSON string for log output.
    """
    if isinstance(msg, dict):
        if "status" in msg and "message" in msg:
            return f"Status: {msg['status']} | {msg['message']}"
        if "model" in msg:
            return f"Model: {msg['model']}"
        if "version" in msg:
            return f"Version: {msg['version']}"
        for k, v in msg.items():
            return f"{k}: {v}"
        return str(msg)
    if isinstance(msg, str):
        s = msg.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                import json

                obj = json.loads(s)
                return _extract_log_summary(obj)
            except Exception:
                return s[:100] + ("…" if len(s) > 100 else "")
        return s[:100] + ("…" if len(s) > 100 else "")
    return str(msg)


def log_level_emoji(level):
    # Use the enum value for mapping if available, else fallback to str(level)
    if not isinstance(level, LogLevelEnum):
        try:
            level = LogLevelEnum(level)
        except Exception:
            return str(level)
    mapping = {
        LogLevelEnum.INFO: "ℹ️",
        LogLevelEnum.WARNING: "⚠️",
        LogLevelEnum.ERROR: "❌",
        LogLevelEnum.TRACE: "🔍",
        LogLevelEnum.DEBUG: "🛠️",
        LogLevelEnum.SUCCESS: "✅",
        LogLevelEnum.SKIPPED: "⏭️",
        LogLevelEnum.FIXED: "🛠️",
        LogLevelEnum.PARTIAL: "🟠",
        LogLevelEnum.UNKNOWN: "❓",
        LogLevelEnum.CRITICAL: "🛑",
    }
    return mapping.get(level, str(level))


def emit_log_event_sync(level: LogLevelEnum, message, context):
    import csv
    import io
    import json

    import yaml

    fmt = get_log_format() if "get_log_format" in globals() else LogFormat.JSON
    if isinstance(fmt, str):
        try:
            fmt = LogFormat(fmt.lower())
        except Exception:
            fmt = LogFormat.JSON
    if not isinstance(level, LogLevelEnum):
        try:
            level = LogLevelEnum(level)
        except Exception:
            level = LogLevelEnum.INFO
    log_event = {
        "level": level.value if hasattr(level, "value") else str(level),
        "message": message,
        "context": (
            context.model_dump() if hasattr(context, "model_dump") else dict(context)
        ),
    }
    if fmt == LogFormat.JSON:
        print(json.dumps(log_event, indent=2, cls=OmniJSONEncoder))
    elif fmt == LogFormat.TEXT:
        print(
            f"[{log_event['level'].upper()}] {log_event['message']}\nContext: {log_event['context']}"
        )
    elif fmt == LogFormat.KEY_VALUE:
        kv = " ".join(f"{k}={v}" for k, v in log_event.items())
        print(kv)
    elif fmt == LogFormat.MARKDOWN:
        emoji = log_level_emoji(level)
        func = context.calling_function
        line = context.calling_line
        timestamp = (
            context.timestamp.split(".")[0]
            if "." in context.timestamp
            else context.timestamp
        )
        log_level_str = (
            level.value.upper() if hasattr(level, "value") else str(level).upper()
        )
        # Only print full JSON for DEBUG/TRACE, else print summary
        if level in (LogLevelEnum.DEBUG, LogLevelEnum.TRACE):
            if isinstance(message, dict) or (
                isinstance(message, str)
                and (message.strip().startswith("{") or message.strip().startswith("["))
            ):
                try:
                    msg_obj = (
                        message if isinstance(message, dict) else json.loads(message)
                    )
                    msg_str = f"\n```json\n{json.dumps(msg_obj, indent=2)}\n```"
                except Exception:
                    msg_str = str(message)
            else:
                msg_str = str(message)
        else:
            msg_str = _extract_log_summary(message)
        print(f"{timestamp} {emoji} {log_level_str} {msg_str} | {func}:{line}")
    elif fmt == LogFormat.YAML:
        print(yaml.dump(log_event, sort_keys=False))
    elif fmt == LogFormat.CSV:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=log_event.keys())
        writer.writeheader()
        writer.writerow(log_event)
        print(output.getvalue().strip())
    else:
        print(json.dumps(log_event, indent=2, cls=OmniJSONEncoder))
