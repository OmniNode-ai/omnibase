<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: pr_description_2025_05_23_pr19.md
version: 1.0.0
uuid: dba8b3da-438e-4634-bde1-a051d01b66ad
author: OmniNode Team
created_at: '2025-05-28T12:40:26.112925'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://pr_description_2025_05_23_pr19
namespace: markdown://pr_description_2025_05_23_pr19
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# Canonical Protocols, Stamping, and Ignore Logic Refactor

- **Branch:** feat-stamper-node → main
- **PR ID or Link:** None

## Summary of Changes
This PR implements a comprehensive refactor of protocol interface locations, stamping/metadata idempotency, and canonical ignore logic for test and example YAMLs. It ensures all foundational protocols are in a single canonical package, all imports are robust, and test fixtures are never restamped.

## Key Achievements
- **Protocols & Imports:**
  - Moved all foundational protocol files to `src/omnibase/protocol/`.
  - Updated all imports to use `omnibase.protocol.*`.
  - Added `py.typed` for type safety and mypy compliance.
- **Stamping & Metadata:**
  - Fixed idempotency and corruption issues in the stamping system.
  - Removed all metadata blocks from test/example YAMLs.
  - Ensured only runtime YAML content remains in fixtures/examples.
- **Ignore Logic:**
  - Added canonical `.onexignore` files to all fixture/example directories.
  - Patterns ensure test YAMLs are never restamped.
- **Linting & CI:**
  - All yamllint, ruff, black, isort, and mypy checks pass.
  - Pre-commit hooks now robustly enforce standards.

## File-by-File Impact (Optional)
- `src/omnibase/protocol/`: All protocol interfaces consolidated here.
- `src/omnibase/nodes/stamper_node/tests/fixtures/`, `examples/`: `.onexignore` added, metadata removed from YAMLs.
- `src/omnibase/nodes/stamper_node/node.onex.yaml`, `minimal_example.yaml`, `minimal_stamped_fixture.yaml`: Metadata block removed.

## Metrics
- **Files Changed:** 294
- **Lines Added:** 8617
- **Lines Removed:** 8334
- **Lines Changed:** +8617 / -8334
- **Time Spent:** N/A

## Compliance & Quality (Optional)
- All changes conform to project standards and naming conventions.
- All pre-commit and CI checks pass.

## Reviewer Notes (Optional)
- Focus review on protocol import paths, .onexignore logic, and YAML fixture/test handling.

## Prompts & Actions (Chronological)
- [2025-05-23T07:14:12-04:00] fix the stamping errors (id: 4280ac0, agent: "jonahgabriel")
- [2025-05-22T17:24:54-04:00] Fixed namespace normalization for files with hyphens - All 266 files now stamp successfully - Idempotency working perfectly - Some YAML lint issues remain to be fixed (id: bd2ac05, agent: "jonahgabriel")
- [2025-05-22T17:00:23-04:00] FIXED: Ignore pattern handling in file command - Core fix adds .onexignore checking to onex stamp file - Test file now properly excluded, stamper passes, yamllint passes (id: 22dd22e, agent: "jonahgabriel")
- [2025-05-22T15:06:49-04:00] check in before refactor (id: ac43182, agent: "jonahgabriel")
- [2025-05-22T14:39:55-04:00] fix: Resolve hash computation for new files - Fixed stamp_with_idempotency to compute real hashes for new files instead of using placeholder - New files now get proper computed hashes instead of placeholder zeros - Both Python and Markdown handlers now compute real hashes for new metadata blocks (id: 76f029a, agent: "jonahgabriel")
- [2025-05-21T19:02:48-04:00] Node refactor (id: 3df6b79, agent: "jonahgabriel")
- [2025-05-21T18:48:43-04:00] check in before refactor (id: 1e8fff2, agent: "jonahgabriel")
- [2025-05-21T18:47:57-04:00] check in before refactor (id: a65be88, agent: "jonahgabriel")
- [2025-05-21T17:21:46-04:00] feat(stamper-node): migrate handlers, update docs, add advanced checklist for Canary Node & CLI alignmen (id: 3a63330, agent: "jonahgabriel")

## Major Milestones
- Canonical protocol package established
- All test/example YAMLs are now restamp-proof
- All CI and linting checks pass

## Blockers / Next Steps
- None (ready for review/merge)

## Related Issues/Tickets (Optional)
- None

## Breaking Changes (Optional)
- None

## Migration/Upgrade Notes (Optional)
- None

## Documentation Impact (Optional)
- Docs updated for protocol, stamping, and ignore logic

## Test Coverage (Optional)
- All tests pass; test fixtures are now stable and not restamped

## Security/Compliance Notes (Optional)
- None

## Reviewer(s) (Optional)
- None

## Release Notes Snippet (Optional)
- Canonical protocol refactor, stamping idempotency, and ignore logic for test YAMLs
