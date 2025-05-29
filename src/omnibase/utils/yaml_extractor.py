# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.282097'
# description: Stamped by PythonHandler
# entrypoint: python://yaml_extractor.py
# hash: 220ab0e44187e92116c2189b988835ba01bec99166f5fb1f01209a52a921e801
# last_modified_at: '2025-05-29T11:50:12.533883+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: yaml_extractor.py
# namespace: omnibase.yaml_extractor
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 61b925ef-aa72-4f23-8cc0-77681c4c69f0
# version: 1.0.0
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
