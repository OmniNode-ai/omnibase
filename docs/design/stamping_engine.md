# ONEX Stamping Engine: Canonical Design

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the canonical design for the ONEX stamping engine  
> **Audience:** System architects, developers, node authors  
> **Companion:** [Handler Protocols](../reference-handlers-protocol.md), [Handler Registry](../reference-handlers-registry.md), [Metadata Specification](../metadata.md)

---

## Overview

The ONEX stamping engine is responsible for orchestrating the extraction, insertion, updating, and validation of canonical metadata blocks in supported file types (Python, YAML, Markdown, JSON, etc.). The engine ensures idempotency, hash stability, and protocol compliance across all file types. All block extraction, parsing, and formatting are orchestrated by the engine, but actual extraction, serialization, and deserialization are delegated to the handler, which serves as the single source of file-type truth. There is no ambiguity or "optional" extraction: the handler is always invoked for file-type-specific logic, and the engine coordinates all stamping protocol and normalization.

---

## Design Principles

- **Single Source of Truth:** All stamping, idempotency, hash logic, normalization, and protocol compliance are centralized in the engine.
- **Separation of Concerns:** Handlers are responsible only for file-type-specific serialization, deserialization, extraction, and validation, and are the sole source of file-type truth.
- **Extensibility:** New file types can be supported by registering new handlers.
- **Testability:** All core logic is unit tested in isolation; handlers are simple and easy to test.
- **Reusability:** Extractors and serializers are shared utilities, used by validators and other tools.

---

## Engine Responsibilities

- Orchestrate the extraction of all metadata blocks from the file by invoking the handler's file-type-specific extractor.
- Parse previous metadata using the handler's deserialization logic.
- Enforce canonical serialization and normalization of all content (including newlines, whitespace, YAML/JSON representation) according to the protocol.
- Compute the canonical hash and determine if the file is "dirty" (content changed).
- Decide whether to update `last_modified_at` and `hash`.
- Call the handler for file-type-specific serialization (comment prefix, delimiters, etc.).
- Return the canonical stamped content and metadata.
- Migrate all files to the canonical format as the expected standard.

---

## Normalization Guarantees

The engine enforces canonical serialization and normalization of whitespace, newlines, and formatting for both the metadata block and the rest of the file. This includes normalization of YAML/JSON representations, standardization of line endings, and removal of extraneous whitespace as defined by the protocol. While the engine is responsible for enforcing these guarantees, handlers may invoke shared canonical utilities provided by the engine for content model serialization, ensuring protocol-compliant output.

---

## Handler Responsibilities

- Provide file-type-specific serialization and deserialization (e.g., YAML, Python comment block), and always act as the single source of file-type truth.
- Provide file-type-specific validation (syntax, schema, etc.).
- Implement file-type-specific block extraction; all extraction, parsing, and formatting for a file type are delegated to the handler, with no ambiguity or optionality.

---

## Engine-Handler Boundary

To maintain clear separation of concerns, all responsibilities for protocol logic, stamping, normalization, and canonicalization are centralized in the engine. The handler is always the sole source of file-type-specific logic, including extraction, serialization, deserialization, and validation. There is no ambiguity: the engine always invokes the handler for extraction, parsing, and formatting, and never attempts file-type-specific logic itself. The engine enforces all canonical normalization and protocol guarantees, while handlers may invoke canonical serialization utilities for the content model as needed. This ensures the engine remains the single authority for protocol compliance, and the handler remains the single authority for file-type specifics.

---

## Canonical Extractor/Serializer Utilities

> **Note:** These utilities are common, shared tools used by handlers for tasks such as canonical serialization/deserialization of the metadata content model itself (e.g., converting a Python dict to canonical YAML/JSON). They are **not** tools used by the engine for file-type-specific block extraction or formatting. The engine never directly performs file-type-specific parsing or formatting; it always delegates such responsibilities to the handler, which may leverage these utilities to ensure protocol-compliant output.

- **Extractor:**
  - The engine invokes the handler's file-type-specific extractor to extract and parse metadata blocks from any supported file type.
  - Returns: (metadata, rest_of_file_content)
- **Serializer:**
  - The engine invokes the handler's serializer to convert a metadata model into the correct block format for a given file type.
  - Handlers may use canonical serialization utilities provided by the engine to ensure protocol-compliant output for the content model, but all file-type-specific formatting and extraction remain the responsibility of the handler.

---

## Canonical Hashing Algorithm

The canonical hashing algorithm is strictly defined to ensure stable, protocol-compliant hashes across all file types and stamping operations:

- **Hash Computation Steps:**
  1. **Normalize the Rest of the File:** Remove the metadata block and normalize the rest of the file content according to protocol requirements (including whitespace, line endings, and structural normalization).
  2. **Serialize the Metadata Block:** Serialize the metadata block using the handler, but with protocol-defined placeholders for volatile fields:
     - The `hash` field is replaced with a fixed protocol placeholder.
     - The `last_modified_at` field is replaced with a protocol placeholder or canonical value.
     - All serialization and normalization (such as YAML/JSON formatting, whitespace, newlines) must conform to protocol rules and are enforced by the engine.
  3. **Concatenate and Hash:** Concatenate the canonical serialized metadata block and the normalized rest of the file. Apply the protocol hash function (e.g., SHA-256) to this concatenated, canonicalized content.

