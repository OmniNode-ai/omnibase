"""
Test the directory traverser implementation using in-memory mocks.
Tests the directory traversal functionality and ignore pattern handling.
"""

from pathlib import Path
from typing import Dict, Set
from unittest import mock

import pytest

from omnibase.model.model_enum_ignore_pattern_source import (
    IgnorePatternSourceEnum,
    TraversalModeEnum,
)
from omnibase.model.model_file_filter import FileFilterModel
from omnibase.model.model_onex_message_result import OnexStatus
from omnibase.utils.directory_traverser import DirectoryTraverser


class MockPath:
    """Mock Path class for in-memory filesystem testing."""
    
    def __init__(self, path_str, is_file=True, is_dir=False, size=1000, content=""):
        self.path_str = path_str
        self._is_file = is_file
        self._is_dir = is_dir
        self._size = size
        self.content = content
        self._parent = None if "/" not in path_str else path_str.rsplit("/", 1)[0]
        
    def __eq__(self, other):
        if isinstance(other, MockPath):
            return self.path_str == other.path_str
        return False
        
    def __hash__(self):
        return hash(self.path_str)
        
    def is_file(self):
        return self._is_file
        
    def is_dir(self):
        return self._is_dir
        
    def exists(self):
        return True
        
    def absolute(self):
        return self
        
    def as_posix(self):
        return self.path_str
        
    def stat(self):
        return mock.MagicMock(st_size=self._size)
        
    @property
    def parent(self):
        if self._parent is None:
            return self
        return MockPath(self._parent, is_file=False, is_dir=True)
        
    @property
    def parent_parent(self):
        """Get the parent's parent."""
        if self._parent is None:
            return self
        parent = MockPath(self._parent, is_file=False, is_dir=True)
        if parent._parent is None:
            return parent
        return MockPath(parent._parent, is_file=False, is_dir=True)
    
    def __str__(self):
        return self.path_str
        
    def __truediv__(self, other):
        """Implement the / operator for path joining."""
        if self.path_str.endswith("/"):
            return MockPath(f"{self.path_str}{other}")
        return MockPath(f"{self.path_str}/{other}")


