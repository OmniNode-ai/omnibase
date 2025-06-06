import os
import sys

TRACE_MODE = os.environ.get("ONEX_TRACE") == "1"
_trace_mode_flag = None


def is_trace_mode():
    """
    Returns True if trace/debug mode is enabled via ONEX_TRACE env or --debug-trace CLI flag.
    Uses a global cache for efficiency.
    """
    global _trace_mode_flag
    if _trace_mode_flag is not None:
        return _trace_mode_flag
    _trace_mode_flag = TRACE_MODE or ("--debug-trace" in sys.argv)
    return _trace_mode_flag
