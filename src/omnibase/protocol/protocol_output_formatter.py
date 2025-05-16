from typing import Protocol

from omnibase.model.model_enum_output_format import OutputFormatEnum
from omnibase.model.model_output_data import OutputDataModel


class ProtocolOutputFormatter(Protocol):
    """
    Protocol for ONEX output formatting components.

    Example:
        class MyFormatter:
            def format(self, data: OutputDataModel, style: OutputFormatEnum = OutputFormatEnum.JSON) -> str:
                ...
    """

    def format(
        self, data: OutputDataModel, style: OutputFormatEnum = OutputFormatEnum.JSON
    ) -> str: ...
