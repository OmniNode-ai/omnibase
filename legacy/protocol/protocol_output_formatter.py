from typing import Protocol, Any
from foundation.model.model_unified_result import UnifiedBatchResultModel

class OutputFormatterProtocol(Protocol):
    """
    Protocol for output formatters used by orchestrators and tools.
    Enforces DI and testability for all output formatting logic.
    """
    def format_output(self, result: Any, format_type: str = "text") -> UnifiedBatchResultModel:
        ... 