<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: dda9829f-30e8-4fa9-83a1-32f510a6156e -->
<!-- name: milestone_0_bootstrap.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:57.269719 -->
<!-- last_modified_at: 2025-05-19T16:19:57.269720 -->
<!-- description: Stamped Markdown file: milestone_0_bootstrap.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 1bedad876ba29c0d673b88ffdf3f1ec317f9ee7694acdff7f3821d056767f229 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'milestone_0_bootstrap.md'} -->
<!-- namespace: onex.stamped.milestone_0_bootstrap.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# Milestone 0: ONEX Bootstrap – Initial Project Scaffolding

> **Status:** Canonical Draft
> **Last Updated:** 2025-05-18
> **Purpose:** Establish the foundational directory structure, core libraries, and bootstrapping utilities required to build and validate the ONEX system. This milestone precedes Milestone 1 and enables all metadata, validation, and CI logic to be implemented correctly and consistently. M0 focuses on creating *stubs* and *placeholders* that align with the full ONEX architecture defined in the Node Architecture documentation series.
> **Audience:** Node authors, tool builders, runtime developers, CI engineers

---

## 🔧 Why This Milestone Exists

Although Milestone 1 defines the initial schemas, metadata standards, and validation tools, those deliverables require supporting infrastructure to exist first:
- Source layout for `src/omnibase/`, `tests/`, and CLI tooling following [Structural Conventions](./docs/nodes/onex_structural_conventions.md)
- Base registry for loading and discovering schemas
- Shared validation/error handling infrastructure
- Stamping and hashing utility interfaces
- CI-compatible module layout
- Foundational protocol interfaces defined in [Protocol Definitions](./docs/nodes/onex_protocol_definitions.md)
- Canonical `.onex` node handling logic based on the [Node Contracts and Metadata Specification](./docs/nodes/node_contracts.md)

Rather than duplicating partial setups across multiple tasks, Milestone 0 provides a clean, minimal foundation aligned with ONEX conventions and ready to support all further work by creating necessary stubs and placeholders.

---

## 🧱 ONEX Node Concept (Bootstrap Overview)

At the Milestone 0 level, it's important to understand that an ONEX node is conceptually viewed as a **function** defined by metadata (`.onex`). M0 tasks involve creating stubs that support the discovery and basic handling of this metadata structure, which includes fields related to the node's type, interfaces, and dependencies.

For a full explanation of the ONEX Node as a Function model, including Pure vs Impure nodes, Reducers, State, and Node Typology (Tier 1, 2, 3), please refer to the dedicated Node Architecture documentation series in `docs/nodes/`:
- [ONEX Node Model: Overview](./docs/nodes/index.md)
- [ONEX Node Typology and Execution Model](./docs/nodes/onex_node_typology.md)
- [ONEX Node Model: State and Reducers](./docs/nodes/state_reducers.md)
- [ONEX Node Model: Contracts and Metadata Specification](./docs/nodes/node_contracts.md)
- [ONEX Node Architecture: Structural Conventions](./docs/nodes/onex_structural_conventions.md)
- [ONEX Node Architecture: Protocol Definitions](./docs/nodes/onex_protocol_definitions.md)
- [ONEX Node Architecture: Caching and Composite Nodes](./docs/nodes/caching_and_composite_nodes.md)
- [ONEX Node Architecture: Graph Resolution and Execution Planning](./docs/nodes/graph_resolution.md)
- [ONEX Node Architecture: Sessions and Streaming Architecture](./docs/nodes/sessions_and_streaming.md)
- [ONEX Node Architecture: GraphQL vs ONEX](./docs/nodes/graphql_vs_onex.md)
- [ONEX Node Architecture: Performance, Memory, and Cost](./docs/nodes/performance_memory_and_cost.md)
- [ONEX Developer Guide: Conventions & Best Practices](./docs/nodes/onex_development_process.md)
- [ONEX Node Model: Future Work and Roadmap](./docs/nodes/onex_future_roadmap.md)

---

## 📂 Notes (Milestone 0)

- Milestone 0 unblocks Milestone 1 (schema enforcement and runtime)
- Canonical templates, protocols, and test structure must be complete before beginning Milestone 1
- Bootstrap includes only stubs—not full validation logic
- For full architectural explanations, including Node as Function, Typology, State/Reducers, Caching, Planning, Streaming, etc., refer to the [Node Architecture documentation series in `docs/nodes/`](./docs/nodes/README.md - *Assuming a README in docs/nodes linking everything*)

---

