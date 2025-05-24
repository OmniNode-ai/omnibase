# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: yaml_extractor.py
# version: 1.0.0
# uuid: a8fec6df-2244-43cd-88ee-a7360a0403f8
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.169899
# last_modified_at: 2025-05-21T16:42:46.044379
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 772a66a47311e9da78797cfdde5eef56e64424c6e4fa0ba5e2a834e0605f1d34
# entrypoint: python@yaml_extractor.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.yaml_extractor
# meta_type: tool
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any

import yaml

from omnibase.exceptions import OmniBaseError


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
