from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable
from pathlib import Path

@dataclass
class NamingViolation:
    """Represents a single naming convention violation."""
    file_path: str
    current_name: str
    suggested_name: Optional[str] = None
    violation_type: str = ""
    line_number: Optional[int] = None
    context: Optional[dict] = None

@runtime_checkable
class NamingConventionCheck(Protocol):
    """Protocol defining the interface for individual naming convention checks."""
    
    @property
    def check_name(self) -> str:
        """The unique identifier for this check."""
        ...
    
    @property
    def description(self) -> str:
        """Human-readable description of what this check validates."""
        ...
    
    def validate(self, path: Path, content: Optional[str] = None) -> Optional[NamingViolation]:
        """Validate the given path against this naming convention.
        
        Args:
            path: The path to validate
            content: Optional file content for checks that need to analyze file contents
            
        Returns:
            NamingViolation if a violation is found, None otherwise
        """
        ...

class NamingConventionValidator(ABC):
    """Abstract base class for naming convention validators."""
    
    @abstractmethod
    def register_check(self, check: NamingConventionCheck) -> None:
        """Register a new naming convention check."""
        ...
    
    @abstractmethod
    def validate_path(self, path: Path) -> list[NamingViolation]:
        """Validate a single path against all registered checks."""
        ...
    
    @abstractmethod
    def validate_directory(self, directory: Path) -> list[NamingViolation]:
        """Validate an entire directory recursively against all registered checks."""
        ...
    
    @abstractmethod
    def generate_report(self, violations: list[NamingViolation]) -> str:
        """Generate a human-readable report of violations."""
        ... 