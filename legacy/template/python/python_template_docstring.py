#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_template_docstring"
# namespace: "omninode.tools.python_template_docstring"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:31+00:00"
# last_modified_at: "2025-05-05T13:00:31+00:00"
# entrypoint: "python_template_docstring.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Standard docstring format for Python files.

This module demonstrates the required format for docstrings in Python files,
including module level docstrings, class docstrings with Attributes sections,
and function docstrings with Args, Returns, and Raises sections.

Examples:
    Basic usage example of the module:

    >>> from mymodule import ExampleClass
    >>> obj = ExampleClass(param1="value1")
    >>> result = obj.example_method(42)
    >>> print(result)
    Success

Notes:
    This template follows the project's documentation standards
    and should be used as a reference for all Python files.

Attributes:
    CONSTANT_VALUE (int): A module-level constant used for demonstration
    DEFAULT_TIMEOUT (float): Default timeout value in seconds
"""


CONSTANT_VALUE: int = 42
DEFAULT_TIMEOUT: float = 30.0


class ExampleClass:
    """A template class demonstrating proper docstring format.

    This class serves as an example of how to document a Python class
    including its attributes, methods, and usage examples.

    Attributes:
        name (str): The name of the example instance
        value (int): A numeric value for the instance
        config (dict): Configuration dictionary for the instance

    Examples:
        >>> obj = ExampleClass("test", 42)
        >>> obj.example_method(10)
        'Success'

    Notes:
        This class demonstrates the required sections for class docstrings
        including Attributes, Examples, and Notes sections.
    """

    def __init__(self, name: str, value: int = 0):
        """Initialize the example class.

        Args:
            name (str): The name for this instance
            value (int, optional): Initial value. Defaults to 0.

        Raises:
            ValueError: If name is empty or value is negative
        """
        if not name:
            raise ValueError("Name cannot be empty")
        if value < 0:
            raise ValueError("Value cannot be negative")

        self.name = name
        self.value = value
        self.config = {}

    def example_method(self, param: int) -> str:
        """Process the parameter and return a result.

        This method demonstrates proper docstring format for methods,
        including Args, Returns, and Raises sections.

        Args:
            param (int): The input parameter to process

        Returns:
            str: The result of the processing

        Raises:
            ValueError: If param is negative
            TypeError: If param is not an integer

        Examples:
            >>> obj = ExampleClass("test")
            >>> obj.example_method(42)
            'Success'

        Notes:
            This method is for demonstration purposes only.
        """
        if not isinstance(param, int):
            raise TypeError("Parameter must be an integer")
        if param < 0:
            raise ValueError("Parameter cannot be negative")

        return "Success"