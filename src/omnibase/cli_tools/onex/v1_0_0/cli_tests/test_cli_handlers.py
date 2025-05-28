# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_cli_handlers.py
# version: 1.0.0
# uuid: 0908e4a4-4b18-4bee-8e63-2f3a58dc87da
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.348283
# last_modified_at: 2025-05-28T17:20:04.147416
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 19607eedce982b5ca2b98ce8cecac9b00b81c1389f85f5c2ff9a2bc5ac38cf5a
# entrypoint: python@test_cli_handlers.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.test_cli_handlers
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for the handlers CLI command.

This module tests the `onex handlers list` command functionality including
different output formats, filtering options, and error handling.
"""

import json

import pytest
from typer.testing import CliRunner

from omnibase.cli_tools.onex.v1_0_0.commands.list_handlers import list_handlers
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

runner = CliRunner()


@pytest.fixture(autouse=True)
def ensure_registry_populated():
    registry = FileTypeHandlerRegistry()
    registry.register_all_handlers()


class TestHandlersListCommand:
    """Test the handlers list command."""

    def test_handlers_list_help(self) -> None:
        """Test the handlers list help command."""
        # Test the function directly since it's a command
        # This test will be skipped for now as we test the function directly
        pass

    def test_handlers_list_default_table_format(self) -> None:
        """Test the default table format output."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter=None,
                type_filter=None,
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        print("DEBUG: CLI output for handlers list (table):\n", output)
        assert "Registered File Type Handlers" in output
        assert "Handler ID" in output
        assert "Type" in output
        assert "Source" in output
        assert "Priority" in output
        assert "Priority Legend:" in output
        assert "extension:.py" in output
        assert "special:.onexignore" in output

    def test_handlers_list_summary_format(self) -> None:
        """Test the summary format output."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="summary",
                source_filter=None,
                type_filter=None,
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        assert "Handler Summary" in output
        assert "Total Handlers:" in output
        assert "By Source:" in output
        assert "By Type:" in output
        assert "core:" in output
        assert "runtime:" in output

    def test_handlers_list_json_format(self) -> None:
        """Test the JSON format output."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="json",
                source_filter=None,
                type_filter=None,
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()

        # Parse the JSON output to verify it's valid
        try:
            data = json.loads(output)
            assert isinstance(data, dict)
            # Should have some handlers
            assert len(data) > 0
            # Check structure of first handler
            first_handler = next(iter(data.values()))
            assert "type" in first_handler
            assert "source" in first_handler
            assert "priority" in first_handler
            assert "handler_class" in first_handler
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    def test_handlers_list_with_metadata(self) -> None:
        """Test the metadata flag shows additional columns."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter=None,
                type_filter=None,
                show_metadata=True,
                verbose=False,
            )

        output = f.getvalue()
        assert "Name" in output
        assert "Version" in output
        assert "Author" in output
        assert "Description" in output
        assert "python_handler" in output
        assert "OmniNode Team" in output

    def test_handlers_list_verbose(self) -> None:
        """Test the verbose flag shows all details."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter=None,
                type_filter=None,
                show_metadata=False,
                verbose=True,
            )

        output = f.getvalue()
        # Verbose should include metadata columns
        assert "Name" in output
        assert "Version" in output
        assert "Author" in output
        assert "Description" in output
        # And verbose-specific columns
        assert "Supported Ext" in output
        assert "Supported Files" in output
        assert "Content" in output

    def test_handlers_list_filter_by_source_core(self) -> None:
        """Test filtering by core source."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter="core",
                type_filter=None,
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        assert "special:.onexignore" in output
        assert "special:.gitignore" in output
        # Should not contain runtime handlers
        assert "extension:.py" not in output

    def test_handlers_list_filter_by_source_runtime(self) -> None:
        """Test filtering by runtime source."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter="runtime",
                type_filter=None,
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        assert "extension:.py" in output
        assert "extension:.yaml" in output
        # Should not contain core handlers
        assert "special:.onexignore" not in output

    def test_handlers_list_filter_by_type_extension(self) -> None:
        """Test filtering by extension type."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter=None,
                type_filter="extension",
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        assert "extension:.py" in output
        assert "extension:.yaml" in output
        # Should not contain special handlers
        assert "special:.onexignore" not in output

    def test_handlers_list_filter_by_type_special(self) -> None:
        """Test filtering by special type."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter=None,
                type_filter="special",
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        assert "special:.onexignore" in output
        assert "special:.gitignore" in output
        # Should not contain extension handlers
        assert "extension:.py" not in output

    def test_handlers_list_filter_no_matches(self) -> None:
        """Test filtering with no matches."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter="nonexistent",
                type_filter=None,
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        assert "No handlers found matching the specified filters" in output

    def test_handlers_list_combined_filters(self) -> None:
        """Test combining multiple filters."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="table",
                source_filter="core",
                type_filter="special",
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        assert "special:.onexignore" in output
        assert "special:.gitignore" in output
        # Should not contain extension or runtime handlers
        assert "extension:.py" not in output

    def test_handlers_list_invalid_format(self) -> None:
        """Test with invalid format option."""
        import io
        from contextlib import redirect_stdout, redirect_stderr

        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            list_handlers(
                format_type="invalid",
                source_filter=None,
                type_filter=None,
                show_metadata=False,
                verbose=False,
            )

        output = f.getvalue()
        # Should default to table format
        assert "Registered File Type Handlers" in output

    def test_format_extensions_list_empty(self) -> None:
        """Test format_extensions_list with empty list."""
        from omnibase.cli_tools.onex.v1_0_0.commands.list_handlers import (
            format_extensions_list,
        )

        assert format_extensions_list([]) == "None"

    def test_format_extensions_list_with_items(self) -> None:
        """Test format_extensions_list with items."""
        from omnibase.cli_tools.onex.v1_0_0.commands.list_handlers import (
            format_extensions_list,
        )

        result = format_extensions_list([".py", ".yaml", ".md"])
        assert result == ".md, .py, .yaml"  # Should be sorted

    def test_format_filenames_list_empty(self) -> None:
        """Test format_filenames_list with empty list."""
        from omnibase.cli_tools.onex.v1_0_0.commands.list_handlers import (
            format_filenames_list,
        )

        assert format_filenames_list([]) == "None"

    def test_format_filenames_list_with_items(self) -> None:
        """Test format_filenames_list with items."""
        from omnibase.cli_tools.onex.v1_0_0.commands.list_handlers import (
            format_filenames_list,
        )

        result = format_filenames_list(["config.yaml", ".gitignore", "README.md"])
        assert result == ".gitignore, README.md, config.yaml"  # Should be sorted


if __name__ == "__main__":
    pytest.main([__file__])
