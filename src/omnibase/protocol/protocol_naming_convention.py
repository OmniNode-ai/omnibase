from typing import Protocol
from omnibase.model.model_naming_convention import NamingConventionResultModel

class ProtocolNamingConvention(Protocol):
    """
    Protocol for ONEX naming convention enforcement.

    Example:
        class MyNamingConvention:
            def validate_name(self, name: str) -> NamingConventionResultModel:
                ...
    """
    def validate_name(self, name: str) -> NamingConventionResultModel:
        ... 