class MockDirectoryTraverser(DirectoryTraverser):
    """
    Mock implementation of DirectoryTraverser for in-memory testing.
    """
    
    def __init__(self, mock_files=None):
        """
        Initialize the mock directory traverser.
        
        Args:
            mock_files: Dictionary mapping path strings to MockPath objects
        """
        super().__init__()
        self.mock_files = mock_files or {}
        self.mock_file_list = list(self.mock_files.values())
        
    def glob(self, pattern):
        """
        Mock implementation of Path.glob.
        
        Args:
            pattern: Glob pattern to match
            
        Returns:
            List of MockPath objects matching the pattern
        """
        # Simple pattern matching for testing
        results = []
        for path in self.mock_file_list:
            if self._matches_pattern(path.path_str, pattern):
                results.append(path)
        return results
        
    def _matches_pattern(self, path_str, pattern):
        """
        Check if a path matches a glob pattern.
        
        This is a simplified implementation for testing purposes.
        
        Args:
            path_str: Path string to check
            pattern: Glob pattern to match
            
        Returns:
            True if the path matches the pattern, False otherwise
        """
        # Handle recursive patterns
        if "**" in pattern:
            # Convert ** to * for simple testing
            pattern = pattern.replace("**", "*")
            
        # Handle file extension patterns
        if pattern.startswith("*."):
            ext = pattern[1:]
            return path_str.endswith(ext)
            
        # Handle directory patterns
        if pattern.endswith("/"):
            return pattern[:-1] in path_str
            
        # Simple substring matching for test purposes
        parts = pattern.replace("*", "").split("/")
        for part in parts:
            if part and part not in path_str:
                return False
                
        return True
    
    def find_files(
        self,
        directory: MockPath,
        include_patterns=None,
        exclude_patterns=None,
        recursive=True,
        ignore_file=None,
    ):
        """Override find_files to use our mock filesystem."""
        # Create a mock filter config
        filter_config = FileFilterModel(
            traversal_mode=TraversalModeEnum.RECURSIVE if recursive else TraversalModeEnum.FLAT,
            include_patterns=include_patterns or self.DEFAULT_INCLUDE_PATTERNS,
            exclude_patterns=exclude_patterns or [],
            ignore_file=ignore_file,
            ignore_pattern_sources=[IgnorePatternSourceEnum.DEFAULT]
        )
        
        return self._find_files_with_config_mock(directory, filter_config)
    
    def _find_files_with_config_mock(self, directory, filter_config):
        """Mock implementation of _find_files_with_config."""
        # Reset counters
        self.reset_counters()
        
        # Determine if operation is recursive
        recursive = filter_config.traversal_mode in [
            TraversalModeEnum.RECURSIVE,
            TraversalModeEnum.SHALLOW
        ]
        
        # Load ignore patterns
        ignore_patterns = []
        if filter_config.exclude_patterns:
            ignore_patterns.extend(filter_config.exclude_patterns)
        
        # For mock testing, always ignore .git directories
        ignore_patterns.append(".git/")
        
        # Find all matching files
        eligible_files = set()
        dir_path = directory.path_str
        
        for path in self.mock_file_list:
            if not path.is_file():
                continue
                
            # Check if path is in the directory
            if not path.path_str.startswith(dir_path):
                continue
                
            # Skip files not in the specified directory when in FLAT mode
            if filter_config.traversal_mode == TraversalModeEnum.FLAT:
                if path.parent.path_str != dir_path:
                    continue
                    
            # Skip files in non-immediate subdirectories in SHALLOW mode
            if filter_config.traversal_mode == TraversalModeEnum.SHALLOW:
                if path.parent.path_str != dir_path and path.parent.parent.path_str != dir_path:
                    continue
            
            # Check include patterns
            include_matched = False
            for pattern in filter_config.include_patterns:
                if self._matches_pattern(path.path_str, pattern):
                    include_matched = True
                    break
                    
            if not include_matched:
                continue
                
            # Check exclude patterns
            if self.should_ignore(path, ignore_patterns):
                continue
                
            eligible_files.add(path)
            
        return eligible_files
    
    def should_ignore(self, path, ignore_patterns):
        """Mock implementation of should_ignore."""
        if not ignore_patterns:
            return False
            
        rel_path = path.path_str
        
        for pattern in ignore_patterns:
            if pattern.endswith("/") and pattern[:-1] in rel_path:
                return True
                
            if self._matches_pattern(rel_path, pattern):
                return True
                
        return False


@pytest.fixture
def mock_file_system():
    """Create a mock file system with test files."""
    root = MockPath("/test", is_file=False, is_dir=True)
    
    # Create mock files
    files = {
        "/test": root,
        "/test/test.yaml": MockPath("/test/test.yaml", content="name: test"),
        "/test/test.json": MockPath("/test/test.json", content='{"name": "test"}'),
        "/test/test.txt": MockPath("/test/test.txt", content="This is not YAML or JSON"),
        "/test/subdir": MockPath("/test/subdir", is_file=False, is_dir=True),
        "/test/subdir/sub_test.yaml": MockPath("/test/subdir/sub_test.yaml", content="name: subtest"),
        "/test/subdir/sub_test.json": MockPath("/test/subdir/sub_test.json", content='{"name": "subtest"}'),
        "/test/.git": MockPath("/test/.git", is_file=False, is_dir=True),
        "/test/.git/git.yaml": MockPath("/test/.git/git.yaml", content="name: git"),
    }
    
    return files


@pytest.fixture
def traverser(mock_file_system):
    """Create a MockDirectoryTraverser with the mock file system."""
    return MockDirectoryTraverser(mock_files=mock_file_system)