## 🧰 Canonical Templates (Explanation Snippets)

> These code snippets illustrate the *structure* of canonical stubs expected for M0 implementation and are intended to guide contributors. For the full explanation of Canonical Templates, refer to the dedicated documentation: [Canonical Templates](./docs/nodes/onex_templates_scaffolding.md). The actual template *files* reside in `src/omnibase/templates/` and `tests/template/`.

### `src/omnibase/core/registry.py` (Illustrative Stub Snippet)

    ```python
    from omnibase.protocol.registry import RegistryProtocol # Import the protocol

    class SchemaRegistry(RegistryProtocol): # Implement the protocol
        def __init__(self):
            self._schemas = {} # Placeholder for schema storage

        @classmethod
        def load_from_disk(cls):
            # Stub: Placeholder for M1 schema loading logic
            # M0 ensures this method exists and conforms to protocol
            print("Stub: Loading schemas from disk")
            instance = cls()
            # In M0, load the minimal onex_node.yaml and state_contract.json stubs
            # In M1+, load all schemas and register them
            return instance

        @classmethod
        def load_mock(cls):
            # Stub: Placeholder for M1 mock schema loading logic
            # M0 ensures this method exists and conforms to protocol
            print("Stub: Loading mock schemas")
            instance = cls()
            # In M0, add minimal stub data or loaded stub schemas
            return instance

        def get_node(self, node_id: str):
            # Stub: Placeholder for M1 node lookup logic
            # M0 ensures this method exists and conforms to protocol
            print(f"Stub: Getting node {node_id}")
            # In M0, return a minimal stub dict that allows tests to pass basic assertions
            # Include placeholders for key fields the validator stub will read
            return {
                "name": node_id,
                "stub": True,
                "schema_version": "0.1.0", # Include key fields from the spec
                "uuid": "stub-uuid-123",
                "meta_type": "tool",
                "entrypoint": {"type": "python", "target": "stub.py"},
                "state_contract": "stub://contract.json",
                "dependencies": [],
                "base_class": [],
                # Include placeholders for optional/future fields the validator stub expects
                "reducer": None,
                "cache": None,
                "performance": None,
                "trust": None,
                "x-extensions": {},
                "protocols_supported": [],
                "environment": [],
                "license": "stub",
            }

    ```

