from pathlib import Path
from typing import Protocol, Optional

from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel


class ProtocolStamper(Protocol):
    """
    Protocol for stamping ONEX node metadata with hashes, signatures, or trace data.

    Example:
        class MyStamper:
            def stamp(self, path: str) -> OnexResultModel:
                ...
    """

    def stamp(self, path: str) -> OnexResultModel:
        """Stamp an ONEX metadata file at the given path."""
        ...

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs: object,
    ) -> OnexResultModel:
        """
        Stamp the file with a metadata block, replacing any existing block.
        :return: OnexResultModel describing the operation result.
        """
        ...
