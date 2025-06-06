import pytest
import yaml
from pathlib import Path
from importlib import import_module
import sys
import os
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.nodes.template_node.v1_0_0.models.state import TemplateNodeInputState, TemplateNodeOutputState
from pydantic import ValidationError
import enum

SCENARIO_INDEX = Path(__file__).parent / "index.yaml"
SCENARIO_DIR = Path(__file__).parent
SNAPSHOT_DIR = SCENARIO_DIR.parent / "snapshots"
NODE_MODULE = "omnibase.nodes.template_node.v1_0_0.node"

# Load scenario registry
with open(SCENARIO_INDEX, "r") as f:
    scenario_index = yaml.safe_load(f)

scenarios = scenario_index.get("scenarios", [])

PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def pytest_addoption(parser):
    parser.addoption(
        "--regenerate-snapshots",
        action="store_true",
        default=False,
        help="Regenerate scenario output snapshots."
    )

def enum_to_value(obj):
    if isinstance(obj, dict):
        return {k: enum_to_value(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [enum_to_value(i) for i in obj]
    elif isinstance(obj, enum.Enum):
        return obj.value
    else:
        return obj

@pytest.mark.parametrize("scenario_entry", scenarios, ids=[s["id"] for s in scenarios])
def test_scenario(scenario_entry, request):
    regenerate_snapshots = request.config.getoption("--regenerate-snapshots") or os.environ.get("REGENERATE_SNAPSHOTS") == "1"
    scenario_id = scenario_entry["id"]
    entrypoint = Path(scenario_entry["entrypoint"])
    if entrypoint.is_absolute():
        scenario_path = entrypoint
    else:
        scenario_path = (SCENARIO_DIR / entrypoint.name) if entrypoint.parts[0] == "scenarios" else (SCENARIO_DIR / entrypoint)
    with open(scenario_path, "r") as f:
        scenario = yaml.safe_load(f)
    chain = scenario["chain"][0]
    node_input = chain["input"]
    expected = chain["expect"]

    # Import the node and run with input
    node_mod = import_module(NODE_MODULE.replace("/", "."))
    node_cls = getattr(node_mod, "TemplateNode")
    node = node_cls(event_bus=InMemoryEventBus())  # Force in-memory event bus for tests
    try:
        input_state = TemplateNodeInputState(**node_input)
    except ValidationError as e:
        # If we get a validation error, the scenario should expect failure
        assert scenario_entry.get('expected_result', 'success') == 'failure', f"Scenario {scenario_entry['id']} failed validation unexpectedly: {e}"
        return
    result = node.run(input_state)
    # Canonicalize output as dict for snapshot
    if hasattr(result, 'model_dump'):
        result_dict = result.model_dump()
    else:
        result_dict = dict(result)
    # Validate output as TemplateNodeOutputState
    try:
        snapshot_model = TemplateNodeOutputState(**result_dict)
    except ValidationError as e:
        raise AssertionError(f"Output is not a valid TemplateNodeOutputState for scenario {scenario_id}: {e}")
    # Prepare snapshot path
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    snapshot_path = SNAPSHOT_DIR / f"snapshot_{scenario_id}.yaml"
    # If regenerating or snapshot does not exist, write snapshot
    if regenerate_snapshots or not snapshot_path.exists():
        # Convert Enums to their values for YAML serialization
        serializable_result = enum_to_value(result_dict)
        with open(snapshot_path, "w") as f:
            yaml.safe_dump(serializable_result, f, sort_keys=False)
    else:
        # Load and validate snapshot
        with open(snapshot_path, "r") as f:
            snapshot_data = yaml.safe_load(f)
        if snapshot_data is None:
            if regenerate_snapshots:
                # Regenerate the snapshot if allowed
                serializable_result = enum_to_value(result_dict)
                with open(snapshot_path, "w") as f:
                    yaml.safe_dump(serializable_result, f, sort_keys=False)
                # Reload for validation
                with open(snapshot_path, "r") as f:
                    snapshot_data = yaml.safe_load(f)
            else:
                raise AssertionError(f"Snapshot file {snapshot_path} is empty or invalid YAML. Delete or regenerate the snapshot.")
        try:
            snapshot_loaded = TemplateNodeOutputState(**snapshot_data)
        except ValidationError as e:
            raise AssertionError(f"Snapshot file {snapshot_path} is not a valid TemplateNodeOutputState: {e}")
        # Model-aware comparison
        assert snapshot_loaded.model_dump() == snapshot_model.model_dump(), f"Snapshot mismatch for scenario {scenario_id}\nExpected: {snapshot_loaded.model_dump()}\nActual: {snapshot_model.model_dump()}"
    # If we reach here, the scenario should expect success
    assert scenario_entry.get('expected_result', 'success') == 'success', f"Scenario {scenario_entry['id']} expected failure but passed" 