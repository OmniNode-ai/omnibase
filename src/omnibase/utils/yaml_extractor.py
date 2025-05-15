from pathlib import Path
import yaml
from omnibase.core.errors import OmniBaseError


def extract_example_from_schema(schema_path: Path, example_index: int = 0) -> dict:
    """
    Extract a node metadata example from a YAML schema file's 'examples' section.
    Returns the example at the given index as a dict.
    Raises OmniBaseError if the schema or example is missing or malformed.
    """
    try:
        with schema_path.open("r") as f:
            data = yaml.safe_load(f)
        examples = data.get("examples")
        if not examples or not isinstance(examples, list):
            raise OmniBaseError(f"No 'examples' section found in schema: {schema_path}")
        if example_index >= len(examples):
            raise OmniBaseError(f"Example index {example_index} out of range for schema: {schema_path}")
        example = examples[example_index]
        if not isinstance(example, dict):
            raise OmniBaseError(f"Example at index {example_index} is not a dict in schema: {schema_path}")
        return example
    except Exception as e:
        raise OmniBaseError(f"Failed to extract example from schema: {schema_path}: {e}")

# TODO: Add CLI and formatting utilities for M1+ 