<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: CHANGELOG.md -->
<!-- version: 1.0.0 -->
<!-- uuid: c3662c9f-f517-462a-861a-9e1a212bb3cd -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.155253 -->
<!-- last_modified_at: 2025-05-21T16:42:46.083347 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: ab2c7d7fc4c18181b3e7b5999c5242f48d4444624e2d5eaa64de8b1a9394bfbd -->
<!-- entrypoint: {'type': 'python', 'target': 'CHANGELOG.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.CHANGELOG -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: CHANGELOG.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 76ab6c9a-e187-4018-8af8-5570807332ff -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.430251 -->
<!-- last_modified_at: 2025-05-21T16:39:55.685548 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: dfa31c2af44cd2e8f3e67d4be1f8c4e357388743a8fdcd6742e49d6d33c15045 -->
<!-- entrypoint: {'type': 'python', 'target': 'CHANGELOG.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.CHANGELOG -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: CHANGELOG.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 5a3fee26-7d98-4da4-b3d9-0ce5ac695b6c -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.658448 -->
<!-- last_modified_at: 2025-05-21T16:24:00.332852 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 3dd930d33497bcc65ac3dd4e572c79593f95b88eed47ed7247247cf37e62a54e -->
<!-- entrypoint: {'type': 'python', 'target': 'CHANGELOG.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.CHANGELOG -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

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
