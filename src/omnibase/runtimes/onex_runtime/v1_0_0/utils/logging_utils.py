from omnibase.model.model_log_entry import LogContextModel
from omnibase.model.model_log_entry import LogMarkdownRowModel
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
    global _markdown_header_printed, _markdown_log_buffer
    fmt = get_log_format() if 'get_log_format' in globals() else 'json'
    log_event = {
        "level": level.value if hasattr(level, 'value') else str(level),
        "message": message,
        "context": context.model_dump() if hasattr(context, 'model_dump') else dict(context),
    }
    if fmt == "json":
        print(json.dumps(log_event, indent=2))
    elif fmt == "text":
        print(f"[{log_event['level'].upper()}] {log_event['message']}\nContext: {log_event['context']}")
    elif fmt == "key-value":
        kv = ' '.join(f"{k}={v}" for k, v in log_event.items())
        print(kv)
    elif fmt == "markdown":
        row_model = LogMarkdownRowModel(
            level_emoji=log_level_emoji(log_event['level']),
            message=str(log_event['message']),
            function=str(log_event['context'].get('calling_function','')),
            line=int(log_event['context'].get('calling_line',0)),
            timestamp=str(log_event['context'].get('timestamp','')),
        )
        _markdown_log_buffer.append(row_model)
    elif fmt == "yaml":
        print(yaml.dump(log_event, sort_keys=False))
    elif fmt == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=log_event.keys())
        writer.writeheader()
        writer.writerow(log_event)
        print(output.getvalue().strip())
    else:
        print(json.dumps(log_event, indent=2))

def log_level_emoji(level):
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
    return mapping.get(str(level).lower(), str(level))

def _flush_markdown_log_buffer():
    global _markdown_log_buffer
    if not _markdown_log_buffer:
        return
    # Prepare header as a LogMarkdownRowModel
    header_row = LogMarkdownRowModel(
        level_emoji="Level",
        message="Message",
        function="Function",
        line="Line",
        timestamp="Timestamp",
    )
    all_rows = [header_row] + _markdown_log_buffer
    # Compute max width for each column
    col_names = ["level_emoji", "message", "function", "line", "timestamp"]
    col_widths = []
    for col in col_names:
        max_len = max(len(str(getattr(row, col))) for row in all_rows)
        # For message, cap at _markdown_max_message_width
        if col == "message":
            max_len = min(max_len, _markdown_max_message_width)
        col_widths.append(max_len)
    # Row formatter
    def format_row(row):
        vals = []
        for i, col in enumerate(col_names):
            val = str(getattr(row, col))
            width = col_widths[i]
            if col == "message":
                val = _truncate(val, width)
            vals.append(val.ljust(width))
        return "| " + " | ".join(vals) + " |"
    # Print header row
    print(format_row(header_row))
    # Separator row as a LogMarkdownRowModel
    sep_row = LogMarkdownRowModel(
        level_emoji='-' * col_widths[0],
        message='-' * col_widths[1],
        function='-' * col_widths[2],
        line='-' * col_widths[3],
        timestamp='-' * col_widths[4],
    )
    print(format_row(sep_row))
    # Data rows
    for row in _markdown_log_buffer:
        print(format_row(row))
    _markdown_log_buffer.clear()

def flush_markdown_log_buffer():
    _flush_markdown_log_buffer() 