# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: docstring_generator.py
# version: 1.0.0
# uuid: 5522b60e-7a02-4dc9-964c-fbe8761fdf48
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.168966
# last_modified_at: 2025-05-21T16:42:46.047508
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 687aa2397ad6dc129c2503f1a1b659a94422bb616389d04c1fb7e61795482413
# entrypoint: python@docstring_generator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.docstring_generator
# meta_type: tool
# === /OmniNode:Metadata ===


import argparse
import json
from pathlib import Path
from typing import Any, cast

import yaml
from jinja2 import Environment, FileSystemLoader

SCHEMA_DIR = Path("src/omnibase/schemas")
TEMPLATE_PATH = Path("docs/templates/schema_doc.md.j2")
OUTPUT_DIR = Path("docs/generated")
CHANGELOG_PATH = Path("docs/changelog.md")

# Utility: Load changelog as a string


def load_changelog() -> str | None:
    if CHANGELOG_PATH.exists():
        with CHANGELOG_PATH.open("r") as f:
            return f.read()
    return None


# Utility: Parse schema file (YAML or JSON)
def load_schema(path: Path) -> dict[str, Any]:
    """Load a schema from a file and return as a dictionary."""
    if path.suffix == ".yaml":
        with path.open("r") as f:
            # Cast to dict[str, Any] for mypy compliance
            return cast(dict[str, Any], yaml.safe_load(f))
    elif path.suffix == ".json":
        with path.open("r") as f:
            # Cast to dict[str, Any] for mypy compliance
            return cast(dict[str, Any], json.load(f))
    else:
        raise ValueError(f"Unsupported schema file: {path}")


# Utility: Extract fields from schema
def extract_fields(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract fields from a schema dictionary."""
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields = []
    for name, prop in props.items():
        field = {
            "name": name,
            "type": prop.get("type", "object"),
            "required": name in required,
            "description": prop.get("description", ""),
            "enum": prop.get("enum", None),
        }
        fields.append(field)
    return fields


# Utility: Extract examples from schema
def extract_examples(schema: dict[str, Any]) -> list[str]:
    """Extract example strings from a schema dictionary."""
    examples = schema.get("examples", [])
    if isinstance(examples, list):
        return [yaml.dump(ex, sort_keys=False) for ex in examples]
    return []


# --- Stubs for mypy compliance ---
def extract_docstring_metadata(docstring: str) -> dict[str, Any]:
    """Stub for docstring metadata extraction."""
    return {}


def parse_function_signature(signature: str) -> dict[str, Any]:
    """Stub for function signature parsing."""
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Markdown docs for all schemas."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(OUTPUT_DIR),
        help="Output directory for Markdown docs.",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_PATH.parent)))
    template = env.get_template(TEMPLATE_PATH.name)
    changelog = load_changelog()

    # Discover schemas (deduplicate YAML/JSON pairs)
    seen = set()
    for schema_path in sorted(SCHEMA_DIR.glob("*.yaml")):
        name = schema_path.stem
        seen.add(name)
        schema = load_schema(schema_path)
        title = schema.get("title", name)
        version = schema.get("SCHEMA_VERSION", schema.get("schema_version", "unknown"))
        description = schema.get("description", "")
        fields = extract_fields(schema)
        examples = extract_examples(schema)
        doc = template.render(
            title=title,
            version=version,
            description=description,
            changelog=changelog,
            fields=fields,
            examples=examples,
        )
        out_path = output_dir / f"{name}.md"
        with out_path.open("w") as f:
            f.write(doc)
        if args.verbose:
            print(f"Generated {out_path}")
    # Now handle JSON schemas not already seen
    for schema_path in sorted(SCHEMA_DIR.glob("*.json")):
        name = schema_path.stem
        if name in seen:
            continue
        schema = load_schema(schema_path)
        title = schema.get("title", name)
        version = schema.get("SCHEMA_VERSION", schema.get("schema_version", "unknown"))
        description = schema.get("description", "")
        fields = extract_fields(schema)
        examples = extract_examples(schema)
        doc = template.render(
            title=title,
            version=version,
            description=description,
            changelog=changelog,
            fields=fields,
            examples=examples,
        )
        out_path = output_dir / f"{name}.md"
        with out_path.open("w") as f:
            f.write(doc)
        if args.verbose:
            print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
