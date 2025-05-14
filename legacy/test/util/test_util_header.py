import pytest
from typing import List
from foundation.registry.utility_registry import get_util
from foundation.protocol.protocol_util_header import ProtocolUtilHeader
from foundation.test.test_case_registry import TEST_CASE_REGISTRY

def get_header_util() -> ProtocolUtilHeader:
    util = get_util('header')
    assert isinstance(util, ProtocolUtilHeader)
    return util

def test_extract_shebang():
    util = get_header_util()
    lines = ['#!/usr/bin/env python3', 'print("hi")']
    shebang, rest = util.extract_shebang(lines)
    assert shebang == '#!/usr/bin/env python3'
    assert rest == ['print("hi")']

    lines = ['print("hi")']
    shebang, rest = util.extract_shebang(lines)
    assert shebang is None
    assert rest == ['print("hi")']

def test_extract_module_docstring():
    util = get_header_util()
    lines = ['"""Module docstring"""', 'print("hi")']
    doc, rest = util.extract_module_docstring(lines)
    assert doc == '"""Module docstring"""'
    assert rest == ['print("hi")']

    lines = ['# comment', 'print("hi")']
    doc, rest = util.extract_module_docstring(lines)
    assert doc is None
    assert rest == ['# comment', 'print("hi")']

def test_extract_future_imports():
    util = get_header_util()
    lines = ['from __future__ import annotations', 'from __future__ import print_function', 'print("hi")']
    futures, rest = util.extract_future_imports(lines)
    assert futures == ['from __future__ import annotations', 'from __future__ import print_function']
    assert rest == ['print("hi")']

    lines = ['print("hi")']
    futures, rest = util.extract_future_imports(lines)
    assert futures == []
    assert rest == ['print("hi")']

def test_normalize_python_header():
    util = get_header_util()
    lines = [
        '#!/usr/bin/env python3',
        '"""Module docstring"""',
        'from __future__ import annotations',
        'from __future__ import print_function',
        'print("hi")'
    ]
    header, rest = util.normalize_python_header(lines)
    assert header == [
        '#!/usr/bin/env python3',
        '"""Module docstring"""',
        'from __future__ import annotations',
        'from __future__ import print_function'
    ]
    assert rest == ['print("hi")']

@pytest.fixture
def utility_registry():
    class Registry(dict):
        def register(self, name, obj):
            self[name] = obj
        def get(self, name):
            return self[name]
    reg = Registry()
    reg.register('header', get_util('header'))
    return reg

class TestUtilHeaderHybrid:
    """
    Hybrid pattern: registry-driven, DI-compliant, protocol-compliant test for UtilHeader.
    """
    def test_extract_header_valid(self, utility_registry):
        fname = TEST_CASE_REGISTRY.get_test_case("header_util", "valid_header_shebang", "valid")
        with open(fname, "r") as f:
            lines = f.read().splitlines()
        util: ProtocolUtilHeader = utility_registry.get('header')
        shebang, rest = util.extract_shebang(lines)
        assert shebang == '#!/usr/bin/env python3'
        docstring, rest2 = util.extract_module_docstring(rest)
        assert docstring.startswith('"""Module docstring')
        future_imports, rest3 = util.extract_future_imports(rest2)
        assert future_imports == ['from __future__ import annotations']
        header, rest4 = util.normalize_python_header(lines)
        assert header[0] == '#!/usr/bin/env python3'
        assert any('Module docstring' in h for h in header)
        assert any('from __future__ import annotations' in h for h in header)
        assert rest4 == ['print("hello world")']

    def test_extract_header_invalid(self, utility_registry):
        fname = TEST_CASE_REGISTRY.get_test_case("header_util", "invalid_header_no_shebang", "invalid")
        with open(fname, "r") as f:
            lines = f.read().splitlines()
        util: ProtocolUtilHeader = utility_registry.get('header')
        shebang, rest = util.extract_shebang(lines)
        assert shebang is None
        docstring, rest2 = util.extract_module_docstring(rest)
        assert docstring.startswith('"""Module docstring')
        future_imports, rest3 = util.extract_future_imports(rest2)
        assert future_imports == ['from __future__ import annotations']
        header, rest4 = util.normalize_python_header(lines)
        assert all(not h.startswith('#!') for h in header)
        assert any('Module docstring' in h for h in header)
        assert any('from __future__ import annotations' in h for h in header)
        assert rest4 == ['print("hello world")'] 