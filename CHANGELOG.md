<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: d072ed98-3e9e-47a7-8c87-8d4aa966997d -->
<!-- name: CHANGELOG.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:00.544689 -->
<!-- last_modified_at: 2025-05-19T16:20:00.544696 -->
<!-- description: Stamped Markdown file: CHANGELOG.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: dc8b676d6292cf0828c80ee20d7d8e4b870f0b026983ed418350d40ca044a264 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'CHANGELOG.md'} -->
<!-- namespace: onex.stamped.CHANGELOG.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# OmniBase / ONEX – CHANGELOG

All notable changes to this project will be documented in this file. This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format and is intended for contributors and users of the open source OmniBase/ONEX project.

---

## [Unreleased]
- Project is in active foundational development. See [docs/milestones/overview.md](docs/milestones/overview.md) for roadmap and planned features.

## [v0.1.0] – Milestone 0: Bootstrap (2025-05-19)
### Added
- Canonical directory structure and packaging (PEP 517/518, Poetry)
- Protocol definitions and registry stubs for ONEX node model
- CLI entrypoint (`onex`) and protocol-compliant CLI tools
- Canonical templates for node metadata, CLI, and test scaffolding
- Canonical test suite: registry-driven, markerless, fixture-injected, protocol-first
- Error taxonomy and base error class (`OmniBaseError`)
- Example schemas and loader with YAML/JSON support
- Documentation: architecture, onboarding, testing philosophy, and milestone checklist
- Velocity log automation and PR description tooling

### Changed
- Migrated legacy code to `legacy/` (now removed from history for open source release)
- Updated all documentation and templates to match canonical ONEX standards

### Removed
- All sensitive/internal files and legacy code from repository and git history

### References
- See [docs/dev_logs/](docs/dev_logs/) for detailed velocity logs
- See [docs/milestones/milestone_0_checklist.md](docs/milestones/milestone_0_checklist.md) for full implementation checklist

---

## [Upcoming]
- Milestone 1: Validation engine, registry, and execution runtime
- Milestone 2: Planning, caching, trust, and composite graph support
- Milestone 3+: Federation, P2P, and interop

For more details, see the [project roadmap](docs/milestones/overview.md). 
