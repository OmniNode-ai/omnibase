"""
Comprehensive Regression Tests for Stamper Idempotency and Namespace Issues

This test file addresses the specific bugs found and fixed in the stamper:
1. Namespace generation using "onex.stamped" instead of "omnibase.stamped"
2. Idempotency issues where UUID and created_at were not preserved
3. Cross-handler consistency issues
4. UUID preservation bugs in hash corruption and content change scenarios

Follows ONEX testing standards:
- Markerless, registry-driven, fixture-injected, protocol-first testing
- No unit/integration markers on test functions
- All test cases registered in central registries
- Dependencies injected via pytest fixtures
- Tests public protocol contracts only
"""
import difflib
import itertools
import re
from pathlib import Path
from typing import Any, Dict, List, Protocol
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.enums.metadata import NodeMetadataField
from omnibase.metadata.metadata_constants import (
    METADATA_VERSION,
    SCHEMA_VERSION,
    get_namespace_prefix,
)
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.model_node_metadata import (
    Namespace,
    NodeMetadataBlock,
    strip_volatile_fields_from_dict,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_markdown import (
    MarkdownHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python import PythonHandler
from omnibase.runtimes.onex_runtime.v1_0_0.io.in_memory_file_io import InMemoryFileIO

MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


class IdempotencyTestCase(BaseModel):
    """Model for idempotency test cases."""
    id: str
    file_extension: str
    handler_class: type
    initial_content: str
    description: str


class NamespaceTestCase(BaseModel):
    """Model for namespace validation test cases."""
    id: str
    file_extension: str
    handler_class: type
    filename: str
    initial_content: str
    expected_namespace_pattern: str
    description: str


class UUIDPreservationTestCase(BaseModel):
    """Model for UUID preservation test cases."""
    id: str
    file_extension: str
    handler_class: type
    filename: str
    initial_content: str
    corruption_type: str
    description: str


class ProtocolIdempotencyTestRegistry(Protocol):
    """Protocol for idempotency test case registries."""

    def get_idempotency_cases(self) ->List[IdempotencyTestCase]:
        ...

    def get_namespace_cases(self) ->List[NamespaceTestCase]:
        ...

    def get_uuid_preservation_cases(self) ->List[UUIDPreservationTestCase]:
        ...


class StamperRegressionTestRegistry:
    """
    Canonical registry for stamper regression test cases.

    Covers the specific bugs that were found and fixed:
    - Namespace generation issues
    - Idempotency preservation of UUID and created_at
    - Cross-handler consistency
    - UUID preservation in corruption and content change scenarios
    """

    def get_idempotency_cases(self) ->List[IdempotencyTestCase]:
        """Get test cases for idempotency validation."""
        return [IdempotencyTestCase(id='python_idempotency', file_extension
            ='.py', handler_class=PythonHandler, initial_content=
            """# Simple Python file
print('hello world')
""", description=
            'Test Python file idempotency preservation'),
            IdempotencyTestCase(id='markdown_idempotency', file_extension=
            '.md', handler_class=MarkdownHandler, initial_content=
            """# Test Markdown

Some content here.
""", description=
            'Test Markdown file idempotency preservation'),
            IdempotencyTestCase(id='yaml_idempotency', file_extension=
            '.yaml', handler_class=MetadataYAMLHandler, initial_content=
            """test_key: test_value
other_key: other_value
""", description
            ='Test YAML file idempotency preservation')]

    def get_namespace_cases(self) ->List[NamespaceTestCase]:
        """Get test cases for namespace validation."""
        return [NamespaceTestCase(id='python_namespace', file_extension=
            '.py', handler_class=PythonHandler, filename='test_module.py',
            initial_content="""# Simple Python module
print('hello')
""",
            expected_namespace_pattern='^omnibase\\.test_module$',
            description='Test Python file namespace generation'),
            NamespaceTestCase(id='markdown_namespace', file_extension='.md',
            handler_class=MarkdownHandler, filename='readme.md',
            initial_content="""# Test README

Some documentation here.
""",
            expected_namespace_pattern='^omnibase\\.readme$', description=
            'Test Markdown file namespace generation'), NamespaceTestCase(
            id='yaml_namespace', file_extension='.yaml', handler_class=
            MetadataYAMLHandler, filename='config.yaml', initial_content=
            """test_key: test_value
config_key: config_value
""",
            expected_namespace_pattern='^omnibase\\.config$', description=
            'Test YAML file namespace generation'), NamespaceTestCase(id=
            'complex_filename_namespace', file_extension='.py',
            handler_class=PythonHandler, filename='my-complex_file.name.py',
            initial_content=
            """# Complex filename test
def complex_function():
    return 'complex'
"""
            , expected_namespace_pattern=
            '^omnibase\\.my_complex_file_name$', description=
            'Test complex filename normalization for namespace')]

    def get_uuid_preservation_cases(self) ->List[UUIDPreservationTestCase]:
        """Get test cases for UUID preservation validation."""
        return [UUIDPreservationTestCase(id='python_hash_corruption',
            file_extension='.py', handler_class=PythonHandler, filename=
            'test_hash_corruption.py', initial_content=
            """# Test file for hash corruption
def test_function():
    return 'test'
"""
            , corruption_type='hash_corruption', description=
            'Test UUID preservation when hash is corrupted'),
            UUIDPreservationTestCase(id='python_content_change',
            file_extension='.py', handler_class=PythonHandler, filename=
            'test_content_change.py', initial_content=
            """# Test file for content change
def original_function():
    return 'original'
"""
            , corruption_type='content_change', description=
            'Test UUID preservation when content changes'),
            UUIDPreservationTestCase(id='python_namespace_corruption',
            file_extension='.py', handler_class=PythonHandler, filename=
            'test_namespace_corruption.py', initial_content=
            """# Test file for namespace corruption
def namespace_test():
    return 'namespace'
"""
            , corruption_type='namespace_corruption', description=
            'Test UUID preservation when namespace is corrupted'),
            UUIDPreservationTestCase(id='markdown_hash_corruption',
            file_extension='.md', handler_class=MarkdownHandler, filename=
            'test_hash_corruption.md', initial_content=
            """# Test Markdown

Content for hash corruption test.
""",
            corruption_type='hash_corruption', description=
            'Test UUID preservation in Markdown when hash is corrupted'),
            UUIDPreservationTestCase(id='markdown_content_change',
            file_extension='.md', handler_class=MarkdownHandler, filename=
            'test_content_change.md', initial_content=
            """# Original Title

Original content here.
""",
            corruption_type='content_change', description=
            'Test UUID preservation in Markdown when content changes'),
            UUIDPreservationTestCase(id='yaml_hash_corruption',
            file_extension='.yaml', handler_class=MetadataYAMLHandler,
            filename='test_hash_corruption.yaml', initial_content=
            """original_key: original_value
test_key: test_value
""",
            corruption_type='hash_corruption', description=
            'Test UUID preservation in YAML when hash is corrupted'),
            UUIDPreservationTestCase(id='yaml_content_change',
            file_extension='.yaml', handler_class=MetadataYAMLHandler,
            filename='test_content_change.yaml', initial_content=
            """original_key: original_value
""", corruption_type=
            'content_change', description=
            'Test UUID preservation in YAML when content changes')]


stamper_regression_registry = StamperRegressionTestRegistry()


@pytest.fixture(params=[pytest.param(MOCK_CONTEXT, id='mock', marks=pytest.
    mark.mock), pytest.param(INTEGRATION_CONTEXT, id='integration', marks=
    pytest.mark.integration)])
def file_io(request) ->InMemoryFileIO:
    """
    Canonical file I/O fixture for stamper tests.

    Provides different contexts for CI tiers:
    - Mock context: In-memory file I/O for fast tests
    - Integration context: In-memory file I/O (same for now, could be real file I/O later)
    """
    if request.param == MOCK_CONTEXT:
        return InMemoryFileIO()
    elif request.param == INTEGRATION_CONTEXT:
        return InMemoryFileIO()
    else:
        raise OnexError(f'Unknown file I/O context: {request.param}',
            CoreErrorCode.INVALID_PARAMETER)


@pytest.fixture(params=[pytest.param(MOCK_CONTEXT, id='mock', marks=pytest.
    mark.mock), pytest.param(INTEGRATION_CONTEXT, id='integration', marks=
    pytest.mark.integration)])
def handler_factory(request):
    """
    Factory fixture for creating handlers in different contexts.

    Returns a function that creates handlers with appropriate dependencies.
    """

    def _create_handler(handler_class: type) ->Any:
        if request.param == MOCK_CONTEXT:
            return handler_class()
        elif request.param == INTEGRATION_CONTEXT:
            return handler_class()
        else:
            raise OnexError(f'Unknown handler context: {request.param}',
                CoreErrorCode.INVALID_PARAMETER)
    return _create_handler


@pytest.mark.parametrize('test_case', stamper_regression_registry.
    get_namespace_cases(), ids=lambda case: case.id)
def test_namespace_generation_regression(test_case: NamespaceTestCase,
    handler_factory, file_io: InMemoryFileIO) ->None:
    """
    Test that namespace generation uses correct 'omnibase.stamped' prefix.

    This test addresses the regression where namespaces were generated with
    'onex.stamped' prefix instead of the correct 'omnibase.stamped' prefix.

    Args:
        test_case: Namespace test case from registry
        handler_factory: Handler factory fixture
        file_io: In-memory file I/O fixture
    """
    handler = handler_factory(test_case.handler_class)
    file_path = Path(test_case.filename)
    file_io.write_text(file_path, test_case.initial_content)
    content = file_io.read_text(file_path)
    result = handler.stamp(file_path, content)
    assert result.status == OnexStatus.SUCCESS, f'Stamping failed: {result.messages}'
    stamped_content = result.metadata.get('content', '')
    assert stamped_content, 'No stamped content found in result metadata'
    metadata = extract_metadata_fields(handler, stamped_content, file_path)
    generated_namespace = get_namespace_str(metadata.get('namespace'))
    assert generated_namespace is not None, 'Namespace not found in metadata'
    expected_pattern = (test_case.expected_namespace_pattern or
        f'^{get_namespace_prefix()}\\.[a-zA-Z0-9_\\.]+$')
    assert re.match(expected_pattern, generated_namespace
        ), f"Namespace '{generated_namespace}' should match pattern '{expected_pattern}'"
    assert not generated_namespace.startswith('onex.stamped.'
        ), f"Namespace '{generated_namespace}' should not use old 'onex.stamped.' prefix"
    assert not generated_namespace.startswith('omnibase.stamped.'
        ), f"Namespace '{generated_namespace}' should not use meaningless 'omnibase.stamped.' prefix"


@pytest.mark.parametrize('test_case,overwrite', list(itertools.product(
    stamper_regression_registry.get_idempotency_cases(), [False, True])),
    ids=lambda val: f'{val[0].id}-overwrite_{val[1]}' if isinstance(val,
    tuple) else str(val))
def test_idempotency_preservation_with_overwrite(test_case:
    IdempotencyTestCase, overwrite: bool, handler_factory, file_io:
    InMemoryFileIO) ->None:
    """
    Protocol-first: Asserts sticky field preservation (uuid, created_at) when stamping with and without overwrite.
    Catches regressions where --overwrite does not preserve sticky fields.
    """
    handler = handler_factory(test_case.handler_class)
    file_path = Path(
        f'test_idempotency_overwrite_{test_case.id}{test_case.file_extension}')
    file_io.write_text(file_path, test_case.initial_content)
    content1 = file_io.read_text(file_path)
    result1 = handler.stamp(file_path, content1)
    assert result1.status == OnexStatus.SUCCESS, f'First stamping failed: {result1.messages}'
    stamped_content1 = result1.metadata.get('content', '')
    assert stamped_content1, 'No stamped content found in first result'
    metadata1 = extract_metadata_fields(handler, stamped_content1, file_path)
    emit_log_event_sync(LogLevelEnum.DEBUG,
        f"[IDEMPOTENCY] First stamp: uuid={metadata1.get('uuid')}, created_at={metadata1.get('created_at')}"
        , node_id='test_stamper_idempotency_regression', event_bus=self.
        _event_bus)
    assert metadata1.get('uuid'
        ) is not None, 'UUID not found in initial metadata'
    assert metadata1.get('created_at'
        ) is not None, 'created_at not found in initial metadata'
    result2 = handler.stamp(file_path, stamped_content1, overwrite=overwrite)
    assert result2.status == OnexStatus.SUCCESS, f'Second stamping failed: {result2.messages}'
    stamped_content2 = result2.metadata.get('content', '')
    assert stamped_content2, 'No stamped content found in second result'
    metadata2 = extract_metadata_fields(handler, stamped_content2, file_path)
    emit_log_event_sync(LogLevelEnum.DEBUG,
        f"[IDEMPOTENCY] Second stamp (overwrite={overwrite}): uuid={metadata2.get('uuid')}, created_at={metadata2.get('created_at')}"
        , node_id='test_stamper_idempotency_regression', event_bus=self.
        _event_bus)
    assert_idempotency_fields_preserved(metadata1, metadata2)
    meta1_stripped = strip_volatile_fields_from_dict(metadata1)
    meta2_stripped = strip_volatile_fields_from_dict(metadata2)
    assert meta1_stripped == meta2_stripped, 'Non-volatile metadata fields should be identical for idempotency (overwrite={})'.format(
        overwrite)


@pytest.mark.parametrize('test_case', stamper_regression_registry.
    get_uuid_preservation_cases(), ids=lambda case: case.id)
def test_uuid_preservation_bug_reproduction(test_case:
    UUIDPreservationTestCase, handler_factory, file_io: InMemoryFileIO) ->None:
    """
    Test that reproduces the UUID preservation bug in various corruption scenarios.

    This test specifically reproduces the bug where UUID is not preserved when:
    1. Hash is corrupted (set to placeholder values)
    2. Content changes occur
    3. Namespace is corrupted

    Args:
        test_case: UUID preservation test case from registry
        handler_factory: Handler factory fixture
        file_io: In-memory file I/O fixture
    """
    handler = handler_factory(test_case.handler_class)
    file_path = Path(test_case.filename)
    file_io.write_text(file_path, test_case.initial_content)
    content1 = file_io.read_text(file_path)
    result1 = handler.stamp(file_path, content1)
    assert result1.status == OnexStatus.SUCCESS, f'Initial stamping failed: {result1.messages}'
    stamped_content1 = result1.metadata.get('content', '')
    assert stamped_content1, 'No stamped content found in initial result'
    metadata1 = extract_metadata_fields(handler, stamped_content1, file_path)
    original_uuid = metadata1.get('uuid')
    original_created_at = metadata1.get('created_at')
    original_hash = metadata1.get('hash')
    original_namespace = get_namespace_str(metadata1.get('namespace'))
    emit_log_event_sync(LogLevelEnum.DEBUG,
        f'[UUID] Baseline: uuid={original_uuid}, created_at={original_created_at}, hash={original_hash}, namespace={original_namespace}'
        , node_id='test_stamper_idempotency_regression', event_bus=self.
        _event_bus)
    assert original_uuid is not None, 'UUID not found in baseline metadata'
    assert original_created_at is not None, 'created_at not found in baseline metadata'
    assert original_hash is not None, 'hash not found in baseline metadata'
    assert original_namespace is not None, 'namespace not found in baseline metadata'
    if test_case.corruption_type == 'hash_corruption':
        corrupted_content = stamped_content1.replace(f'hash: {original_hash}',
            f'hash: "{\'0\' * 64}"')
    elif test_case.corruption_type == 'content_change':
        if test_case.file_extension == '.py':
            additional_content = """
# Added comment for content change test
def added_function():
    return 'content_changed'
"""
        elif test_case.file_extension == '.md':
            additional_content = """
## Added Section

New content added for content change test.
"""
        elif test_case.file_extension == '.yaml':
            additional_content = """
# Added for content change test
new_key: new_value
content_changed: true
"""
        else:
            additional_content = (
                '\n# Modified content for content change test\n')
        corrupted_content = stamped_content1 + additional_content
    elif test_case.corruption_type == 'namespace_corruption':
        corrupted_content = stamped_content1.replace(
            f'namespace: {original_namespace}',
            f"namespace: omnibase.wrong.{original_namespace.split('.')[-1]}")
    else:
        corrupted_content = stamped_content1
    result2 = handler.stamp(file_path, corrupted_content)
    assert result2.status == OnexStatus.SUCCESS, f'Corruption fix stamping failed: {result2.messages}'
    stamped_content2 = result2.metadata.get('content', '')
    assert stamped_content2, 'No stamped content found in corruption fix result'
    metadata2 = extract_metadata_fields(handler, stamped_content2, file_path)
    corrected_uuid = metadata2.get('uuid')
    corrected_created_at = metadata2.get('created_at')
    corrected_hash = metadata2.get('hash')
    corrected_namespace = get_namespace_str(metadata2.get('namespace'))
    assert corrected_uuid == original_uuid, f"UUID preservation bug detected! Original UUID '{original_uuid}' was not preserved, got '{corrected_uuid}'"
    assert corrected_created_at == original_created_at, f"created_at should be preserved! Original '{original_created_at}' was not preserved, got '{corrected_created_at}'"
    if test_case.corruption_type == 'hash_corruption':
        assert corrected_hash != '0' * 64, 'Hash should be recalculated from placeholder'
        assert len(corrected_hash) == 64, 'Hash should be 64 characters'
        assert corrected_namespace == original_namespace, 'Namespace should be preserved for hash corruption'
    elif test_case.corruption_type == 'content_change':
        assert corrected_hash != original_hash, 'Hash should change when content changes'
        assert corrected_namespace == original_namespace, 'Namespace should be preserved for content change'
    elif test_case.corruption_type == 'namespace_corruption':
        assert corrected_namespace == original_namespace, 'Namespace should be corrected back to canonical form'
        assert not corrected_namespace.startswith('omnibase.wrong.'
            ), 'Namespace should not use wrong prefix'
        assert corrected_namespace.startswith('omnibase.'
            ), 'Namespace should use correct omnibase prefix'
        assert corrected_hash != original_hash, 'Hash should change when namespace is corrected'
    emit_log_event_sync(LogLevelEnum.DEBUG,
        f'[UUID] After corruption: uuid={corrected_uuid}, created_at={corrected_created_at}, hash={corrected_hash}, namespace={corrected_namespace}'
        , node_id='test_stamper_idempotency_regression', event_bus=self.
        _event_bus)


@pytest.mark.parametrize('test_case', stamper_regression_registry.
    get_idempotency_cases(), ids=lambda case: case.id)
def test_content_change_updates_metadata(test_case: IdempotencyTestCase,
    handler_factory, file_io: InMemoryFileIO) ->None:
    """
    Test that content changes properly update hash and last_modified_at while preserving UUID.

    This test verifies that when content actually changes, the appropriate metadata
    fields are updated while idempotency fields (UUID, created_at) are preserved.

    Args:
        test_case: Idempotency test case from registry
        handler_factory: Handler factory fixture
        file_io: In-memory file I/O fixture
    """
    handler = handler_factory(test_case.handler_class)
    file_path = Path(f'test_content_change{test_case.file_extension}')
    file_io.write_text(file_path, test_case.initial_content)
    content1 = file_io.read_text(file_path)
    result1 = handler.stamp(file_path, content1)
    assert result1.status == OnexStatus.SUCCESS, f'First stamping failed: {result1.messages}'
    stamped_content1 = result1.metadata.get('content', '')
    assert stamped_content1, 'No stamped content found in first result'
    metadata1 = extract_metadata_fields(handler, stamped_content1, file_path)
    emit_log_event_sync(LogLevelEnum.DEBUG,
        f"[CONTENT_CHANGE] First stamp: uuid={metadata1.get('uuid')}, created_at={metadata1.get('created_at')}, hash={metadata1.get('hash')}"
        , node_id='test_stamper_idempotency_regression', event_bus=self.
        _event_bus)
    if test_case.file_extension == '.py':
        additional_content = """
# Added Python comment for hash change test
def new_function():
    return 'modified'
"""
    elif test_case.file_extension == '.md':
        additional_content = """
## New Section Added

This content was added to test hash changes.
"""
    elif test_case.file_extension == '.yaml':
        additional_content = """
# Added for hash change test
added_key: added_value
test_modification: true
"""
    else:
        additional_content = '\n# Modified content for hash change test\n'
    modified_stamped_content = stamped_content1 + additional_content
    result2 = handler.stamp(file_path, modified_stamped_content)
    assert result2.status == OnexStatus.SUCCESS, f'Second stamping failed: {result2.messages}'
    stamped_content2 = result2.metadata.get('content', '')
    assert stamped_content2, 'No stamped content found in second result'
    metadata2 = extract_metadata_fields(handler, stamped_content2, file_path)
    emit_log_event_sync(LogLevelEnum.DEBUG,
        f"[CONTENT_CHANGE] Second stamp: uuid={metadata2.get('uuid')}, created_at={metadata2.get('created_at')}, hash={metadata2.get('hash')}"
        , node_id='test_stamper_idempotency_regression', event_bus=self.
        _event_bus)
    assert metadata1.get('uuid') == metadata2.get('uuid'
        ), 'UUID should be preserved when content changes'
    assert metadata1.get('created_at') == metadata2.get('created_at'
        ), 'created_at should be preserved when content changes'
    assert metadata1.get('hash') != metadata2.get('hash'
        ), f"hash should change when content changes. Original: {metadata1.get('hash')}, New: {metadata2.get('hash')}"
    assert metadata1.get('last_modified_at') != metadata2.get(
        'last_modified_at'
        ), 'last_modified_at should be updated when content changes'
    assert metadata1.get('namespace') == metadata2.get('namespace'
        ), 'namespace should be preserved when only content changes'


def test_cross_handler_namespace_consistency(handler_factory) ->None:
    """
    Test that all handlers generate consistent namespace patterns.

    This test ensures that the namespace generation fix is applied consistently
    across all handlers and that they all use the correct 'omnibase.stamped' prefix.
    """
    handlers = [(PythonHandler, 'test.py'), (MarkdownHandler, 'test.md'), (
        MetadataYAMLHandler, 'test.yaml')]
    for handler_class, filename in handlers:
        handler = handler_factory(handler_class)
        file_path = Path(filename)
        mock_metadata = NodeMetadataBlock.create_with_defaults(name=
            file_path.stem, author='Test Author', file_path=file_path)
        namespace = get_namespace_str(mock_metadata.namespace)
        assert namespace.startswith('omnibase.stamped.'
            ), f'Handler {handler_class.__name__} generates incorrect namespace prefix: {namespace}'
        assert_namespace_compliance(namespace)


def test_namespace_validation_pattern_compliance() ->None:
    """
    Test that namespace validation patterns are correctly enforced.

    This test ensures that the namespace validation logic correctly identifies
    valid and invalid namespace patterns.
    """
    valid_namespaces = ['omnibase.stamped.test_file',
        'omnibase.stamped.complex_file_name', 'omnibase.stamped.simple',
        'omnibase.stamped.file123']
    invalid_namespaces = ['onex.stamped.test_file', 'omnibase.stamped.',
        'omnibase.stamped', 'wrong.prefix.test_file',
        'omnibase.stamped.test-file', 'omnibase.stamped.test file']
    for namespace in valid_namespaces:
        try:
            assert_namespace_compliance(get_namespace_str(namespace))
        except AssertionError as e:
            pytest.fail(f"Valid namespace '{namespace}' failed validation: {e}"
                )
    for namespace in invalid_namespaces:
        with pytest.raises(AssertionError):
            assert_namespace_compliance(get_namespace_str(namespace))


def extract_metadata_fields(handler, content: str, file_path: Path) ->Dict[
    str, Any]:
    """Extract metadata fields from stamped content using handler logic."""
    try:
        metadata_block, _ = handler.extract_block(file_path, content)
        if metadata_block:
            return metadata_block.model_dump()
        return {}
    except Exception:
        return {}


def assert_idempotency_fields_preserved(meta1: Dict[str, Any], meta2: Dict[
    str, Any]) ->None:
    """Assert that idempotency fields are preserved between two metadata instances."""
    assert meta1.get('uuid') == meta2.get('uuid'
        ), f"UUID not preserved: {meta1.get('uuid')} != {meta2.get('uuid')}"
    assert meta1.get('created_at') == meta2.get('created_at'
        ), f"created_at not preserved: {meta1.get('created_at')} != {meta2.get('created_at')}"


def assert_namespace_compliance(namespace: str) ->None:
    """Assert that a namespace follows the correct pattern."""
    prefix = get_namespace_prefix()
    pattern = f"^{prefix}\\.[a-zA-Z0-9_\\.']+$"
    assert re.match(pattern, namespace
        ), f"Namespace '{namespace}' does not match pattern: {pattern}"


def test_proper_namespace_generation(handler_factory, file_io: InMemoryFileIO
    ) ->None:
    """
    Test that the new namespace generation creates proper module-based namespaces.

    This test verifies that we've fixed the fundamental namespace issue where
    'omnibase.stamped.*' was being used instead of actual module hierarchy.
    """
    test_cases = [('src/omnibase/nodes/template_node/main.py',
        '^omnibase\\.nodes\\.template_node\\.main$'), (
        'src/omnibase/handlers/handler_python.py',
        '^omnibase\\.handlers\\.handler_python$'), (
        'src/omnibase/model/model_metadata.py',
        '^omnibase\\.model\\.model_metadata$'), ('scripts/fix_yaml.py',
        '^omnibase\\.scripts\\.fix_yaml$'), ('README.md',
        '^omnibase\\.README$'), ('test_file.py', '^omnibase\\.test_file$')]
    handler = handler_factory(PythonHandler)
    for file_path_str, expected_pattern in test_cases:
        file_path = Path(file_path_str)
        initial_content = f"# Test file: {file_path_str}\nprint('hello')\n"
        file_io.write_text(file_path, initial_content)
        content = file_io.read_text(file_path)
        result = handler.stamp(file_path, content)
        assert result.status == OnexStatus.SUCCESS, f'Stamping failed for {file_path_str}: {result.messages}'
        stamped_content = result.metadata.get('content', '')
        assert stamped_content, f'No stamped content found for {file_path_str}'
        metadata = extract_metadata_fields(handler, stamped_content, file_path)
        namespace = get_namespace_str(metadata.get('namespace'))
        assert namespace is not None, f'Namespace not found for {file_path_str}'
        assert re.match(expected_pattern, namespace
            ), f"File {file_path_str}: namespace '{namespace}' does not match expected pattern '{expected_pattern}'"
        assert 'stamped' not in namespace, f"File {file_path_str}: namespace '{namespace}' should not contain 'stamped'"
        assert namespace.startswith('omnibase.'
            ), f"File {file_path_str}: namespace '{namespace}' should start with 'omnibase.'"
        print(f'✅ {file_path_str} → {namespace}')


def test_debug_content_change_hash_calculation(handler_factory, file_io:
    InMemoryFileIO) ->None:
    """
    Debug test to understand why hash is not changing when content changes.

    This test will step through the process and log what's happening at each step.
    """
    handler = handler_factory(PythonHandler)
    file_path = Path('debug_test.py')
    initial_content = "# Initial Python file\nprint('hello')\n"
    file_io.write_text(file_path, initial_content)
    content1 = file_io.read_text(file_path)
    result1 = handler.stamp(file_path, content1)
    assert result1.status == OnexStatus.SUCCESS
    stamped_content1 = result1.metadata.get('content', '')
    print(f'\n=== FIRST STAMPING ===')
    print(f'Original content length: {len(content1)}')
    print(f'Stamped content length: {len(stamped_content1)}')
    metadata1 = extract_metadata_fields(handler, stamped_content1, file_path)
    original_hash = metadata1.get('hash')
    print(f'Original hash: {original_hash}')
    prev_meta1, rest1 = handler.extract_block(file_path, stamped_content1)
    print(f'Extracted rest1 length: {len(rest1) if rest1 else 0}')
    print(f'Extracted rest1 content: {repr(rest1)}')
    additional_content = (
        "\n# Added for debugging\ndef debug_function():\n    return 'debug'\n")
    modified_stamped_content = stamped_content1 + additional_content
    print(f'\n=== CONTENT MODIFICATION ===')
    print(f'Additional content: {repr(additional_content)}')
    print(f'Modified content length: {len(modified_stamped_content)}')
    prev_meta2, rest2 = handler.extract_block(file_path,
        modified_stamped_content)
    print(f'Extracted rest2 length: {len(rest2) if rest2 else 0}')
    print(f'Extracted rest2 content: {repr(rest2)}')
    print(f'Rest content changed: {rest1 != rest2}')
    result2 = handler.stamp(file_path, modified_stamped_content)
    assert result2.status == OnexStatus.SUCCESS
    stamped_content2 = result2.metadata.get('content', '')
    print(f'\n=== SECOND STAMPING ===')
    print(f'Second stamped content length: {len(stamped_content2)}')
    metadata2 = extract_metadata_fields(handler, stamped_content2, file_path)
    new_hash = metadata2.get('hash')
    print(f'New hash: {new_hash}')
    print(f'Hash changed: {original_hash != new_hash}')
    import hashlib
    if prev_meta1:
        meta1_dict = prev_meta1.model_dump()
        canonical1 = CanonicalYAMLSerializer().canonicalize_for_hash(meta1_dict
            , rest1 or '', volatile_fields=['hash', 'last_modified_at'],
            metadata_serializer=handler.serialize_block, body_canonicalizer
            =lambda x: x)
        manual_hash1 = hashlib.sha256(canonical1.encode()).hexdigest()
        print(f'Manual hash1: {manual_hash1}')
    if prev_meta2:
        meta2_dict = prev_meta2.model_dump()
        canonical2 = CanonicalYAMLSerializer().canonicalize_for_hash(meta2_dict
            , rest2 or '', volatile_fields=['hash', 'last_modified_at'],
            metadata_serializer=handler.serialize_block, body_canonicalizer
            =lambda x: x)
        manual_hash2 = hashlib.sha256(canonical2.encode()).hexdigest()
        print(f'Manual hash2: {manual_hash2}')
        print(f'Manual hashes different: {manual_hash1 != manual_hash2}')
    assert original_hash != new_hash, f'Hash should change when content changes'


def compare_stamped_content_idempotent(content1: str, content2: str) ->bool:
    """
    Compare two stamped contents for idempotency, masking volatile fields in the metadata block.
    Returns True if non-volatile content is identical, False otherwise.
    """
    from omnibase.mixin.mixin_canonical_serialization import (
        CanonicalYAMLSerializer,
        extract_metadata_block_and_body,
        strip_block_delimiters_and_assert,
    )
    from omnibase.model.model_node_metadata import NodeMetadataBlock
    meta_block1, rest1 = extract_metadata_block_and_body(content1,
        '# === OmniNode:Metadata ===', '# === /OmniNode:Metadata ===')
    meta_block2, rest2 = extract_metadata_block_and_body(content2,
        '# === OmniNode:Metadata ===', '# === /OmniNode:Metadata ===')
    if not meta_block1 or not meta_block2:
        return content1 == content2
    delimiters = {'=== OmniNode:Metadata ===', '=== /OmniNode:Metadata ==='}
    meta_yaml1 = strip_block_delimiters_and_assert(meta_block1.splitlines(),
        delimiters)
    meta_yaml2 = strip_block_delimiters_and_assert(meta_block2.splitlines(),
        delimiters)
    import yaml
    meta_dict1 = yaml.safe_load(meta_yaml1)
    meta_dict2 = yaml.safe_load(meta_yaml2)
    volatile_fields = NodeMetadataField.volatile()
    canon1 = CanonicalYAMLSerializer().canonicalize_metadata_block(meta_dict1,
        volatile_fields=volatile_fields, sort_keys=True, explicit_start=
        False, explicit_end=False, comment_prefix='# ')
    canon2 = CanonicalYAMLSerializer().canonicalize_metadata_block(meta_dict2,
        volatile_fields=volatile_fields, sort_keys=True, explicit_start=
        False, explicit_end=False, comment_prefix='# ')
    rest1 = rest1.strip()
    rest2 = rest2.strip()
    return canon1.strip() == canon2.strip() and rest1 == rest2


def get_namespace_str(ns):
    if isinstance(ns, dict) and 'value' in ns:
        return ns['value']
    if hasattr(ns, 'value'):
        return ns.value
    return str(ns)