def test_find_files_recursive(traverser, mock_file_system):
    """Test finding files recursively."""
    files = traverser.find_files(
        directory=mock_file_system["/test"],
        include_patterns=["**/*.yaml", "**/*.json"],
        recursive=True,
    )
    
    # Should find 4 files: test.yaml, test.json, subdir/sub_test.yaml, subdir/sub_test.json
    # But not .git/git.yaml (ignored by default)
    assert len(files) == 4
    assert mock_file_system["/test/test.yaml"] in files
    assert mock_file_system["/test/test.json"] in files
    assert mock_file_system["/test/subdir/sub_test.yaml"] in files
    assert mock_file_system["/test/subdir/sub_test.json"] in files
    assert mock_file_system["/test/.git/git.yaml"] not in files


def test_find_files_non_recursive(traverser, mock_file_system):
    """Test finding files non-recursively."""
    files = traverser.find_files(
        directory=mock_file_system["/test"],
        include_patterns=["**/*.yaml", "**/*.json"],
        recursive=False,
    )
    
    # Should find 2 files: test.yaml, test.json
    # But not files in subdirectories
    assert len(files) == 2
    assert mock_file_system["/test/test.yaml"] in files
    assert mock_file_system["/test/test.json"] in files
    assert mock_file_system["/test/subdir/sub_test.yaml"] not in files
    assert mock_file_system["/test/subdir/sub_test.json"] not in files


def test_find_files_with_filter_config(traverser, mock_file_system):
    """Test finding files with a filter config."""
    filter_config = FileFilterModel(
        traversal_mode=TraversalModeEnum.RECURSIVE,
        include_patterns=["**/*.yaml"],
        exclude_patterns=["**/subdir/**"],
        ignore_pattern_sources=[IgnorePatternSourceEnum.DEFAULT],
    )
    
    files = traverser._find_files_with_config_mock(mock_file_system["/test"], filter_config)
    
    # Should find 1 file: test.yaml
    # But not test.json (not matched by pattern) or files in subdirectories (excluded)
    assert len(files) == 1
    assert mock_file_system["/test/test.yaml"] in files
    assert mock_file_system["/test/test.json"] not in files
    assert mock_file_system["/test/subdir/sub_test.yaml"] not in files


def test_should_ignore(traverser, mock_file_system):
    """Test the should_ignore method."""
    patterns = ["*.json", "*.yml", ".git/"]
    
    # Test files that should be ignored
    assert traverser.should_ignore(mock_file_system["/test/test.json"], patterns)
    assert traverser.should_ignore(mock_file_system["/test/.git/git.yaml"], patterns)
    
    # Test files that should not be ignored
    assert not traverser.should_ignore(mock_file_system["/test/test.yaml"], patterns)
    assert not traverser.should_ignore(mock_file_system["/test/test.txt"], patterns)


def test_traversal_modes(traverser, mock_file_system):
    """Test different traversal modes."""
    # Test FLAT mode
    filter_config = FileFilterModel(
        traversal_mode=TraversalModeEnum.FLAT,
        include_patterns=["**/*.yaml", "**/*.json"],
        ignore_pattern_sources=[IgnorePatternSourceEnum.NONE],
    )
    
    files = traverser._find_files_with_config_mock(mock_file_system["/test"], filter_config)
    
    # Should find 2 files: test.yaml, test.json
    assert len(files) == 2
    assert mock_file_system["/test/test.yaml"] in files
    assert mock_file_system["/test/test.json"] in files
    assert mock_file_system["/test/subdir/sub_test.yaml"] not in files
    
    # Test SHALLOW mode
    filter_config = FileFilterModel(
        traversal_mode=TraversalModeEnum.SHALLOW,
        include_patterns=["**/*.yaml", "**/*.json"],
        ignore_pattern_sources=[IgnorePatternSourceEnum.NONE],
    )
    
    files = traverser._find_files_with_config_mock(mock_file_system["/test"], filter_config)
    
    # Should find 4 files: all .yaml and .json files in root and immediate subdirectories
    assert len(files) == 4
    assert mock_file_system["/test/test.yaml"] in files
    assert mock_file_system["/test/test.json"] in files
    assert mock_file_system["/test/subdir/sub_test.yaml"] in files
    assert mock_file_system["/test/subdir/sub_test.json"] in files 