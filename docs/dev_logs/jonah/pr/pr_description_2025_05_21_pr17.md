<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: pr_description_2025_05_21_pr17.md
version: 1.0.0
uuid: 5622d634-2dea-4d17-9805-51392ca505de
author: OmniNode Team
created_at: 2025-05-28T12:40:26.092932
last_modified_at: 2025-05-28T17:20:05.138717
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: d10f18d1f42c3bfc30a337f039853e8c9ef2700c7d168c99068ae2f1f9940cb0
entrypoint: python@pr_description_2025_05_21_pr17.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.pr_description_2025_05_21_pr17
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# PR Title
Update CLI Documentation for Formatter Registry and Protocol-Driven Tools

## Branch
doc-updates → main

## PR ID or Link
PR #17

## Summary of Changes
This PR updates the documentation to reflect recent changes to the CLI interface, formatter registry, and protocol-driven tools like the stamper. It incorporates improvements for dry-run safety, idempotency, and handler-based architecture.

## Key Achievements
- **CLI Interface Documentation**
  - Updated `docs/cli_interface.md` to reflect formatter registry enhancements
  - Added details about protocol-driven and fixture-injectable architecture
  - Updated documentation on safer CLI defaults with dry run mode
  - Improved examples of output formatting with detailed message structures
  - Updated status from "Draft" to "Canonical"
  - Added information about custom formatter registration
- **Testing Documentation**
  - Enhanced `docs/testing.md` to include guidance on testing protocol-driven tools
  - Added sections on testing handler-based architectures
  - Added detailed guidance on testing idempotency
  - Included examples for testing dry-run vs. write mode behavior
- **Stamper Tool Documentation**
  - Updated `docs/tools/stamper.md` to reflect the migration from `.stamperignore` to `.onexignore`
  - Clarified that the CLI now requires explicit `--write` flag to modify files
  - Added information about formatter registry and output options

## Prompts & Actions (Chronological)
- 2025-05-21T10:30:00-04:00 [jonahgabriel] Updated docs/cli_interface.md with formatter registry details and protocol-driven architecture
- 2025-05-21T11:15:00-04:00 [jonahgabriel] Enhanced docs/testing.md with protocol-driven testing guidance
- 2025-05-21T11:45:00-04:00 [jonahgabriel] Confirmed docs/tools/stamper.md reflects current CLI safety improvements
- 2025-05-21T12:30:00-04:00 [jonahgabriel] Committed documentation updates
- 2025-05-21T12:45:00-04:00 [jonahgabriel] Created PR description

## Major Milestones
- All CLI-related documentation now aligns with implementation of safer defaults (dry run)
- Testing documentation includes guidance on protocol-driven tools and handler-based architecture
- Documentation reflects migration from `.stamperignore` to `.onexignore`
- Formatter registry and output options are well-documented

## Blockers / Next Steps
- None blocking. Next: Continue implementing the formatter registry and output compression features in codebase

## Metrics
- Lines Changed: "+239 / -35"
- Files Modified: 3
- Time Spent: ~2.5 hours

## Related Issues/Tickets
- None

## Breaking Changes
- None

## Migration/Upgrade Notes
- Users should now use `.onexignore` instead of `.stamperignore` and must explicitly use `--write` flag to modify files with the stamper

## Documentation Impact
- Updated CLI Interface, Testing, and Stamper documentation to reflect current implementation

## Test Coverage
- N/A (documentation only)

## Security/Compliance Notes
- CLI now has safer defaults with dry run mode, preventing accidental file modifications

## Reviewer(s)
- @foundation-team, @onex-maintainers

## Release Notes Snippet
- Updated CLI documentation to reflect formatter registry enhancements, protocol-driven architecture, and safer defaults. Clarified migration from `.stamperignore` to `.onexignore` and added guidance on testing protocol-driven tools and handler-based architectures.
