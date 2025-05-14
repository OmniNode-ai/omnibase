from typing import Protocol, Optional, Dict
from foundation.model.model_unified_result import UnifiedResultModel

class ProtocolInMemoryValidate(Protocol):
    def validate_content(self, content: str, config: Optional[Dict] = None) -> UnifiedResultModel:
        """
        Validate the given content (in-memory string) and return a UnifiedResultModel.
        Args:
            content: The content to validate (YAML, JSON, etc.)
            config: Optional configuration dictionary
        Returns:
            UnifiedResultModel: The result of the validation
        """
        ... 