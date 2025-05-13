# Milestone 06 – Artifact Storage Abstraction (Content‑Addressable Store)

> **Owner:** core‑storage squad
> **Status:** Planned
> **Target version:** v0.6.0
> **Time‑box:** 2 calendar weeks (estimate)

## 1 · Description

Design and implement the first‑pass artifact storage layer that underpins OmniBase.  The layer must expose a small, protocol‑first interface that supports:

* deterministic, content‑addressable digests (SHA‑256)
* pluggable back‑ends (local FS + S3 as reference implementations)
* streaming read/write (≥ 1 GiB artifact support without full memory load)
* basic garbage‑collection driven by registry root‑set
* sync **and** async invocation paths

## 2 · Acceptance Criteria

* An `ArtifactStore` **ABC & Protocol** defined under `core.storage.base` with at least:

  * `put(data_stream) -> Digest`
  * `get(digest) -> IO[bytes]`
  * `stat(digest) -> ArtifactMeta`
  * async equivalents (`async_put`, `async_get`)
* **LocalStore** implementation (hash‑fan‑out directory layout, configurable root dir).
* **S3Store** implementation (uses boto3, bucket & prefix configurable at runtime).
* CLI commands:

  * `omnibase artifact push <path>` – returns digest
  * `omnibase artifact pull <digest> --output <path>`
  * `omnibase artifact gc --dry‑run` – prints reclaimable space, honours retention flags.
* Unit + integration tests covering 95 % of paths (streaming, large files, network error simulation).
* Documentation in `docs/storage/` explaining CAS design & GC policy.

## 3 · Deliverables

| Item                           | Location                                               |
| ------------------------------ | ------------------------------------------------------ |
| `ArtifactStore` ABC & Protocol | `core/storage/base.py`, `protocols/testing/storage.py` |
| LocalStore impl                | `core/storage/local_store.py`                          |
| S3Store impl                   | `core/storage/s3_store.py`                             |
| CLI sub‑commands               | `cli/commands/artifact.py`                             |
| GC job                         | `core/storage/gc.py` & scheduler wiring                |
| Docs                           | `docs/storage/cas_overview.md`                         |
| Tests                          | `tests/storage/`                                       |

## 4 · Dependencies

* **Milestone 01** – Core Protocol definitions (base ABC/Protocol scaffolding).
* **Milestone 02** – Registry MVP (root‑set extraction for GC).
* **Milestone 05** – Capability security model (FILE\_READ / FILE\_WRITE / NETWORK\_CONNECT permissions for store back‑ends).

## 5 · Timeline (high‑level)

| Week | Goals                                                                     |
| ---- | ------------------------------------------------------------------------- |
|  1   | Interface design → code review → LocalStore implementation → smoke tests  |
|  2   | S3Store + CLI wiring → GC job → docs → full test suite → milestone review |

## 6 · Risks & Mitigations

* **Large artifacts** – ensure streaming API & chunked S3 uploads ➜ enforce max chunk size.
* **Data loss** – write‑after‑write hash verification + S3 versioning enabled.
* **GC false‑positives** – dry‑run mode + retention tag support in metadata before destructive sweep.
