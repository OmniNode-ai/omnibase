# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: sample_python_functions.py
# version: 1.0.0
# uuid: 8f66a17f-8dd9-4743-a9c8-32bd13be8cd0
# author: OmniNode Team
# created_at: 2025-05-26T08:43:55.222821
# last_modified_at: 2025-05-26T14:02:03.079071
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6a7b4cee693909493e4f7282d03fa04efca415b4bae5292191592126f27fc6f2
# entrypoint: python@sample_python_functions.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.sample_python_functions
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Sample Python file for function discovery testing.
This file contains various function patterns to test the discovery system.
"""

from omnibase.core.error_codes import CoreErrorCode, OnexError


def regular_function(x: int, y: int) -> int:
    """This function should NOT be discovered (no marker)."""
    return x + y


def validate_schema(schema: dict, correlation_id: str | None = None) -> bool:
    """
    Validates JSON schema format and structure.

    @onex:function
    @raises SCHEMA_INVALID
    @raises SCHEMA_MALFORMED
    @side_effect logs validation events

    Args:
        schema: Dictionary containing the schema to validate
        correlation_id: Optional correlation ID for tracking

    Returns:
        bool: True if schema is valid, False otherwise
    """
    if not isinstance(schema, dict):
        raise OnexError("Schema must be a dictionary", CoreErrorCode.VALIDATION_FAILED)
    return True


def process_data(data: list, transform_rules: list | None = None) -> dict:
    """
    Process and transform input data according to rules.

    @onex:function
    @raises DATA_INVALID
    @raises TRANSFORM_FAILED
    @side_effect logs processing events
    @side_effect may cache results

    Args:
        data: List of data items to process
        transform_rules: Optional transformation rules

    Returns:
        dict: Processed data results
    """
    if not isinstance(data, list):
        raise OnexError("Data must be a list", CoreErrorCode.VALIDATION_FAILED)
    return {"processed": len(data), "rules_applied": len(transform_rules or [])}


def calculate_metrics(values: list[float], metric_type: str = "mean") -> float:
    """
    Calculate statistical metrics from a list of values.

    @onex:function
    @raises INVALID_METRIC_TYPE
    @raises EMPTY_VALUES_LIST
    @side_effect logs calculation events

    Args:
        values: List of numeric values
        metric_type: Type of metric to calculate (mean, median, sum)

    Returns:
        float: Calculated metric value
    """
    if not values:
        raise OnexError("Values list cannot be empty", CoreErrorCode.VALIDATION_FAILED)

    if metric_type == "mean":
        return sum(values) / len(values)
    elif metric_type == "median":
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            return sorted_values[n // 2]
    elif metric_type == "sum":
        return sum(values)
    else:
        raise OnexError(
            f"Unknown metric type: {metric_type}", CoreErrorCode.INVALID_PARAMETER
        )


if __name__ == "__main__":
    # Test the functions
    print(f"Sum: {regular_function(5, 3)}")
    print(f"Schema valid: {validate_schema({'type': 'object'})}")
    print(f"Data processed: {process_data([1, 2, 3])}")
    print(f"Mean: {calculate_metrics([1, 2, 3, 4, 5])}")
