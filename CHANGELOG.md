<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: CHANGELOG.md
version: 1.0.0
uuid: 9b9605c5-938b-4a2a-a568-671825370f46
author: OmniNode Team
created_at: 2025-05-22T17:18:16.672842
last_modified_at: 2025-05-22T21:19:13.392077
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b5d9a51011a0cf47a97662236564a8a6cb017b17e7c4f01be143ac93b770f0b7
entrypoint: python@CHANGELOG.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.CHANGELOG
meta_type: tool
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