- **Rationale:**
  - This approach ensures that the hash reflects the true content and metadata state, ignoring only those fields that change as a result of stamping.
  - Guarantees idempotency and stability of the hash across multiple stamping operations.
  - Prevents false positives for content changes triggered solely by metadata updates.

---

## Unified Stamping Pipeline

1. **Extract** all metadata blocks and the rest of the file.
2. **Parse** the previous metadata.
3. **Compute** the hash using the previous `last_modified_at` and a placeholder hash.
4. **If not dirty:** reuse previous `last_modified_at` and hash.
5. **If dirty:** update both.
6. **Call handler** to serialize the block and reassemble the file.

---

## Extensibility & Pluggability

- Handlers can be registered for new file types (Markdown, JSON, etc.).
- Extractors and serializers are reusable by validators, linters, and other tools.
- ONEX only supports canonical, protocol-compliant metadata blocks and does not support non-standard or legacy block formats.
- The engine can be extended for new stamping protocols or block formats that adhere strictly to the canonical specification.

---

## Migration Plan

1. Refactor the engine to own all stamping/idempotency logic.
2. Refactor handlers to only provide serialization/validation.
3. Migrate all tests to use the new engine-driven pipeline.
4. Migrate all files to the canonical format as the expected standard.
5. Add/expand tests for edge cases and new file types.

---

## Rationale

- **No more drift:** All handlers behave identically.
- **Easier to test:** One place to fix bugs, one place to add new file types.
- **Extensible:** New file types can be added with minimal code.
- **Protocol compliance:** All stamping is guaranteed to follow the canonical protocol.
- The single-format approach ensures stronger guarantees, eliminates edge case drift, and maximizes maintainability and testability.

---

## Handling Malformed or Non-Canonical Blocks

To maintain strict protocol compliance, the engine always attempts to normalize or replace a malformed or non-canonical block with a canonical block if the metadata is parseable. If the metadata block is not parseable, the engine aborts the operation and reports a clear, actionable error—silent ignoring is never allowed. The handler is responsible for validating file-type-specific syntax and schema and must report detailed errors for malformed content. The engine enforces that only protocol-compliant metadata blocks are stamped and maintained, and all normalization or recovery is explicit and reported.

---

## Validation Responsibilities

All block validation (including syntax, placement, and uniqueness) is always performed before stamping, and failure to validate blocks aborts the operation. Validation is a layered responsibility:

- **Handler Validation:**
  - Perform file-type-specific syntax checks (e.g., YAML schema validation, comment block correctness).
  - Validate metadata schema and field types as per file-type requirements.
  - Report detailed validation errors related to the file format or block structure.

- **Engine Validation:**
  - Enforce protocol-level validation rules (e.g., presence of required metadata fields, canonical formatting, uniqueness, and block placement).
  - Validate hash and timestamp consistency.
  - Ensure idempotency and normalization guarantees are met.

Stamping is aborted on any validation failure. There is no silent failure or partial stamping. This strict validation strategy ensures robust stamping and metadata integrity across all supported file types.

---

## Protocol Interfaces

### Handler Protocol

```python
from typing import Protocol, Optional, Tuple
from pathlib import Path

class ProtocolFileTypeHandler(Protocol):
    """Protocol for file type handlers in the stamping engine."""
    
    def serialize_block(self, meta: "NodeMetadataBlock") -> str:
        """Serialize metadata block to file-type-specific format."""
        ...
    
    def extract_block(self, path: Path, content: str) -> Tuple[Optional["NodeMetadataBlock"], str]:
        """Extract metadata block and return (metadata, rest_of_content)."""
        ...
    
    def validate(self, path: Path, content: str, **kwargs) -> "OnexResultModel":
        """Validate file content and metadata block."""
        ...
    
    def can_handle(self, path: Path, content: str) -> bool:
        """Determine if this handler can process the given file."""
        ...
```

### Engine API

```python
from typing import Protocol
from pathlib import Path

class StampingEngineProtocol(Protocol):
    """Protocol for the ONEX stamping engine."""
    
    def stamp_file(self, path: Path, content: str, handler: ProtocolFileTypeHandler) -> "OnexResultModel":
        """Stamp a single file with metadata."""
        ...
    
    def stamp_directory(self, directory: Path, **options) -> "OnexResultModel":
        """Stamp all eligible files in a directory."""
        ...
    
    def validate_file(self, path: Path, content: str) -> "OnexResultModel":
        """Validate file metadata and content."""
        ...
```

---

## Handler Discovery and Registry

Handlers are managed via a centralized registry to support extensibility and pluggability:

### Registration

