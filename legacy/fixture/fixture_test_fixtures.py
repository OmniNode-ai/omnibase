import os
import tempfile
import logging
from pathlib import Path
import pytest

@pytest.fixture
def temp_py_file() -> Path:
    """Fixture to create a temporary Python file for AST tests."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("""
class A:
    pass
class B(A):
    pass
class C(B):
    pass
""")
        fname = f.name
    yield Path(fname)
    os.remove(fname)

@pytest.fixture
def temp_invalid_py_file() -> Path:
    """Fixture to create a temporary invalid Python file."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("class A: bad syntax here")
        fname = f.name
    yield Path(fname)
    os.remove(fname)

@pytest.fixture
def logger() -> logging.Logger:
    """Fixture for a test logger."""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger 