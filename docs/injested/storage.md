# OmniBase Storage & Artifact Protocols

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase uses content-addressable storage (CAS) to manage all artifacts. This ensures referential integrity, deduplication, traceability, and deterministic retrieval. Artifacts are immutable and versioned via digests.

---

## Key Concepts

| Term         | Definition                                                                 |
|--------------|----------------------------------------------------------------------------|
| **Artifact** | Any serialized input/output unit (e.g., files, metadata blocks, datasets) |
| **Digest**   | A SHA256 or BLAKE3 hash of the content, used as the unique key            |
| **CAS**      | Storage system keyed by content digests, supporting immutability          |
| **Retention**| Policies governing GC behavior, e.g. based on tags or usage               |

---

## Storage Model

- Artifacts are stored under `artifacts/` in the file system or database
- Keys are SHA256 or BLAKE3 digests of the serialized content
- Registry metadata points to artifact digests
- Artifact types include:
  - `FileArtifact`
  - `DirectoryTreeArtifact`
  - `MetadataBlockArtifact`
  - `SerializedModelArtifact`
  - `NotebookArtifact`

---

## Storage Abstraction

```python
class ArtifactStorage(ABC):
    def get(self, digest: str) -> bytes: ...
    def put(self, content: bytes) -> str: ...
    def has(self, digest: str) -> bool: ...
    def delete(self, digest: str) -> None: ...
```

---

## Artifact Lifecycle

1. Created during tool/validator execution
2. Stored in CAS and assigned a digest
3. Referenced via metadata or returned in result object
4. Optionally retained in registry root set

---

## Sample Result Reference

```json
{
  "output": {
    "summary": "Headers inserted",
    "artifact_ref": "sha256:deadbeef...",
    "produced_at": "2025-05-12T14:20:00Z"
  }
}
```

---

## CAS Implementation Notes

- Root directory is configured via `config.storage_root`
- Filesystem structure may be flattened or sharded (e.g. `ab/cd/abcd1234...`)
- Checksum integrity is validated on every retrieval
- Supports fast existence checks and lazy loading

---

## Garbage Collection (Mark-and-Sweep)

- Registry metadata forms the root set
- Unreferenced digests older than retention threshold are deleted
- Tags like `retain: always` can prevent GC

---

## Planned Enhancements

- [ ] Metadata-aware `omnibase gc` CLI with dry-run mode
- [ ] Artifact lineage graph export
- [ ] Remote artifact syncing and caching
- [ ] Partial tree storage for diff/patch optimization

---

> No artifact left behind—unless you told it to expire.