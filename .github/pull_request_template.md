<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode.ai
schema_version: 1.1.0
name: pull_request_template.md
version: 1.0.0
uuid: dac2573f-039f-42bf-ae82-43f37a9947fd
author: OmniNode Team
created_at: 2025-05-21T13:18:56.539399
last_modified_at: 2025-05-23T13:07:24.490425
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 7b2668f04fed37e2c78d1c61f7fc3d7f1eef418e0ff1ec8bc7ffd5a1bf227cda
entrypoint: python@pull_request_template.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.pull_request_template
meta_type: tool
<!-- === /OmniNode:Metadata === -->

# Pull Request Template

## Description

Brief description of the changes in this PR.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Handler/Plugin addition or modification
- [ ] Node implementation or modification
- [ ] Protocol/Interface changes
- [ ] Test infrastructure changes
- [ ] CI/CD changes

## Handler & Plugin Review Checklist

*Complete this section if your PR adds or modifies handlers, plugins, or related infrastructure.*

### Handler Implementation
- [ ] Handler implements all required metadata properties (`handler_name`, `handler_version`, `handler_author`, `handler_description`, `supported_extensions`, `supported_filenames`, `handler_priority`, `requires_content_analysis`)
- [ ] Handler follows canonical naming conventions (lowercase with underscores)
- [ ] Handler implements all required protocol methods (`can_handle`, `extract_block`, `serialize_block`, `stamp`, `validate`, `pre_validate`, `post_validate`)
- [ ] Handler returns proper types (`OnexResultModel`, `Optional[OnexResultModel]`, etc.)
- [ ] Handler includes comprehensive error handling and graceful degradation

### Handler Placement & Architecture
- [ ] **Core Handler** (Priority 100): Essential system functionality (e.g., `.onexignore`, `.gitignore`)
  - [ ] Justification provided for core placement
  - [ ] No dependencies on external libraries beyond standard library
  - [ ] Critical for system operation
- [ ] **Runtime Handler** (Priority 50): Standard file type support (e.g., `.py`, `.md`, `.yaml`)
  - [ ] Handles common file types in ONEX ecosystem
  - [ ] Well-established, stable functionality
  - [ ] Minimal external dependencies
- [ ] **Node-Local Handler** (Priority 10): Node-specific functionality
  - [ ] Specific to particular node's requirements
  - [ ] Does not conflict with existing handlers
  - [ ] Properly scoped to node directory
- [ ] **Plugin Handler** (Priority 0): Third-party or experimental functionality
  - [ ] Entry point configuration provided
  - [ ] Plugin package structure documented
  - [ ] Installation and usage instructions included

### Testing & Quality
- [ ] Handler has comprehensive test coverage (>90%)
- [ ] Tests follow canonical testing patterns (registry-driven, fixture-injected, protocol-first)
- [ ] Tests include both mock and integration contexts
- [ ] Handler metadata enforcement tests pass
- [ ] All pre-commit hooks pass (black, ruff, mypy, isort, yamllint)
- [ ] Handler is included in CI enforcement pipeline

### Documentation
- [ ] Handler documented in appropriate location (`docs/handlers/`, `docs/plugins/`)
- [ ] Usage examples provided
- [ ] Supported file types and patterns documented
- [ ] Migration guide provided if replacing existing functionality
- [ ] API documentation updated if needed

## Node Implementation Review Checklist

*Complete this section if your PR adds or modifies node implementations.*

### Node Structure
- [ ] Node follows canonical directory structure (`name_type/v1_0_0/`)
- [ ] Required files present (`node.py`, `state_contract.yaml`, `.onex` metadata)
- [ ] Node implements proper entrypoint signature with `handler_registry` parameter
- [ ] Node uses engine pattern for core logic separation
- [ ] Node emits standard events (`NODE_START`, `NODE_SUCCESS`, `NODE_FAILURE`)

### State Contracts & Models
- [ ] Input/output state models are properly defined with Pydantic
- [ ] State contract YAML is valid and complete
- [ ] Schema versioning is implemented
- [ ] All required fields have appropriate types and validation

### Testing
- [ ] Node has comprehensive test coverage
- [ ] Tests use canonical patterns (context-agnostic, fixture-injected)
- [ ] Both unit and integration tests provided
- [ ] CLI/node output parity verified
- [ ] Error handling and edge cases covered

## Protocol & Interface Review Checklist

*Complete this section if your PR modifies protocols or interfaces.*

### Protocol Design
- [ ] Protocol uses `typing.Protocol` (not ABC) for external interfaces
- [ ] Protocol methods have proper type annotations
- [ ] Protocol is documented with clear contract specifications
- [ ] Breaking changes are clearly identified and justified

### Backward Compatibility
- [ ] Changes maintain backward compatibility OR migration path provided
- [ ] Deprecation notices added for removed functionality
- [ ] Version bumping strategy followed

## General Quality Checklist

### Code Quality
- [ ] Code follows project naming conventions and standards
- [ ] All functions and classes have proper docstrings
- [ ] Type annotations are complete and accurate
- [ ] Error handling is comprehensive and follows project patterns
- [ ] No hardcoded values; configuration is externalized

### Testing
- [ ] All tests pass locally
- [ ] Test coverage is maintained or improved
- [ ] Tests follow canonical testing patterns
- [ ] No flaky or unreliable tests introduced

### Documentation
- [ ] README updated if needed
- [ ] Relevant documentation updated
- [ ] Breaking changes documented
- [ ] Migration guides provided where applicable

### CI/CD
- [ ] All CI checks pass
- [ ] Pre-commit hooks pass
- [ ] No new linting or type checking errors
- [ ] Performance impact assessed (if applicable)

## Architectural Review Requirements

*The following changes require architectural review by maintainers:*

- [ ] New protocols or interfaces
- [ ] Changes to core handler registry or plugin system
- [ ] Breaking changes to existing APIs
- [ ] New node types or major node modifications
- [ ] Changes to CI/CD pipeline or testing infrastructure
- [ ] New external dependencies
- [ ] Performance-critical changes
- [ ] Security-related changes

## Testing

Describe the tests you ran to verify your changes. Provide instructions so reviewers can reproduce.

- [ ] Unit tests pass: `poetry run pytest`
- [ ] Integration tests pass: `poetry run pytest -m integration`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] Handler metadata enforcement passes: `poetry run pytest tests/protocol/test_handler_metadata_enforcement.py`
- [ ] Manual testing performed (describe scenarios)

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules

## Additional Notes

Add any other context about the pull request here, including:
- Performance implications
- Security considerations
- Deployment requirements
- Related issues or PRs

## Issue Link

Closes #[issue-number-or-description]

---

Maintainer: OmniNode Core Team  
Checklist Version: YYYY-MM-DD  
See docs/testing.md#amendment-and-feedback-process for change requests.
