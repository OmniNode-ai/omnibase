# TODO: Implement full .tree validation tests in M1+.
# See docs/testing.md and milestone_0_checklist.md for requirements.

import os
from pathlib import Path

import pytest
import yaml


def test_tree_format_yaml_exists_and_is_valid():
    tree_path = Path("src/omnibase/schemas/tree_format.yaml")
    assert tree_path.exists(), "tree_format.yaml does not exist"
    # TODO: Extend with real structure/content validation in M1+
    with tree_path.open("r") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, (dict, list)), "tree_format.yaml must be a dict or list"


TREE_DISCOVERY_TEST_CASES = {}


def register_tree_discovery_test_case(name):
    def decorator(cls):
        TREE_DISCOVERY_TEST_CASES[name] = cls
        return cls

    return decorator


@register_tree_discovery_test_case("stub_tree_structure")
class StubTreeStructureCase:
    def run(self, tree_structure):
        # Stub: tree_structure is a list of node paths
        for path in tree_structure:
            assert os.path.exists(path)
            # TODO: Add logic to parse node.onex.yaml and assert validity
        # TODO: Add negative tests in M1+


@pytest.fixture
def stub_tree_structure():
    # Stub: Replace with real .tree loading logic in M1+
    return ["src/omnibase/schemas/onex_node.yaml"]


@pytest.mark.parametrize(
    "test_case",
    list(TREE_DISCOVERY_TEST_CASES.values()),
    ids=list(TREE_DISCOVERY_TEST_CASES.keys()),
)
def test_tree_discovery_cases(test_case, stub_tree_structure):
    test_case().run(stub_tree_structure)


# TODO: Replace stub_tree_structure with real .tree loader and add negative tests in M1+
