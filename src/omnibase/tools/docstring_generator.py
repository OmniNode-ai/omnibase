import argparse
import json
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

SCHEMA_DIR = Path("src/omnibase/schemas")
TEMPLATE_PATH = Path("docs/templates/schema_doc.md.j2")
OUTPUT_DIR = Path("docs/generated")
CHANGELOG_PATH = Path("docs/changelog.md")

# Utility: Load changelog as a string


def load_changelog():
    if CHANGELOG_PATH.exists():
        with CHANGELOG_PATH.open("r") as f:
            return f.read()
    return None


# Utility: Parse schema file (YAML or JSON)
def load_schema(path):
    if path.suffix == ".yaml":
        with path.open("r") as f:
            return yaml.safe_load(f)
    elif path.suffix == ".json":
        with path.open("r") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported schema file: {path}")


# Utility: Extract fields from schema
def extract_fields(schema):
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
def extract_examples(schema):
    examples = schema.get("examples", [])
    if isinstance(examples, list):
        return [yaml.dump(ex, sort_keys=False) for ex in examples]
    return []


def main():
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
