<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: pr_description_2025_05_20_pr16.md -->
<!-- version: 1.0.0 -->
<!-- uuid: f5e40b14-b601-4c53-9652-1af9aa77bd9c -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.156650 -->
<!-- last_modified_at: 2025-05-21T16:42:46.076967 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: b02dce617635d123d496e834a407e4a68b8c9ee2ce37e0878e7299293771ba7f -->
<!-- entrypoint: {'type': 'python', 'target': 'pr_description_2025_05_20_pr16.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.pr_description_2025_05_20_pr16 -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: pr_description_2025_05_20_pr16.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 32c1e72a-e95f-4a3e-a96e-625601bac417 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.431698 -->
<!-- last_modified_at: 2025-05-21T16:39:55.881201 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: e69240f369328bc22069579178d28241cce1c70f5ce9454a6a6cc862879f0190 -->
<!-- entrypoint: {'type': 'python', 'target': 'pr_description_2025_05_20_pr16.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.pr_description_2025_05_20_pr16 -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: pr_description_2025_05_20_pr16.md -->
<!-- version: 1.0.0 -->
<!-- uuid: bd88b21f-4eb8-4555-96ec-7ac6410ed195 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.659955 -->
<!-- last_modified_at: 2025-05-21T16:24:00.389961 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 42f1a59f91e006bb23dc682f2ccbb7e6434f0f6f40fae68ce53e0c8654b3ce98 -->
<!-- entrypoint: {'type': 'python', 'target': 'pr_description_2025_05_20_pr16.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.pr_description_2025_05_20_pr16 -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

```yaml
=== OmniNode:Metadata ===
metadata_version: 0.1.0
schema_version: 1.1.0
uuid: 38CA7B2A-A438-40C8-A5C0-19B9EC8CDB18
name: pr_description_2025_05_20_pr16.md
version: 1.0.0
author: jonahgabriel
created_at: 2025-05-20T12:44:56-04:00
last_modified_at: 2025-05-20T12:44:56-04:00
description: PR description for PR 16
state_contract: none
lifecycle: active
hash: 7f83a61d2f277a8906759b8a21dee153e5356105
entrypoint: {'type': 'markdown', 'target': 'pr_description_2025_05_20_pr16.md'}
namespace: onex.dev_logs.pr.pr_description_2025_05_20_pr16.md
meta_type: pr_description
=== /OmniNode:Metadata ===
```

# Milestone 1: Standards, Idempotency, and PR Description Automation

- **Branch:** feat-milestone1-wrap-up → main
- **PR ID or Link:** 16 (https://github.com/OmniNode-ai/omnibase/pull/16)

## Summary of Changes
This PR completes Milestone 1: refactors the ONEX metadata stamping system for idempotency, unifies result models and handler registry, and automates PR description logging with full standards compliance.

## Key Achievements
- **Stamper/Engine:**
  - Refactored for idempotency using mtime and hash checks
  - Canonical delimiters and handler-based stamping
  - Info-level logging for idempotency and dirty-check logic
- **Model & Enum Unification:**
  - Unified all code to use canonical `OnexResultModel` and `OnexStatus` enum from a single source
  - Deleted legacy/duplicate model and enum definitions
  - Updated all imports and usages to ensure protocol and typing compliance
- **Handler Registry & CLI:**
  - Refactored CLI and engine to use `FileTypeHandlerRegistry`
  - Delegated stamping to handler for each file
  - Improved error handling and summary reporting
- **Testing:**
  - Updated all tests to use protocol-compliant dummy handlers
  - Fixed test suite for new protocol behaviors and enum usage
  - All tests and type checks (`pytest`, `mypy`, `ruff`, `black`, `isort`) pass
- **Pre-commit Workflow:**
  - Removed `--fix` from Ruff in pre-commit config
  - Documented robust manual workflow for linting/formatting
  - All pre-commit hooks now pass cleanly
- **Interface & Typing Compliance:**
  - All interfaces use `Protocol` or `ABC` as per project rules
  - All protocol methods use Pydantic models and Enums for arguments/returns
  - No primitive types for domain-specific data

## File-by-File Impact (Optional)
- `.cursor/rules/pr_description.mdc`: Updated rule for PR description logging and stamping
- `src/omnibase/templates/dev_logs/template_pr_description.md`: Canonical PR description template
- `src/omnibase/handlers/handler_markdown.py`, `metadata_block_mixin.py`, `handler_metadata_yaml.py`, `handler_python.py`: Refactored for idempotency, handler registry, and protocol compliance
- `src/omnibase/model/model_node_metadata.py`: Unified result model and enum, removed duplication, updated imports
- `src/omnibase/tools/cli_stamp.py`, `stamper_engine.py`: Updated for new handler registry and error handling
- `.pre-commit-config.yaml`: Removed auto-fix from Ruff, ensured idempotent workflow
- All test files: Updated for protocol-compliant handlers and enum usage

## Metrics
- **Files Changed:** 29
- **Lines Added:** 1477
- **Lines Removed:** 1115
- **Lines Changed:** +1477 / -1115
- **Time Spent:** N/A

## Compliance & Quality (Optional)
- Follows `typing_and_protocols` and `interface_design_protocol_vs_abc` rules
- All tests, type checks, and pre-commit hooks pass
- No known blockers; ready for review and merge

## Reviewer Notes (Optional)
- This is a foundational refactor for maintainability and extensibility
- All breaking changes are documented; migration is automatic for all internal code
- Please review handler, CLI, and model changes for protocol and typing clarity

## Prompts & Actions (Chronological)
- [2025-05-20T05:30:43-04:00] removed .stamperignore legacy handling (id: 2b5314e, author: "jonahgabriel")
- [2025-05-20T12:33:36-04:00] fix(cli): remove unused logger from directory command (ruff F841) (id: 5b2f8fc, author: "jonahgabriel")
- [2025-05-20T12:42:55-04:00] PR descriptions. (id: 7f83a61, author: "jonahgabriel")

## Major Milestones
- Idempotent, handler-driven stamping engine
- Unified result model across codebase
- Robust, non-looping pre-commit workflow
- All tests and linters pass

## Blockers / Next Steps
- None known; ready for review and merge

## Related Issues/Tickets (Optional)
- None

## Breaking Changes (Optional)
- None

## Migration/Upgrade Notes (Optional)
- None

## Documentation Impact (Optional)
- None required beyond inline doc updates

## Test Coverage (Optional)
- All relevant tests updated; all pass

## Security/Compliance Notes (Optional)
- None

## Reviewer(s) (Optional)
- None

## Release Notes Snippet (Optional)
- Refactored ONEX metadata stamper for idempotency, unified result model, improved handler registry, and fixed pre-commit workflow.