### `src/omnibase/tools/cli_validate.py` (Illustrative Stub Snippet)

    ```python
    import typer
    from typing import Any
    from omnibase.protocol.validate import ProtocolValidate # Import the protocol
    from omnibase.schema.loader import load_onex_yaml # Import schema loader stub
    from omnibase.utils.utils_uri_parser import parse_onex_uri  # Canonical import
    from omnibase.model.model_uri import OnexUriModel
    from omnibase.model.model_enum_metadata import UriTypeEnum
    from omnibase.core.errors import OmniBaseError # Import error base

    class MetadataValidator(ProtocolValidate): # Implement the protocol (stub)
        def __init__(self, schema_registry): # M1+ will inject registry
            # In M0, registry is likely passed in here or accessed globally (stub)
            self.registry = schema_registry # Stub for registry
            # Stub: Placeholder for M1 schema storage/lookup
            self.onex_schema = {} # Stub for ONEX schema
            print("Stub: Initializing MetadataValidator")

        def validate(self, path: str) -> bool:
            # Stub: Placeholder for M1 validation logic
            # M0 stub validates basic file loading and reading key fields
            print(f"Stub: Validating .onex file at {path}")

            try:
                # Stub: Load and parse the .onex file using the schema loader stub
                onex_data = load_onex_yaml(path) # Use schema loader stub

                # Stub: Read and acknowledge *all* key canonical fields
                schema_version = onex_data.get('schema_version')
                name = onex_data.get('name')
                version = onex_data.get('version')
                uuid = onex_data.get('uuid')
                description = onex_data.get('description')
                state_contract = onex_data.get('state_contract')
                entrypoint = onex_data.get('entrypoint')
                namespace = onex_data.get('namespace')
                meta_type = onex_data.get('meta_type')
                runtime_language_hint = onex_data.get('runtime_language_hint')
                tags = onex_data.get('tags')
                trust_score_stub = onex_data.get('trust_score_stub')
                x_extensions = onex_data.get('x-extensions')
                protocols_supported = onex_data.get('protocols_supported', [])
                base_class = onex_data.get('base_class', [])
                dependencies = onex_data.get('dependencies', [])
                environment = onex_data.get('environment')
                license = onex_data.get('license')
                reducer = onex_data.get('reducer') # Placeholder for future field
                cache = onex_data.get('cache') # Placeholder for future field
                performance = onex_data.get('performance') # Placeholder for future field
                trust = onex_data.get('trust') # Placeholder for future field


                print(f"Stub: Read schema_version: {schema_version}")
                print(f"Stub: Read name: {name}")
                print(f"Stub: Read meta_type: {meta_type}")
                print(f"Stub: Read state_contract: {state_contract}")
                print(f"Stub: Read dependencies: {dependencies}")
                print(f"Stub: Read base_class: {base_class}")
                print(f"Stub: Read reducer (future): {reducer}")
                # ... print other fields as needed for verification ...


                # Stub: Parse URIs using the canonical parser utility
                for dep_uri in dependencies + base_class:
                    parsed_uri = parse_onex_uri(dep_uri)  # Returns OnexUriModel
                    print(f"Stub: Parsed URI: {dep_uri} -> {parsed_uri}")
                    # M1+ would validate against registry/format

                # Stub validation logic (M1+ will do full schema validation)
                # M0 checks for file loading and basic field access
                if not onex_data or not isinstance(onex_data, dict):
                     raise OmniBaseError("Stub validation failed: Could not load .onex data")
                if 'schema_version' not in onex_data: # Basic stub check
                     raise OmniBaseError("Stub validation failed: Missing schema_version")

                print("Stub: .onex validation logic placeholder passed")
                return True # Stub success

            except Exception as e:
                # Use error base for predictable failure
                raise OmniBaseError(f"Stub .onex validation failed: {e}")


    # Typer CLI command stub
    app = typer.Typer()

    @app.command()
    def validate(path: str = typer.Argument(..., help=".onex file path to validate.")):
        # In M0, validator stub is instantiated and called
        # M1+ will handle dependency injection of registry etc.
        print(f"Stub: onex validate command called for {path}")
        # Instantiate validator stub (M0 does simple instantiation)
        validator_stub = MetadataValidator(schema_registry=None) # Pass stub registry or None in M0
        try:
            validator_stub.validate(path)
            print("Stub: Validation successful (M0 placeholder)")
        except OmniBaseError as e:
            print(f"Stub: Validation failed (M0 placeholder): {e}")
            raise typer.Exit(code=1)

    # Example usage in cli_main.py:
    # from .cli_validate import app as validate_app
    # cli_app = typer.Typer()
    # cli_app.add_typer(validate_app, name="validate")
    # ... add other tool apps
    # if __name__ == "__main__":
    #     cli_app()
    ```

### `src/omnibase/utils/utils_uri_parser.py` (Illustrative Stub Snippet)

    ```python
    import re
    from omnibase.core.errors import OmniBaseError # Import error base

    # Canonical URI format regex (example)
    # Ensure this regex matches the format defined in Node Contracts and Metadata
    URI_PATTERN = re.compile(r"^(tool|validator|agent|model|schema|plugin)://([^@]+)@(.+)$")

    def parse_uri(uri_string: str) -> dict:
        # Stub: Placeholder for M1 URI parsing logic
        print(f"Stub: Parsing URI: {uri_string}")
        match = URI_PATTERN.match(uri_string)
        if not match:
            raise OmniBaseError(f"Stub URI parsing failed: Invalid format for {uri_string}")

        uri_type, namespace, version_spec = match.groups()
        print(f"Stub: Parsed: Type={uri_type}, Namespace={namespace}, Version={version_spec}")

        # In M0, just return the parsed components.
        # M1+ would add more robust validation and potentially dereferencing lookup stubs against a registry.
        return {
            "type": uri_type,
            "namespace": namespace,
            "version_spec": version_spec,
            "original": uri_string # Keep original for reference
        }

    # Add other utility functions...
    ```

---

## 📂 Notes (Milestone 0)

- Milestone 0 unblocks Milestone 1 (schema enforcement and runtime)
- Canonical templates, protocols, and test structure must be complete before beginning Milestone 1
- Bootstrap includes only stubs—not full validation logic
- For full architectural explanations, including Node as Function, Typology, State/Reducers, Caching, Planning, Streaming, etc., refer to the [Node Architecture documentation series in `docs/nodes/`](./docs/nodes/README.md - *Assuming a README in docs/nodes linking everything*)

---

> **Note:** The URI parser utility is protocol-ready for M1+ and uses canonical Enum and Pydantic model types. See src/omnibase/utils/utils_uri_parser.py, model/model_uri.py, and model/model_enum_metadata.py for details.
