# ONEX Node Architecture: Legacy Migration

> **Status:** Canonical  
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting or legacy documentation.

## 12 - Legacy Migration

### Context & Origin

This document outlines the strategy and best practices for migrating code from the legacy Foundation system to the new OmniBase/ONEX architecture. The migration process is guided by the "Node as a Function" model, which informs how legacy components are transformed into well-defined, contract-driven node functions. It addresses the challenge of:

> "How to systematically transform legacy Foundation code into function-oriented ONEX nodes without disrupting ongoing operations."

---

### Migration Strategy Overview

The migration from legacy Foundation to ONEX follows a staged approach, prioritizing foundational components while maintaining backward compatibility.

#### ✅ Migration Phases

1. **Staging**: Move legacy code to a dedicated `legacy/` directory for reference and continued operation.
2. **Protocol Extraction**: Identify and extract protocol interfaces from legacy code.
3. **Core Implementation**: Create new implementations of core protocols using ONEX conventions.
4. **Component Migration**: Gradually migrate individual components as node functions.
5. **Validation & Testing**: Ensure functional equivalence through parallel testing.
6. **Production Transition**: Switch production systems to new implementations.

---

### Legacy Code Staging

Legacy code is preserved in a controlled environment to maintain reference and continuity during migration.

#### ✅ Legacy Directory Structure

```
legacy/
├── foundation/           # Original Foundation codebase
│   ├── protocols/        # Legacy protocol definitions
│   ├── validators/       # Legacy validators
│   └── tools/            # Legacy tools
└── README.md             # Documentation of the legacy codebase
```

#### ✅ Legacy Reference Tagging

Legacy code files are tagged to indicate their migration status:

```python
# 
# LEGACY CODE: Scheduled for migration to ONEX
# Migration Target: src/omnibase/protocol/protocol_validate.py
# Migration Status: Not Started
# Expected Completion: M1
#
```

---

### Component Migration Process

Individual components follow a consistent migration process.

#### ✅ Component Migration Steps

1. **Identify Function Interface**: Define the component's core function, inputs, outputs, and contracts.
2. **Create ONEX Node Structure**: Set up the node directory structure following ONEX conventions.
3. **Implement Node Function**: Reimplement or adapt the core logic as a node function.
4. **Define State Contracts**: Create explicit state contracts for inputs and outputs.
5. **Create Node Metadata**: Define the `.onex` metadata file.
6. **Implement Tests**: Create tests that verify equivalence with legacy behavior.
7. **Update Registry**: Add the new node to the `.tree` file.

---

### Migration Tracking and Documentation

Migration progress is tracked and documented for transparency and coordination.

#### ✅ Migration Log Format

A migration log (`docs/migration_log.md`) tracks the progress of each component:

```markdown
# Migration Log

## Component: SchemaValidator

- **Legacy Location**: `foundation/validators/schema_validator.py`
- **ONEX Location**: `src/omnibase/nodes/validator.schema/`
- **Status**: Completed
- **Migration Date**: 2025-05-15
- **Verified By**: @jonah.gray
- **Notes**: Behavior verified identical to legacy version through test suite.

## Component: PromptGenerator

- **Legacy Location**: `foundation/tools/prompt_generator.py`
- **ONEX Location**: `src/omnibase/nodes/tool.prompt.generator/`
- **Status**: In Progress
- **Expected Completion**: 2025-05-20
- **Assigned To**: @emma.wilson
- **Notes**: Core function extracted, state contracts defined, tests in progress.
```

---

**Status:** This document defines the canonical approach for migrating legacy Foundation code to the ONEX architecture. All migration efforts should follow this strategy to ensure a consistent, controlled, and successful transition.

--- 