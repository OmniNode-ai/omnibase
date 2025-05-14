from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


class BaseLogEntry(ABC):
    """
    Abstract base class for all log entry types in the logging system.
    Enforces required fields and structure for log entries.
    This class is marked as abstract and should be excluded from field validation by validators.
    """

    __meta__ = {"abstract": True}
    uuid: UUID
    timestamp: datetime
    parent_id: Optional[UUID] = None

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize the log entry to a dictionary."""
        pass


class LogTypeTag(str, Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    META = "meta"
    DOCS = "docs"
    TEST = "test"
    PERFORMANCE = "performance"
    SECURITY = "security"
    EXPERIMENT = "experiment"
    ONBOARDING = "onboarding"
    # Add more tags as needed
