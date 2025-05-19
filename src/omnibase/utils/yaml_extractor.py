# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 446869dd-546c-4d3d-8bce-4984e5e2d107
# name: yaml_extractor.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:57.268527
# last_modified_at: 2025-05-19T16:19:57.268529
# description: Stamped Python file: yaml_extractor.py
# state_contract: none
# lifecycle: active
# hash: 316f1a0b9e29d5e3b29e52ad6eaece1779dcca1093e72ba84b1e2ee9688d3344
# entrypoint: {'type': 'python', 'target': 'yaml_extractor.py'}
# namespace: onex.stamped.yaml_extractor.py
# meta_type: tool
# === /OmniNode:Metadata ===

from pathlib import Path
from typing import Any

import yaml

from omnibase.core.errors import OmniBaseError


def extract_example_from_schema(
    schema_path: Path, example_index: int = 0
) -> dict[str, Any]:
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
            raise OmniBaseError(
                f"Example index {example_index} out of range for schema: {schema_path}"
            )
        example = examples[example_index]
        if not isinstance(example, dict):
            raise OmniBaseError(
                f"Example at index {example_index} is not a dict in schema: {schema_path}"
            )
        return example
    except Exception as e:
        raise OmniBaseError(
            f"Failed to extract example from schema: {schema_path}: {e}"
        )


# TODO: Add CLI and formatting utilities for M1+
