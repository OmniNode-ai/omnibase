"""Protocol stubs for type checking."""
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from pathlib import Path

@runtime_checkable
class ProtocolValidateMetadataBlock(Protocol):
    """Protocol for metadata block validation."""
    def validate(self, target: Path, config: Optional[Dict[str, Any]] = None) -> Any: ...
    def get_name(self) -> str: ...

@runtime_checkable
class ProtocolValidateDispatch(Protocol):
    """Protocol for validator dispatch."""
    def dispatch(self, target: Path, config: Optional[Dict[str, Any]] = None) -> Any: ...

@runtime_checkable
class ProtocolValidateResult(Protocol):
    """Protocol for validation results."""
    def is_valid(self) -> bool: ...
    def get_messages(self) -> List[Any]: ...

@runtime_checkable
class ProtocolValidateFixture(Protocol):
    """Protocol for test fixtures."""
    def setup(self) -> None: ...
    def teardown(self) -> None: ...

@runtime_checkable
class ProtocolValidatorRegistry(Protocol):
    """Protocol for validator registry."""
    def register(self, name: str, validator: Any) -> None: ...
    def get_validator(self, name: str) -> Optional[Any]: ...
    def list_validators(self) -> List[str]: ...

@runtime_checkable
class ProtocolRegistryTestCase(Protocol):
    """Protocol for registry test cases."""
    def setup(self) -> None: ...
    def teardown(self) -> None: ...

@runtime_checkable
class ProtocolCLI(Protocol):
    """Protocol for CLI tools."""
    def main(self, args: List[str]) -> int: ...

@runtime_checkable
class ProtocolCLITool(Protocol):
    """Protocol for CLI tool implementation."""
    def run(self, args: List[str]) -> int: ...

@runtime_checkable
class ProtocolOrchestrator(Protocol):
    """Protocol for orchestrator."""
    def orchestrate(self, target: Path, config: Optional[Dict[str, Any]] = None) -> Any: ...

@runtime_checkable
class ProtocolOutputFormatter(Protocol):
    """Protocol for output formatting."""
    def format(self, result: Any) -> str: ...

@runtime_checkable
class ProtocolProcessRunner(Protocol):
    """Protocol for process running."""
    def run(self, cmd: List[str], **kwargs: Any) -> Any: ...

@runtime_checkable
class ProtocolFileUtils(Protocol):
    """Protocol for file utilities."""
    def read_file(self, path: Path) -> str: ...
    def write_file(self, path: Path, content: str) -> None: ...

@runtime_checkable
class ProtocolYamlUtils(Protocol):
    """Protocol for YAML utilities."""
    def load(self, content: str) -> Any: ...
    def dump(self, data: Any) -> str: ...

@runtime_checkable
class ProtocolLogger(Protocol):
    """Protocol for logging."""
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

@runtime_checkable
class ProtocolLogEntry(Protocol):
    """Protocol for log entries."""
    def get_level(self) -> str: ...
    def get_message(self) -> str: ...

@runtime_checkable
class ProtocolStamper(Protocol):
    """Protocol for stamping."""
    def stamp(self, target: Path, content: str) -> None: ...

@runtime_checkable
class ProtocolStamperIgnore(Protocol):
    """Protocol for stamping ignore."""
    def should_ignore(self, target: Path) -> bool: ...

@runtime_checkable
class ProtocolTestableCLI(Protocol):
    """Protocol for testable CLI."""
    def test(self, args: List[str]) -> Any: ... 