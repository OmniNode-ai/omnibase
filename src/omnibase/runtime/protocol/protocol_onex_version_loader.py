from typing import Protocol

from omnibase.model.model_onex_version import OnexVersionInfo


class ProtocolOnexVersionLoader(Protocol):
    """
    Protocol for loading ONEX version information from .onexversion files.
    """

    def get_onex_versions(self) -> OnexVersionInfo: ...