- Handlers register themselves with the engine by associating a file type or extension with a handler instance.
- Registration can occur at runtime or during initialization.

### Discovery

- The engine queries the registry to find the appropriate handler based on file type or extension.
- This allows dynamic support for new file types without modifying the core engine.

### Usage

- The stamping pipeline retrieves the handler from the registry before processing a file.
- If no handler is registered for a file type, stamping is skipped or an error is raised.

This registry pattern simplifies handler management and promotes modularity.

---

## CLI Integration

The stamping engine integrates with the ONEX CLI for user-facing operations:

### Basic Commands

```bash
# Stamp individual files
onex stamp file path/to/file.py
onex stamp file **/*.py

# Stamp directories
onex stamp directory src/

# Validate stamped files
onex validate path/to/file.py

# List available handlers
onex handlers list
```

### Advanced Usage

```bash
# Stamp with specific handler
onex stamp file --handler python path/to/file.py

# Dry run mode
onex stamp file --dry-run path/to/file.py

# Verbose output
onex stamp file --verbose path/to/file.py

# Force re-stamping
onex stamp file --force path/to/file.py
```

---

## Implementation Checklist

### 1. Define Protocols and Canonical Constants
- [ ] Create `ProtocolFileTypeHandler` interface
- [ ] Centralize all block delimiters, config keys, and constants
- [ ] Define canonical `MetadataModel` (Pydantic)

### 2. Implement Canonical Engine
- [ ] Implement engine with directory traversal, ignore logic, handler dispatch, and idempotency
- [ ] Implement canonical hash computation and dirty-checking as defined in the Canonical Hashing Algorithm section
- [ ] Add structured logging and debug mode

### 3. Implement Handler Registry
- [ ] Implement registry mapping extensions/roles to handlers
- [ ] Add debug logging for ignored/unsupported file types

### 4. Implement File Type Handlers
- [ ] Implement `MetadataYAMLHandler`
- [ ] Implement `PythonHandler`
- [ ] Implement `MarkdownHandler`
- [ ] Implement `JSONHandler`
- [ ] Add additional handlers as needed

### 5. Implement and Validate Ignore Logic
- [ ] Implement ignore logic with `pathspec`
- [ ] Validate and test ignore file ingestion and stamping

### 6. Testing
- [ ] Write unit tests for all handlers, engine, registry, and ignore logic
- [ ] Write integration tests for real directory traversal and CLI
- [ ] Write idempotency, edge case, and hash stability tests
- [ ] All tests for idempotency and canonical normalization must pass before milestone completion

### 7. CLI & API Integration
- [ ] Refactor CLI to use new engine and registry
- [ ] Add strong argument validation and debug output

### 8. Documentation
- [ ] Update design doc and user-facing docs
- [ ] Document all constants, protocols, and usage patterns

### 9. Migration & Cleanup
- [ ] Remove all legacy/obsolete code and tests
- [ ] Update test fixtures and documentation to match new architecture

### 10. Review & Finalization
- [ ] Review implementation for protocol compliance, maintainability, and test coverage
- [ ] Address all open questions and edge cases
- [ ] Ensure all idempotency and canonical normalization tests pass
- [ ] Prepare for next milestone or feature extension

---

## Additional Considerations

### Edge Cases
- Malformed files, partial writes, concurrent runs, and invalid ignore patterns must be handled gracefully and never silently ignored.
- Ensure idempotency and hash stability even in the presence of file system anomalies.

### Extensibility
- Handlers must be easily pluggable for new file types or stamping protocols.
- Consider supporting pre/post-processing hooks or pluggable extractors if future requirements demand.

### Observability
- All actions, errors, and ignored file types must be logged in debug mode.
- Structured logging should support both CLI and programmatic consumption.

### Error Handling
- Use a canonical error reporting format for both engine and handlers.
- Clear distinction between recoverable and fatal errors.

### Versioning & Schema Evolution
- Plan for versioning of the metadata model and migration strategies for stamped files.

### Security
- Validate and sanitize all file inputs and metadata to prevent injection or corruption.

### Performance
- Consider performance implications for large directories or files; support batch and incremental stamping if needed.

### Protocol Compliance
- All stamping, extraction, and validation must strictly adhere to the ONEX protocol and node model, with the engine as the single source of protocol truth and the handler as the single source of file-type truth.

---

## References

- [Handler Protocols](../reference-handlers-protocol.md)
- [Handler Registry](../reference-handlers-registry.md)
- [Handler Implementation](../guide-handlers-implementation.md)
- [Metadata Specification](../metadata.md)
- [Core Protocols](../reference-protocols-core.md)
- [Registry Protocols](../reference-protocols-registry.md)
- [Data Models](../reference-data-models.md)
- [CLI Interface](../cli_interface.md)
- [Error Handling](../error_handling.md)

---

**Note:** The ONEX stamping engine provides the foundation for reliable, consistent metadata management across all supported file types. The protocol-driven design ensures extensibility while maintaining strict compliance with ONEX standards. 