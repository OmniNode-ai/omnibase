"""
Stub test for reducer snapshot_state() returning a BaseModel.
Registry-driven, fixture-injected pattern. See docs/testing.md.
"""

import pytest
from pydantic import BaseModel

from omnibase.protocol.protocol_reducer import ProtocolReducer

REDUCER_TEST_CASES = {}


def register_reducer_test_case(name):
    def decorator(cls):
        REDUCER_TEST_CASES[name] = cls
        return cls

    return decorator


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock", marks=pytest.mark.mock),
        pytest.param("integration", id="integration", marks=pytest.mark.integration),
    ]
)
def context(request):
    return request.param


class StubReducer(ProtocolReducer):
    def snapshot_state(self) -> BaseModel:
        class DummyModel(BaseModel):
            foo: str = "bar"

        return DummyModel()


@register_reducer_test_case("stub_snapshot")
class StubSnapshotCase:
    def run(self, reducer, context):
        result = reducer.snapshot_state()
        assert isinstance(result, BaseModel)
        # TODO: Add more assertions and negative tests in M1+


@pytest.mark.parametrize(
    "context", ["mock", "integration"], ids=["mock", "integration"]
)
@pytest.mark.parametrize(
    "test_case", list(REDUCER_TEST_CASES.values()), ids=list(REDUCER_TEST_CASES.keys())
)
def test_reducer_snapshot_cases(test_case, context):
    reducer = StubReducer()
    test_case().run(reducer, context)


# TODO: Replace StubReducer with real implementation in M1+
