#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: ast_visitors
# namespace: omninode.tools.ast_visitors
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:02+00:00
# last_modified_at: 2025-04-27T18:13:02+00:00
# entrypoint: ast_visitors.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""ast_visitors.py
containers.foundation.src.foundation.script.validate.ast_visitors.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast


class TestVisitor(ast.NodeVisitor):
    """AST visitor for finding test classes and functions."""

    __test__ = False

    def __init__(self):
        self.test_items = []
        self.current_class = None

    def visit_ClassDef(self, node):
        is_test_class = node.name.startswith("Test")
        if is_test_class:
            if self._has_skip_decorator(node):
                self.generic_visit(node)
                return
            old_class = self.current_class
            self.current_class = {
                "type": "class",
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", None),
            }
            self.test_items.append(self.current_class)
            self.generic_visit(node)
            self.current_class = old_class
        else:
            self.generic_visit(node)

    def visit_FunctionDef(self, node):
        is_test_function = node.name.startswith("test_")
        if is_test_function:
            if self._has_skip_decorator(node):
                self.generic_visit(node)
                return
            test_item = {
                "type": "method" if self.current_class else "function",
                "name": (
                    f"{self.current_class['name']}.{node.name}"
                    if self.current_class
                    else node.name
                ),
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", None),
            }
            self.test_items.append(test_item)
        self.generic_visit(node)

    def _has_skip_decorator(self, node):
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Attribute)
                and hasattr(decorator, "attr")
                and decorator.attr == "skip"
                and isinstance(decorator.value, ast.Attribute)
                and hasattr(decorator.value, "attr")
                and decorator.value.attr == "mark"
                and isinstance(decorator.value.value, ast.Name)
                and hasattr(decorator.value.value, "id")
                and decorator.value.value.id == "pytest"
            ):
                return True
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and hasattr(decorator.func, "attr")
                and decorator.func.attr == "skip"
                and isinstance(decorator.func.value, ast.Attribute)
                and hasattr(decorator.func.value, "attr")
                and decorator.func.value.attr == "mark"
                and isinstance(decorator.func.value.value, ast.Name)
                and hasattr(decorator.func.value.value, "id")
                and decorator.func.value.value.id == "pytest"
            ):
                return True
        return False


class ImplementationVisitor(ast.NodeVisitor):
    """AST visitor for finding implementation functions and methods."""

    def __init__(self, module_path):
        self.module_path = module_path
        self.current_class = None
        self.functions = set()

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        if self.current_class:
            function_path = f"{self.module_path}.{self.current_class}.{node.name}"
        else:
            function_path = f"{self.module_path}.{node.name}"
        self.functions.add(function_path)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
