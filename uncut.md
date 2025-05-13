    # OmniBase Design Spec (v0.4.0)

    > **Status:** Draft / Living Document
    > **Location:** docs/omnibase/omnibase_design_spec.md
    > **Maintainers:** foundation-team
    > **Last Updated:** 2025-05-15

    ---

    ## Overview

    OmniBase is the foundational infrastructure layer for OmniNode. It encapsulates core protocols, modular function registries, test systems, and validator pipelines. This document defines the architecture, goals, and structural components of the OmniBase repository.

    OmniBase provides the reusable primitives and enforcement mechanisms needed to support agentic infrastructure, including:

    - Validator registration and execution
    - Tool (transformer) registration and chaining
    - Metadata-tagged test case definitions
    - Execution context and result protocols, designed for extensibility and generic application
    - Canary-first development and lifecycle enforcement
    - Registry-driven discovery and execution

    All components are designed to be agent-compatible, composable, and protocol-first. Testing layers implement `typing.Protocol`; production infrastructure derives from `abc.ABC`. The `ExecutionContext`, `Artifact`, and `Result` families follow this rule. The mechanism for agent-generated functions will primarily involve agents producing code (e.g., Python snippets) or declarative configurations that adhere to OmniBase protocols, which are then dynamically registered and executed within a managed environment.

    ---

    ## Canonical Principles

    ### 1. Function-as-Unit

    Every tool, validator, or test is a **registered, standalone function** with well-defined:

    - Input type: Typically a generic `Artifact[T]`. Concrete examples include `FileArtifact`, `DirectoryTreeArtifact`, `MetadataBlockArtifact`. These types will be formally defined, likely within `omnibase/protocols/` or `omnibase/schema/`, inheriting from a base `Artifact` protocol.
    - Execution context: An `ExecutionContext` object. This object will carry necessary information such as configuration parameters, access to managed (and potentially sandboxed) resources or secrets, logging facilities, and tracing correlation IDs.
    - Output/result structure: A generic `Result[U]`. Specific instances like `ValidationResult`, `TransformResult`, `TestResult` will inherit from a base `Result` protocol (e.g., `UnifiedResultModel`). This structure will include common fields like status, detailed messages, structured error information, and references to output artifacts.

    These functions are tagged with metadata and discovered through registries.

    ### 2. Registry-Driven Execution

    Registries track:

    - Validators (`ValidatorRegistry`)
    - Tools (`ToolRegistry`)
    - Test cases (`TestCaseRegistry`)

    Each registry is queryable by:

    - Input/output types (leveraging the generic `Artifact` and `Result` protocols)
    - Tags (e.g. `canary`, `integration`, `pre-commit`)
    - Version (Semantic Versioning - SemVer - is recommended for components) and lifecycle phase
    - Source (hard-coded, agent-generated, external)

    ### 3. Protocol Uniformity

    All function signatures follow a common pattern:

        def run(input: Artifact[T], context: ExecutionContext) -> Result[U]

    This enables:

    - Stateless execution (to the extent possible, state managed via `ExecutionContext` if unavoidable)
    - Runtime orchestration
    - Agent-compatibility
    - Dynamic substitution of logic sources

    ### 4. Source-Agnostic Execution

    Each component can be authored or executed by:

    - Hard-coded logic
    - Agent-generated functions (e.g., Python code, structured configurations)
    - External systems or remote services (via adaptors that conform to the `run` protocol)

    All executions produce results that include:

    - Input hash / provenance
    - Source and version (SemVer recommended)
    - Execution timestamp
    - Scored or pass/fail result, with detailed messages and potential error structures.

    ### 5. Test Case Portability

    Tests are declarative units with structured inputs and validations. They may target:

    - Tools
    - Validators
    - Agent-generated outputs

    Test runners are registry-aware and support filtering by:

    - `test_type` (unit, integration, e2e)
    - `lifecycle` (canary, stable, deprecated)
    - `tags` (file-level, schema, transform, etc.)

    ### 6. Validator and Tool Symmetry

    Validators and tools are duals:

    - Validators **assert** properties over artifacts
    - Tools **mutate** or transform artifacts

    Both follow the same registration and execution protocol. Toolchains can be assembled and versioned like pipelines.

    ### 7. Canary-First Enforcement

    OmniBase enforces a canary development lifecycle:

    - Canary components are isolated and version-locked
    - All infrastructure changes begin in canary mode
    - Test runners, CI, and scaffolds respect lifecycle phase

    ---

    ## Repository Structure

    ```
    omnibase/
    ├── core/
    │   ├── abcs/            # Abstract Base Classes with SCHEMA_VERSION
    │   ├── models/          # Domain models and data structures
    │   ├── registry/        # Core registry implementations
    │   ├── storage/         # Artifact storage and retrieval
    │   └── orchestrator_*.py # Flat modules: orchestrator_precommit.py, etc.
    ├── protocols/
    │   ├── testing/         # Protocols for test doubles (__protocol_version__)
    │   └── lenses/          # Protocols for inspection and introspection
    ├── adapters/            # Adapters for external systems
    ├── cli/                 # Command-line interfaces
    │   └── formatters/      # Output formatters (human, json, yaml)
    ├── validators/          # Validator implementations
    ├── tools/               # Tool implementations
    ├── pipelines/           # Pipeline definitions and composition
    ├── tests/               # Test cases and testing utilities
    ├── templates/           # Scaffolding templates
    ├── config/              # Configuration management
    └── docs/                # Documentation
    ```

    **Rules:**
1. Maximum directory depth is two levels.
2. `core/` and `adapters/` are importable by runtime code.
3. `protocols/` is test-only; CI blocks runtime usage.
4. Every ABC carries `SCHEMA_VERSION`; every Protocol carries `__protocol_version__`.
5. `flake8-omnibase` code `OB101` blocks runtime imports from `protocols.testing`.

    ---

    ## Design Review & Alignment

    ### Strengths

    - Stateless, registry-driven functions enable agentic, composable, and testable systems.
    - Registry-driven discovery and execution support modularity, dynamic orchestration, and compliance enforcement.
    - Source-agnostic execution and provenance tracking enable traceability and agent integration.
    - Declarative, metadata-tagged test cases and registry-aware runners are best practice for scalable test infrastructure.
    - Validator/tool symmetry and canary-first enforcement support safe, incremental evolution.
    - Repository structure is clean and migration-friendly.

    ### Considerations & Suggestions

    - Define all protocols (e.g., `Artifact`, `Result`, `ExecutionContext`) as Python `typing.Protocol`s or ABCs, and enforce with static analysis (e.g., MyPy) in CI.
    - `ExecutionContext`, `Artifact`, and `Result` models must be extensible and versioned.
    - All results should inherit from a unified base like `UnifiedResultModel` (a specific `Result[U]` protocol). This model should standardize reporting of errors versus expected negative outcomes (e.g., a validation failing as designed).
    - Registries must require a comprehensive metadata block per entry, including lifecycle, tags, and version data.
    - Registry-aware test runner should support filtered, batch, and potentially parallel execution.
    - CLI tools must be registry- and protocol-compliant, offering functionalities such as:
        - `omnibase list validators --tag canary`
        - `omnibase run tool <tool_uuid_or_name> --input <artifact_path_or_id>`
        - `omnibase inspect metadata <artifact_uuid_or_name>`
        - `omnibase validate metadata <metadata_file_path>`
        - `omnibase visualize dependencies <artifact_uuid_or_name>`
        - `omnibase compose pipeline --from <tool1_id> --to <tool2_id> --to <validator_id>`
    - Legacy code must be clearly separated, documented, and have a defined EOL or migration path.
    - System should support runtime registration and hot-reload for agent-generated logic, with appropriate security sandboxing.
    - Document all design patterns, protocols, and provide comprehensive onboarding guides.
    - **Security:** Explicitly define security models and sandboxing mechanisms, especially for agent-generated code and external system interactions. See `docs/security/threat_model.md` (pending) for detailed security design.
    - **Dependency Resolution:** Specify the strategy for resolving version conflicts for `dependencies` listed in metadata (e.g., resolver logic, error on conflict, use latest compatible).
    - **Standardized Repository Structure:** Create a canonical directory structure template that all OmniBase components must follow, ensuring consistency and reducing cognitive load.
    - **Protocol Evolution Strategy:** Define a formal protocol evolution strategy with compatibility matrices and migration paths to maintain backward compatibility.
    - **Function Composition Framework:** Design patterns for composing multiple functions into pipelines with automatic dependency resolution and parallel execution.
    - **Artifact Storage & Retrieval:** Implement a storage abstraction for artifacts with content-addressable storage, versioning, and efficient retrieval patterns. CAS runs mark-and-sweep GC; root set = registry-referenced digests; retention by tag, lifecycle, age.

    ### Risks / Watchpoints

    - Registry bloat: mitigate with tagging, scopes, namespaces, and fast lookup indices.
    - Protocol drift: enforce compliance in CI with static analysis and protocol-specific tests.
    - Legacy artifacts: isolate and gate migration workflows clearly.
- **Security Vulnerabilities:** Execution of arbitrary or agent-generated code requires robust sandboxing, input validation, and permission models.
- **Performance Bottlenecks:** Implement monitoring, profiling, and performance testing to identify and address bottlenecks early.
- **Complexity Creep:** Maintain simplicity in the core interfaces while allowing flexibility in implementations.
- **Execution Reliability:** Orchestrators wrap executions with automatic retry (exponential back-off) and circuit breaker guards.

    ---

    ## Metadata Schema Innovations (Graph, Dependencies, UUIDs)

    ### Generalized Metadata Schema

    All artifacts (validators, tools, test cases, data, etc.) must include a metadata block, in-file or as a sidecar.

    The schema supports:

    - **UUIDs** for uniqueness and graph traversal
    - **Parent/child links** (using UUIDs of other metadata blocks) for lineage and inheritance
    - **Typed dependencies** with version resolution (SemVer recommended for versions)
    - **Lifecycle**, **status**, and **tags** for filtering and orchestration
    - **Custom fields** for agents or domain-specific metadata

    ### Canonical Metadata Block Example (YAML)

        # === OmniNode:Metadata ===
        metadata_version: "0.2.1"       # Version of the metadata block schema itself
        schema_version: "1.1.0"         # Version of the specific object's schema (e.g., validator schema)
        uuid: "123e4567-e89b-12d3-a456-426614174000"
        name: "example_validator"
        namespace: "foundation.script.validate"
        version: "0.1.0"                # SemVer for the component itself
        type: "validator"
        entrypoint: "python_validate_example.py"
        protocols_supported: ["O.N.E. Core v0.1"] # Name and version of the OmniBase Execution protocol this adheres to
        # protocol_version: "0.1.0" # Consider if this is needed if version is in protocols_supported
        author: "OmniNode Team"
        owner: "foundation-team"
        created_at: "2025-05-12T12:00:00+00:00"
        last_modified_at: "2025-05-13T10:00:00+00:00"
        parent_id: "uuid_of_root_validator_metadata_block" # UUID of another metadata block
        child_ids: ["uuid_of_child1_metadata", "uuid_of_child2_metadata"] # List of UUIDs
        dependencies:
          - id: "tool_fix_format_headers_uuid" # UUID of the dependency's metadata
            type: "tool"
            version_spec: ">=0.1.0,<0.2.0" # Version constraint for the dependency
            required: true
          - id: "data_example_uuid"
            type: "data_artifact"
            version_spec: "1.0.0"
            required: false
        tags: ["canary", "pre-commit", "schema-validation"]
        lifecycle: "canary"             # E.g., canary, stable, deprecated, experimental
        status: "active"                # E.g., active, inactive, pending_review
        idempotent: true                # Permits automatic retry & caching
        description: "A canonical example of a validator metadata block."
        # === /OmniNode:Metadata ===

    *Note on `protocols_supported`: Adherence can be enforced via static analysis against defined Python `Protocol`s and runtime checks during registration or execution.*

    ---

    ## Unified Output Formats

    All OmniBase tools must support standardized output formats for both human and machine consumption. The table below defines the canonical output formats:

    | Flag | Audience | Characteristics |
    |------|----------|-----------------|
    | `--format human` *(default when `isatty=True`)* | Pre-commit, local use | ANSI color, emoji, ≤100-char lines |
    | `--format json` | CI, orchestrators | Canonical schema, stable key order |
    | `--format yaml` | Debugging, agent ingestion | Block style, anchors permitted |

    The `omnibase.cli.formatters.FORMATTERS` dictionary maps flag values to formatter callables.

    ### Emoji Map

    For human-readable output, use the following emoji map (with fallback to ASCII when `TERM=dumb`):

    | Status | Emoji |
    |--------|-------|
    | PASS | ✅ |
    | FAIL | ❌ |
    | WARN | ⚠️ |
    | SKIP | ⏭️ |
    | TIME | ⏱️ |

    ### Error Object Structure

    All errors reported in machine-readable formats (JSON/YAML) must follow a canonical structure:

    ```json
    {
      "error_code": "VALIDATOR_ERROR_001",
      "error_type": "ValidationError",
      "message": "Human-readable error message",
      "location": {
        "file_path": "path/to/file.py",
        "line_number": 42
      },
      "timestamp": "2025-05-15T10:00:00Z",
      "context": {
        "validator_id": "uuid_of_validator",
        "artifact_id": "uuid_of_artifact"
      },
      "severity": "error", // One of: "error", "warning", "info"
      "suggestions": [
        "Consider fixing X by doing Y",
        "Documentation at: URL"
      ]
    }
    ```

    ---

    ## Orchestrator Entry Point

    All execution flows should use a consistent orchestrator pattern with a single binary invocation per stage:

    ```bash
    omnibase orch --stage pre-commit --format human || exit 1
    ```

    The `omnibase.core.orchestrators` module hosts stage-specific classes implementing the orchestrator interface:

    ```python
    class Orchestrator(ABC):
        def run(self, ctx: ExecCtx) -> RunReport: ...
    ```

    The CLI defaults to JSON output format for non-interactive machine consumption. Human format is used only when running interactively (`isatty=True`).

    ### Orchestrator Types

    - **PreCommitOrchestrator**: Validates changes before commit
    - **CIOrchestrator**: Runs validations in continuous integration
    - **PipelineOrchestrator**: Executes tool/validator pipelines
    - **TestOrchestrator**: Runs test cases
    - **RegistryOrchestrator**: Manages registry operations (add, update, remove)

    All orchestrators follow the same execution pattern but may have stage-specific configurations and behaviors.

    ---

    ## Protocol vs ABC Guidelines

    OmniBase follows strict rules regarding the use of Protocols vs Abstract Base Classes:

    - **protocols/testing/**: Contains `typing.Protocol` objects that are runtime-checkable, with version tracking via `__protocol_version__`.
    - **core/abcs/**: Contains Abstract Base Classes with `SCHEMA_VERSION` constant.

    Types required by both domains (e.g., `ExecutionContext`) provide both a Protocol (for test doubles) and an ABC (for concrete use). Production code must never import from the `protocols.testing` namespace.

    This separation is enforced via a Flake8 plugin during CI.

    ### Version Compatibility Matrix

    | Component Type | Version Format | Compatible With |
    |----------------|----------------|----------------|
    | Protocol | `__protocol_version__ = "1.0.0"` | Same major version |
    | ABC | `SCHEMA_VERSION = "1.0.0"` | Same major version |
    | Registry | `REGISTRY_VERSION = "1.0.0"` | Same major & minor version |
    | Metadata | `metadata_version: "0.2.1"` | Same major & minor version |

    Components should maintain backward compatibility within a major version. Breaking changes require a new major version.
    
    Compatibility algorithm: major mismatch → block; minor mismatch → warn; patch mismatch → allow.

    ---

    ## Configuration Cascading

    OmniBase uses a hierarchical configuration system with well-defined precedence:

    1. Command-line arguments (highest precedence)
    2. Environment variables (`OMNIBASE_*`)
    3. Project-level configuration (`./omnibase.yml`)
    4. User-level configuration (`~/.config/omnibase/config.yml`)
    5. System-level configuration (`/etc/omnibase/config.yml`)
    6. Default values (lowest precedence)

    Configuration is merged at runtime, with higher-precedence sources overriding lower ones. Array values can be appended rather than replaced by using the `+array:` prefix.

    Example config (`omnibase.yml`):
    ```yaml
    validators:
      tags:
        - pre-commit
        - schema
      ignore:
        - build/
        - tmp/
    formatters:
      human:
        color: true
        emoji: true
    registry:
      cache_ttl: 3600
    ```

    ---

    ## Maintenance Policies

    1. New ABCs reside in **core/abcs/**; new Protocols in **protocols/**.
    2. Hook scripts use the orchestrator; individual binaries are no longer allowed in hooks.
    3. Formatter registry must include a `human` formatter compliant with the emoji map.
    4. Directory changes require an entry in `docs/RELEASE_NOTES.md`.
    5. All public APIs must have comprehensive docstrings and type annotations.
    6. Breaking changes must be documented in the release notes and include migration guides.
    7. Deprecation notices must be added at least one minor version before removal.
    8. Runtime compatibility checks must be performed when components with different versions interact.
    9. CI enforces `flake8-omnibase` ruleset (OB1xx codes).

    ---

    ## Migration & Compatibility

    - Legacy metadata may omit UUIDs and detailed dependency objects; migration scripts will aim to retrofit them or flag for manual review.
    - Old-style `dependencies: ["foo", "bar"]` are accepted temporarily only if a clear mapping to new versioned, typed dependencies can be inferred, and will generate warnings logged for upgrade.
    - Graph-based integrity checks (using UUIDs) will flag cycles, broken links, and ID collisions.

    ### Version Migration Strategy

    1. During the transition to canonical structure, a **coexistence period** will be maintained where both old and new structures work.
    2. The `omnibase migrate` command will assist in migrating components to the new structure.
    3. Automated detection and warnings will highlight components that need migration.
    4. Legacy components have a defined EOL (End-of-Life) date after which they will not be supported.

    ---

    ## Graph Extraction & Tooling

    - Metadata structure supports full dependency and lineage graphs.
    - Tools will include:
      - Graph traversal and querying
      - Visualization of dependencies and lineage
      - Impact analysis (e.g., "what downstream components are affected by a change to this tool?")
      - Workflow simulation and validation

    ### Schema Documentation

    All schemas will be auto-documented using a combination of:
    - Pydantic model introspection
    - JSON Schema generation
    - Interactive API documentation using Swagger/OpenAPI

    This documentation will be generated during the build process and made available through:
    - Static documentation site
    - Interactive API explorer
    - CLI help system (`omnibase schema describe <schema_name>`)

    ---

    ## Open Questions & Proposed Answers

    ### 1. Agent Integration Model

    **Q: How will agents be trained to produce code that follows these protocols?**

    **A:** Agents will be provided with scaffolding templates, protocol stubs, and validated examples. A dedicated agent onboarding toolkit will include:
    - Explicit protocol definitions with docstrings and type annotations
    - Example implementations for each protocol
    - Validation tools to check protocol compliance before registration
    - A sandbox environment for testing agent-generated functions
    - A formal feedback loop mechanism to improve agent-generated code over time

    ### 2. Cross-Language Support

    **Q: How will non-Python code interact with the system?**

    **A:** For initial implementation:
    - Python will be the primary language for core protocols and registries
    - Non-Python components can be supported via:
      - Language-specific adapters that conform to the protocols
      - Subprocess execution with standardized I/O formats (JSON/YAML)
      - API Gateway pattern for HTTP/gRPC service integration
    - Future plans include defining language-agnostic protocol specifications (e.g., OpenAPI) that can be implemented in multiple languages

    ### 3. Deployment Model

    **Q: How will OmniBase components be deployed, versioned, and updated?**

    **A:** OmniBase will use a hybrid deployment model:
    - Core components packaged as Python libraries (pip installable)
    - Registry data stored in versioned databases or file repositories
    - Runtime components deployable as standalone services or embedded agents
    - Version management through:
      - Semantic versioning for all components
      - Explicit version compatibility matrices
      - Canary deployment patterns for new component versions
      - Registry-aware dependency resolution at runtime

    ### 4. Testing Approach

    **Q: What testing approaches will be used for OmniBase components?**

    **A:** OmniBase will enforce a comprehensive testing strategy:
    - Unit testing for all protocol implementations
    - Integration testing for registry interactions and tool chains
    - Property-based testing for critical protocol interfaces
    - Golden test cases for validating tool/validator outputs
    - Cross-protocol compliance testing in CI
    - Performance benchmarking for critical paths
    - Security testing for sandboxed execution

    ### 5. Performance Characteristics

    **Q: What performance characteristics are expected for components?**

    **A:** Performance requirements will be formalized as:
    - Registry operations should complete in <100ms for typical queries
    - Tools/validators should explicitly declare their performance category:
      - **Fast**: <100ms execution time, suitable for real-time/interactive use
      - **Standard**: <1s execution time, suitable for CI pipelines
      - **Heavy**: >1s execution time, requiring batch/background processing
    - Metadata will include performance expectations and resource requirements
    - Performance testing will be part of the acceptance process

    ### 6. Version Resolution Algorithm

    **Q: What algorithm will resolve dependency version constraints?**

    **A:** The dependency resolution will use:
    - A modified Pubgrub algorithm (used by Dart, Rust, and modern Python tools)
    - Support for SemVer ranges and compatibility rules
    - Explicit handling of incompatible versions
    - Preference for newer versions within compatible ranges
    - Local override capability for testing
    - Conflict resolution with clear error reporting

    ### 7. Metrics & Monitoring

    **Q: What standard metrics and monitoring patterns will be available?**

    **A:** OmniBase will provide:
    - Standard instrumentation for all components:
      - Execution time and success/failure counts
      - Resource utilization metrics
      - Error rates and types
      - Dependency resolution statistics
    - Structured logging with correlation IDs
    - Tracing support via OpenTelemetry
    - Health/readiness probes for service components
    - Registry status and integrity metrics

    ### 8. Function Backpressure & Rate Limiting

    **Q: How will the system handle overload or rate limiting?**

    **A:** OmniBase will implement:
    - Rate limiting at the registry and execution level
    - Configurable concurrency limits per tool/validator type
    - Priority-based execution queuing (critical, standard, background)
    - Graceful degradation strategies for overload conditions
    - Circuit breakers for failing components
    - Resource allocation and reservation patterns

    ---

    ## Innovative Ideas to Consider

    ### 1. Multi-Stage Validation Pipeline
    - Implement a tiered validation approach (fast/shallow, medium, deep) to run inexpensive validations earlier
    - Enable "validation gating" where deeper validations only run if shallow checks pass
    - Support parallelization of independent validations
    - Provide immediate feedback for fast validations while deeper checks continue

    ### 2. Self-Describing Functions
    - Extract capabilities, inputs, outputs from function implementations
    - Generate API documentation automatically from actual code
    - Use runtime introspection to verify behavior matches description
    - Build interactive explorers that demonstrate function capabilities

    ### 3. Live Debugging Mode
    - Create a development mode where functions execute step-by-step
    - Visualize intermediate states and data transformations
    - Snapshot execution state for reproducible debugging
    - Support interactive modification and re-execution

    ### 4. Compatibility Matrix Generation
    - Automatically generate and maintain compatibility matrices between components
    - Test N×N combinations of component versions in CI/CD
    - Create visual heatmaps of compatibility status
    - Alert on compatibility regressions

    ### 5. Automatic A/B Testing
    - Enable parallel execution of alternative implementations for the same function
    - Compare results for correctness, performance, and resource usage
    - Gather statistics for automated selection of optimal implementation
    - Support gradual rollout of new implementations

    ### 6. Artifact Caching & Memoization
    - Implement content-addressable caching for function outputs
    - Skip duplicate computations when inputs haven't changed
    - Support distributed cache for multi-node environments
    - Provide fine-grained cache invalidation based on dependency changes

    ### 7. Federated Registry Architecture
    - Support distributed, federated registries across organizational boundaries
    - Enable discoverability while maintaining security boundaries
    - Support partial synchronization based on trust relationships
    - Allow "plugin marketplace" model for community contributions

    ### 8. Differential Testing for Validators
    - Apply the same validator to slightly modified inputs to verify sensitivity
    - Compare validator behavior across versions to detect regressions
    - Automatically generate test cases by mutating known valid/invalid inputs
    - Document expected validator sensitivity in metadata

    ### 9. Reinforcement Learning for Optimization
    - Apply RL techniques to optimize tool chains and execution order
    - Learn optimal resource allocation strategies from historical executions
    - Discover efficient validation strategies based on past failures
    - Continuously improve performance of common workflows

    ### 10. Agent-as-Reviewer Pipeline
    - Implement agent-driven review pipeline for code changes
    - Use validation results to guide agent review process
    - Generate targeted improvement suggestions based on validation failures
    - Enable collaborative workflow between human developers and agent reviewers

    ---

    ## Next Steps

    - [ ] Define `ExecutionContext`, `Artifact[T]`, and `Result[U]` base protocols, including common fields and error handling strategies.
    - [ ] Implement initial versions of `FileArtifact`, `ValidationResult`, etc., based on the new protocols.
    - [ ] Migrate refactored metadata system and implement parser/validator for the metadata block.
    - [ ] Freeze canonical validator + test scaffolds using the new protocols and metadata.
    - [ ] Implement registry-driven test runner with filtering capabilities.
    - [ ] Import initial canary-level functions into registries with new metadata.
    - [ ] **Draft initial security model and sandboxing strategy for agent-generated and external function execution.**
    - [ ] **Specify component versioning strategy (confirm SemVer) and dependency resolution logic.**
    - [ ] Document protocols, metadata schema, common patterns, and runner usage.
    - [ ] Provide migration and integration guides for developers.
    - [ ] Develop initial CLI tools for basic registry interaction and function execution.
    - [ ] **Create prototype for artifact storage and retrieval abstraction.**
    - [ ] **Develop function composition framework for building pipelines.**
    - [ ] **Design metrics and instrumentation standards for all components.**
    - [x] **Implement the unified output formatters system (human, JSON, YAML).** [in-progress]
    - [ ] **Scaffold orchestrators for various stages (pre-commit, CI, etc.).**
    - [ ] **Migrate repository to the canonical directory structure.**
    - [ ] **Integrate Flake8 rule preventing runtime imports from protocols.testing.**
    - [ ] **Create automatic schema documentation generation toolkit.**
    - [ ] **Develop version compatibility checking tools and matrices.**
    - [ ] **Implement hierarchical configuration system with cascading precedence.**

    ---

    ## Revision Log

    - **2025-05-12:** Initial draft (v0.1)
    - **2025-05-13 (morning):** Added `schema/`, `templates/`, and `base/` directories. Standardized plural naming. Formalized canonical metadata format (v0.2).
    - **2025-05-13 (afternoon):** (v0.2.1) Incorporated review suggestions:
        - Clarified `ExecutionContext`, generic `Artifact[T]`, and `Result[U]` protocols.
        - Detailed repository structure directory purposes.
        - Expanded on agent-generated function mechanisms and security considerations.
        - Specified SemVer for component versions and detailed dependency versioning in metadata.
        - Added detail on error handling within `Result` objects.
        - Suggested example CLI commands.
        - Emphasized UUID usage for graph links in metadata.
        - Updated "Next Steps" with security, versioning, and protocol definition tasks.
        - Minor updates to metadata example for clarity (e.g. `version_spec` for dependencies, `protocols_supported`).
    - **2025-05-14:** (v0.3.0) Major update:
        - Added `storage/`, `pipelines/`, and `config/` directories to repository structure.
        - Extended CLI examples with visualization and pipeline composition.
        - Added proposed answers to open questions on agent integration, cross-language support, deployment, testing, performance, version resolution, metrics, and rate limiting.
        - Added ten innovative ideas including multi-stage validation, self-describing functions, live debugging, compatibility matrix generation, A/B testing, artifact caching, federated registries, differential testing, reinforcement learning, and agent-as-reviewer pipeline.
        - Extended next steps with artifact storage, function composition, and metrics standards.
    - **2025-05-15:** (v0.4.0) Comprehensive update integrating addendum:
        - Restructured repository layout to follow a stricter two-level maximum depth.
        - Added Protocol vs ABC guidelines with clear rules about when to use each.
        - Added Unified Output Formats section standardizing human, JSON, and YAML outputs.
        - Defined orchestrator entry points and standard execution patterns.
        - Added Version Compatibility Matrix for protocols, ABCs, registries, and metadata.
        - Added Configuration Cascading section documenting hierarchical configuration.
        - Added Maintenance Policies for ongoing development.
        - Enhanced Error Object Structure for consistent error reporting.
        - Added Schema Documentation section for auto-generated API docs.
        - Extended Next Steps with new immediate action items.
    - **2025-05-16:** (v0.4.1) Refined design based on additional review:
        - Added specific enhancements for document hygiene and review processes
        - Defined explicit async execution interface alongside synchronous protocol
        - Added idempotency contract to metadata schema
        - Formalized version compatibility logic and rule set
        - Committed to Postgres as registry backend with file-based caching option
        - Expanded error taxonomy with specific error types
        - Adopted RFC 7396 for config merge semantics
        - Defined security deliverables with specific technology choices
        - Enhanced output formatter with explicit fallbacks
        - Added content-addressable storage garbage collection specification

    ---

    ## OmniBase Design Addendum (v0.4.1)

    > **Status:** Approved
    > **Last Updated:** 2025-05-16

    ### 1. Document Hygiene
    * Review commentary has been moved to `docs/reviews/2025-05-15_system_architect.md`
    * Core specification now focuses on requirements and technical details only

    ### 2. Async Execution Interface
    ```python
    class AsyncRunnable(Protocol):
        async def run(
            self,
            input: Artifact[T],
            context: ExecutionContext,
        ) -> Result[U]: ...
    ```

    This protocol complements the synchronous `Runnable` protocol and is recommended for:
    * Long-running operations (>1s execution time)
    * Operations with I/O or network dependencies
    * Components requiring parallel execution

    ### 3. Idempotency Contract
    The metadata schema now includes an explicit idempotency field:
    ```yaml
    idempotent: true  # Whether multiple executions with same input produce identical results
    ```

    When `idempotent: true`:
    * Orchestrators may automatically retry on transient failures
    * Results may be cached based on input hash
    * Function may be used in parallel execution contexts

    ### 4. Version Compatibility Logic
    ```python
    from enum import Enum
    from semver import Version

    class Compatibility(Enum):
        COMPATIBLE = "compatible"
        WARNING = "warning"  # Compatible but with caution
        INCOMPATIBLE = "incompatible"

    def check_compat(local: str, remote: str) -> Compatibility:
        """Check compatibility between two semantic versions.
        
        Rules:
        - Major version mismatch: INCOMPATIBLE
        - Minor version mismatch: WARNING
        - Patch version mismatch: COMPATIBLE
        """
        local_v = Version.parse(local)
        remote_v = Version.parse(remote)
        
        if local_v.major != remote_v.major:
            return Compatibility.INCOMPATIBLE
        if local_v.minor != remote_v.minor:
            return Compatibility.WARNING
        
        return Compatibility.COMPATIBLE
    ```

    ### 5. Registry Backend Decision
The authoritative registry store is PostgreSQL; local file caches operate in write-through mode with periodic sync.

Postgres provides:
* Transactional consistency guarantees
* JSON/JSONB support for metadata storage
* Support for advanced indexing and querying

Local file-based registry access is supported via:
* Write-through caching to improve performance
* Periodic synchronization with authoritative store
* Read-only mode for disconnected operation

    ### 6. Error Taxonomy Seed
    ```python
    class OmniBaseError(Exception):
        """Base class for all OmniBase errors."""
        pass

    class RegistryError(OmniBaseError):
        """Base class for registry-related errors."""
        pass

    class RegistryLookupError(RegistryError):
        """Error when a component cannot be found in the registry."""
        pass

    class ArtifactError(OmniBaseError):
        """Base class for artifact-related errors."""
        pass

    class ArtifactNotFoundError(ArtifactError):
        """Error when a referenced artifact cannot be found."""
        pass

    class ProtocolError(OmniBaseError):
        """Base class for protocol-related errors."""
        pass

    class ProtocolComplianceError(ProtocolError):
        """Error when a component does not comply with a required protocol."""
        pass

    class SecurityError(OmniBaseError):
        """Base class for security-related errors."""
        pass

    class SandboxViolationError(SecurityError):
        """Error when a component attempts to violate sandbox constraints."""
        pass

    class DependencyError(OmniBaseError):
        """Base class for dependency-related errors."""
        pass

    class DependencyResolutionError(DependencyError):
        """Error when dependencies cannot be resolved."""
        pass

    class ExecutionError(OmniBaseError):
        """Base class for execution-related errors."""
        pass

    class ExecutionTimeoutError(ExecutionError):
        """Error when execution exceeds time limits."""
        pass

    class ConfigurationError(OmniBaseError):
        """Error when configuration is invalid or cannot be loaded."""
        pass
    ```

    ### 7. Config Merge Semantics
    Configuration merging will follow [RFC 7396 (JSON Merge Patch)](https://datatracker.ietf.org/doc/html/rfc7396) semantics, which provides:
    * A standardized approach for partial updates
    * Clear semantics for array replacements
    * Well-defined behavior for nested structures

    The custom `+array:` prefix has been dropped in favor of explicit merge operations through the configuration API.

    ### 8. Security Deliverable
    A dedicated security design document (`docs/security/threat_model.md`) will be created covering:
    * Sandbox implementation using gVisor for container isolation
    * Secret injection pattern via temporary filesystem
    * Capability policy language based on Cedar
    * Permission model for registry and artifact access
    * Dynamic capability request and grant patterns

    ### 9. Output Formatter Fallback
    Output formatting has been enhanced with:
    * `--no-color` flag for explicitly disabling ANSI colors and emoji
    * Automatic detection of terminal capabilities via:
      * `TERM=dumb` environment variable
      * `CI=true` environment variable
      * Non-TTY output detection
    * ASCII fallbacks for all emoji

    ### 10. Garbage Collection Spec
    Content-addressable storage will use a mark-and-sweep garbage collection strategy:
    * Root set consists of all artifacts referenced in registries
    * GC runs as a scheduled job (configurable frequency)
    * Retention policies can be set based on:
      * Tags (e.g., `retain: always` for critical artifacts)
      * Lifecycle phase (e.g., `stable` artifacts kept longer than `experimental`)
      * Age (e.g., remove canary artifacts older than 30 days)
      * Usage patterns (e.g., retain frequently accessed artifacts)

    ---

    ## Technical Implementation Patterns

    The following examples demonstrate concrete implementation patterns for key aspects of the OmniBase architecture. These patterns should be used as reference implementations when developing components.

    ### 1. Protocol & ABC Implementation

    ```python
    # In core/abcs/execution_context.py
    from abc import ABC, abstractmethod
    from typing import Dict, Any, Optional
    from uuid import UUID

    class ExecutionContextABC(ABC):
        """Abstract base class for execution contexts."""
        
        SCHEMA_VERSION = "1.0.0"
        
        @abstractmethod
        def get_config(self, key: str, default: Any = None) -> Any:
            """Get configuration value."""
            pass
        
        @abstractmethod
        def get_capability(self, name: str) -> bool:
            """Check if this context has a named capability."""
            pass
        
        @abstractmethod
        def get_correlation_id(self) -> UUID:
            """Get correlation ID for tracing."""
            pass
        
        @abstractmethod
        def get_logger(self, name: Optional[str] = None):
            """Get logger instance."""
            pass

    # In protocols/testing/execution_context.py
    from typing import Protocol, Dict, Any, Optional, runtime_checkable
    from uuid import UUID

    @runtime_checkable
    class ExecutionContext(Protocol):
        """Protocol for execution contexts."""
        
        __protocol_version__ = "1.0.0"
        
        def get_config(self, key: str, default: Any = None) -> Any:
            """Get configuration value."""
            ...
        
        def get_capability(self, name: str) -> bool:
            """Check if this context has a named capability."""
            ...
        
        def get_correlation_id(self) -> UUID:
            """Get correlation ID for tracing."""
            ...
        
        def get_logger(self, name: Optional[str] = None):
            """Get logger instance."""
            ...
    ```

    ### 2. Error Handling Framework

    ```python
    # In core/errors/retry.py
    import time
    from typing import TypeVar, Callable, Any, Optional
    import random
    from .base import OmniBaseError, ExecutionError

    T = TypeVar('T')

    class RetryableError(ExecutionError):
        """Error that can be automatically retried."""
        pass

    class RetryExhaustedError(ExecutionError):
        """Error when all retry attempts have been exhausted."""
        def __init__(self, original_error, attempt_count):
            self.original_error = original_error
            self.attempt_count = attempt_count
            super().__init__(f"Retry exhausted after {attempt_count} attempts: {original_error}")

    def retry(
        max_attempts: int = 3,
        delay_ms: int = 100, 
        backoff_factor: float = 2.0,
        jitter_ms: int = 50,
        retryable_errors: tuple = (RetryableError,)
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator for retrying functions with exponential backoff.
        
        Args:
            max_attempts: Maximum number of retry attempts
            delay_ms: Initial delay in milliseconds
            backoff_factor: Multiplier for successive delays
            jitter_ms: Random jitter in milliseconds to add to delay
            retryable_errors: Tuple of exception types to retry
        
        Returns:
            Decorated function with retry logic
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            def wrapper(*args, **kwargs) -> T:
                last_exception = None
                current_delay_ms = delay_ms
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except retryable_errors as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms > 0 else 0
                            sleep_time = (current_delay_ms + jitter) / 1000.0
                            time.sleep(max(0, sleep_time))
                            current_delay_ms *= backoff_factor
                        else:
                            break
                
                raise RetryExhaustedError(last_exception, max_attempts)
                
            return wrapper
        
        return decorator
    ```

    ### 3. Circuit Breaker Pattern

    ```python
    # In core/errors/circuit_breaker.py
    import time
    from enum import Enum
    from typing import Callable, TypeVar, Any, Dict
    import threading

    T = TypeVar('T')

    class CircuitState(Enum):
        CLOSED = "closed"       # Normal operation, requests pass through
        OPEN = "open"           # Circuit is tripped, fast-fail all requests  
        HALF_OPEN = "half_open" # Testing if service is healthy again

    class CircuitBreaker:
        """Implementation of the circuit breaker pattern."""
        
        def __init__(
            self,
            failure_threshold: int = 5,
            reset_timeout_seconds: float = 30.0,
            half_open_max_calls: int = 1
        ):
            self.failure_threshold = failure_threshold
            self.reset_timeout_seconds = reset_timeout_seconds
            self.half_open_max_calls = half_open_max_calls
            
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = 0
            self.half_open_calls = 0
            self._lock = threading.RLock()
        
        def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
            """Execute function with circuit breaker protection."""
            with self._lock:
                if self.state == CircuitState.OPEN:
                    if time.time() - self.last_failure_time >= self.reset_timeout_seconds:
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                    else:
                        raise CircuitOpenError("Circuit breaker is open")
                
                if self.state == CircuitState.HALF_OPEN and self.half_open_calls >= self.half_open_max_calls:
                    raise CircuitOpenError("Circuit breaker is at max half-open calls")
                
                if self.state == CircuitState.HALF_OPEN:
                    self.half_open_calls += 1
            
            try:
                result = func(*args, **kwargs)
                
                with self._lock:
                    if self.state == CircuitState.HALF_OPEN:
                        self.failure_count = 0
                        self.state = CircuitState.CLOSED
                    elif self.state == CircuitState.CLOSED:
                        self.failure_count = 0
                
                return result
                
            except Exception as e:
                with self._lock:
                    self.last_failure_time = time.time()
                    self.failure_count += 1
                    
                    if (self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold) or \
                       self.state == CircuitState.HALF_OPEN:
                        self.state = CircuitState.OPEN
                
                raise e

    class CircuitOpenError(Exception):
        """Error when circuit breaker is open."""
        pass

    # Global circuit breaker registry
    _circuit_breakers: Dict[str, CircuitBreaker] = {}
    _registry_lock = threading.RLock()

    def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
        """Get or create a named circuit breaker."""
        with _registry_lock:
            if name not in _circuit_breakers:
                _circuit_breakers[name] = CircuitBreaker(**kwargs)
            return _circuit_breakers[name]
    ```

    ### 4. Async Support

    ```python
    # In core/abcs/async_execution.py
    from abc import ABC, abstractmethod
    from typing import Generic, TypeVar, Awaitable
    from .execution_context import ExecutionContextABC
    from .artifact import ArtifactABC
    from .result import ResultABC

    T = TypeVar('T')
    U = TypeVar('U')

    class AsyncRunnableABC(Generic[T, U], ABC):
        """Abstract base class for asynchronous runnable components."""
        
        SCHEMA_VERSION = "1.0.0"
        
        @abstractmethod
        async def run(
            self, 
            input: ArtifactABC[T], 
            context: ExecutionContextABC
        ) -> ResultABC[U]:
            """Execute the component asynchronously."""
            pass

    # In protocols/testing/async_execution.py
    from typing import Protocol, TypeVar, Generic, Awaitable, runtime_checkable
    from .execution_context import ExecutionContext
    from .artifact import Artifact
    from .result import Result

    T = TypeVar('T')
    U = TypeVar('U')

    @runtime_checkable
    class AsyncRunnable(Protocol[T, U]):
        """Protocol for asynchronous runnable components."""
        
        __protocol_version__ = "1.0.0"
        
        async def run(
            self, 
            input: Artifact[T], 
            context: ExecutionContext
        ) -> Result[U]:
            """Execute the component asynchronously."""
            ...
    ```

    ### 5. Eventing System

    ```python
    # In core/events/event_bus.py
    from typing import Dict, List, Callable, Any, Set, Optional
    from uuid import UUID, uuid4
    import asyncio
    import inspect
    from dataclasses import dataclass, field
    import logging

    logger = logging.getLogger(__name__)

    @dataclass
    class EventSubscription:
        """Subscription to an event."""
        id: UUID
        event_type: str
        callback: Callable
        is_async: bool = False
        filter_patterns: Dict[str, Any] = field(default_factory=dict)

    class EventBus:
        """Simple event bus for publishing and subscribing to events."""
        
        def __init__(self):
            self._subscriptions: Dict[str, List[EventSubscription]] = {}
            self._all_subscriptions: Dict[UUID, EventSubscription] = {}
        
        def subscribe(
            self, 
            event_type: str, 
            callback: Callable,
            **filter_patterns
        ) -> UUID:
            """Subscribe to an event type.
            
            Args:
                event_type: Type of event to subscribe to
                callback: Function to call when event occurs
                filter_patterns: Optional key-value filters for event payload
                
            Returns:
                Subscription ID that can be used to unsubscribe
            """
            is_async = asyncio.iscoroutinefunction(callback)
            
            subscription = EventSubscription(
                id=uuid4(),
                event_type=event_type,
                callback=callback,
                is_async=is_async,
                filter_patterns=filter_patterns
            )
            
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []
            
            self._subscriptions[event_type].append(subscription)
            self._all_subscriptions[subscription.id] = subscription
            
            return subscription.id
        
        def unsubscribe(self, subscription_id: UUID) -> bool:
            """Unsubscribe from events.
            
            Args:
                subscription_id: ID returned from subscribe
                
            Returns:
                True if unsubscribed, False if subscription not found
            """
            if subscription_id not in self._all_subscriptions:
                return False
            
            subscription = self._all_subscriptions[subscription_id]
            self._subscriptions[subscription.event_type].remove(subscription)
            del self._all_subscriptions[subscription_id]
            
            return True
        
        def _matches_filters(self, event_data: Dict[str, Any], filter_patterns: Dict[str, Any]) -> bool:
            """Check if event data matches filter patterns."""
            for key, pattern in filter_patterns.items():
                if key not in event_data:
                    return False
                
                value = event_data[key]
                
                if callable(pattern):
                    # Pattern is a predicate function
                    if not pattern(value):
                        return False
                elif pattern != value:
                    return False
                
            return True
        
        def publish(self, event_type: str, **event_data):
            """Publish an event synchronously.
            
            Args:
                event_type: Type of event
                event_data: Key-value data for the event
            """
            if event_type not in self._subscriptions:
                return
            
            for subscription in self._subscriptions[event_type]:
                if not self._matches_filters(event_data, subscription.filter_patterns):
                    continue
                
                try:
                    if subscription.is_async:
                        # Create a task for async handlers but don't wait
                        asyncio.create_task(subscription.callback(event_type, **event_data))
                    else:
                        subscription.callback(event_type, **event_data)
                except Exception as e:
                    logger.exception(f"Error in event handler for {event_type}: {e}")
        
        async def publish_async(self, event_type: str, **event_data):
            """Publish an event and wait for all async handlers to complete.
            
            Args:
                event_type: Type of event
                event_data: Key-value data for the event
            """
            if event_type not in self._subscriptions:
                return
            
            async_tasks = []
            
            for subscription in self._subscriptions[event_type]:
                if not self._matches_filters(event_data, subscription.filter_patterns):
                    continue
                
                try:
                    if subscription.is_async:
                        task = asyncio.create_task(subscription.callback(event_type, **event_data))
                        async_tasks.append(task)
                    else:
                        subscription.callback(event_type, **event_data)
                except Exception as e:
                    logger.exception(f"Error in event handler for {event_type}: {e}")
            
            if async_tasks:
                await asyncio.gather(*async_tasks, return_exceptions=True)

    # Global event bus instance
    _default_event_bus = EventBus()

    def get_event_bus() -> EventBus:
        """Get the global event bus instance."""
        return _default_event_bus
    ```

    ### 6. Capability-Based Security Model

    ```python
    # In core/security/capabilities.py
    from typing import Dict, Set, List, Optional
    from enum import Enum, auto
    import os
    import re

    class CapabilityType(Enum):
        """Types of capabilities."""
        FILE_READ = auto()
        FILE_WRITE = auto()
        NETWORK_CONNECT = auto()
        DATABASE_READ = auto()
        DATABASE_WRITE = auto()
        REGISTRY_READ = auto()
        REGISTRY_WRITE = auto()
        ARTIFACT_READ = auto()
        ARTIFACT_WRITE = auto()
        EXTERNAL_COMMAND = auto()
        SECRET_ACCESS = auto()

    class Capability:
        """A capability represents permission to access a specific resource."""
        
        def __init__(
            self, 
            type: CapabilityType, 
            resource: str,
            conditions: Optional[Dict[str, str]] = None
        ):
            self.type = type
            self.resource = resource
            self.conditions = conditions or {}
        
        def __eq__(self, other):
            if not isinstance(other, Capability):
                return False
            return (
                self.type == other.type and
                self.resource == other.resource and
                self.conditions == other.conditions
            )
        
        def __hash__(self):
            return hash((self.type, self.resource, frozenset(self.conditions.items())))
        
        def __str__(self):
            cond_str = ", ".join(f"{k}={v}" for k, v in self.conditions.items())
            return f"{self.type.name}:{self.resource}{{{cond_str}}}" if cond_str else f"{self.type.name}:{self.resource}"
        
        def matches(self, other: 'Capability') -> bool:
            """Check if this capability matches another (potentially with wildcards)."""
            if self.type != other.type:
                return False
            
            # Check resource pattern matching
            if not self._match_resource_pattern(self.resource, other.resource):
                return False
            
            # Check conditions
            for k, v in self.conditions.items():
                if k not in other.conditions:
                    return False
                if not self._match_pattern(v, other.conditions[k]):
                    return False
                
            return True
        
        def _match_resource_pattern(self, pattern: str, value: str) -> bool:
            """Match resource patterns with glob-like syntax."""
            # Convert glob pattern to regex
            regex_pattern = pattern.replace(".", "\\.").replace("*", ".*").replace("?", ".")
            return bool(re.fullmatch(regex_pattern, value))
        
        def _match_pattern(self, pattern: str, value: str) -> bool:
            """Match condition patterns with simple wildcards."""
            # Convert glob pattern to regex
            regex_pattern = pattern.replace(".", "\\.").replace("*", ".*").replace("?", ".")
            return bool(re.fullmatch(regex_pattern, value))

    class CapabilitySet:
        """A set of capabilities that can be granted to a component."""
        
        def __init__(self, capabilities: Optional[List[Capability]] = None):
            self._capabilities: Set[Capability] = set(capabilities or [])
        
        def add(self, capability: Capability):
            """Add a capability to the set."""
            self._capabilities.add(capability)
        
        def remove(self, capability: Capability):
            """Remove a capability from the set."""
            self._capabilities.discard(capability)
        
        def has_capability(self, requested: Capability) -> bool:
            """Check if this set contains a capability matching the requested one."""
            for cap in self._capabilities:
                if cap.matches(requested):
                    return True
            return False
        
        def __iter__(self):
            return iter(self._capabilities)
        
        def __len__(self):
            return len(self._capabilities)

    class CapabilityContext:
        """Context for checking and enforcing capabilities."""
        
        def __init__(self, capability_set: CapabilitySet):
            self._capability_set = capability_set
        
        def check_file_read(self, path: str):
            """Check if component has permission to read a file."""
            cap = Capability(CapabilityType.FILE_READ, path)
            if not self._capability_set.has_capability(cap):
                raise CapabilityError(f"Missing capability: {cap}")
        
        def check_file_write(self, path: str):
            """Check if component has permission to write a file."""
            cap = Capability(CapabilityType.FILE_WRITE, path)
            if not self._capability_set.has_capability(cap):
                raise CapabilityError(f"Missing capability: {cap}")
        
        def check_network_connect(self, host: str, port: int):
            """Check if component has permission to connect to network."""
            cap = Capability(
                CapabilityType.NETWORK_CONNECT, 
                f"{host}:{port}"
            )
            if not self._capability_set.has_capability(cap):
                raise CapabilityError(f"Missing capability: {cap}")
        
        def check_database(self, db_name: str, operation: str):
            """Check if component has permission to access database."""
            cap_type = (
                CapabilityType.DATABASE_READ if operation.lower() == "read"
                else CapabilityType.DATABASE_WRITE
            )
            cap = Capability(cap_type, db_name)
            if not self._capability_set.has_capability(cap):
                raise CapabilityError(f"Missing capability: {cap}")
        
        def check_registry(self, registry_name: str, operation: str):
            """Check if component has permission to access registry."""
            cap_type = (
                CapabilityType.REGISTRY_READ if operation.lower() == "read"
                else CapabilityType.REGISTRY_WRITE
            )
            cap = Capability(cap_type, registry_name)
            if not self._capability_set.has_capability(cap):
                raise CapabilityError(f"Missing capability: {cap}")
        
        def check_artifact(self, artifact_id: str, operation: str):
            """Check if component has permission to access artifact."""
            cap_type = (
                CapabilityType.ARTIFACT_READ if operation.lower() == "read"
                else CapabilityType.ARTIFACT_WRITE
            )
            cap = Capability(cap_type, artifact_id)
            if not self._capability_set.has_capability(cap):
                raise CapabilityError(f"Missing capability: {cap}")
        
        def check_external_command(self, command: str):
            """Check if component has permission to execute external command."""
            cap = Capability(CapabilityType.EXTERNAL_COMMAND, command)
            if not self._capability_set.has_capability(cap):
                raise CapabilityError(f"Missing capability: {cap}")
        
        def check_secret_access(self, secret_name: str):
            """Check if component has permission to access a secret."""
            cap = Capability(CapabilityType.SECRET_ACCESS, secret_name)
            if not self._capability_set.has_capability(cap):
                raise CapabilityError(f"Missing capability: {cap}")

    class CapabilityError(Exception):
        """Error when a component requests a capability it doesn't have."""
        pass
    ```

    ---

    ## Configuration System

    The OmniBase configuration system uses a layered approach with clear precedence rules, allowing flexibility while maintaining consistent behavior across environments. Here's an expanded view of the configuration architecture:

    ### Configuration Sources (Highest to Lowest Precedence)

    1. **Command-line arguments** - Override all other sources
    2. **Environment variables** - Prefixed with `OMNIBASE_`
    3. **Project-level configuration** - `./omnibase.yml`
    4. **User-level configuration** - `~/.config/omnibase/config.yml`
    5. **System-level configuration** - `/etc/omnibase/config.yml`
    6. **Default values** - Hardcoded defaults as fallback

    Configuration is merged at runtime, with higher-precedence sources overriding lower ones. Array values can be appended rather than replaced by using the `+array:` prefix.

    Example config (`omnibase.yml`):
    ```yaml
    validators:
      tags:
        - pre-commit
        - schema
      ignore:
        - build/
        - tmp/
    formatters:
      human:
        color: true
        emoji: true
    registry:
      cache_ttl: 3600
    ```

    ### Schema Validation

    All configuration is validated against a schema before use, ensuring early detection of misconfigurations:

    ```python
    from pydantic import BaseModel, Field
    from typing import List, Optional, Dict, Any, Union

    class ValidatorConfig(BaseModel):
        tags: List[str] = Field(default_factory=list)
        ignore: List[str] = Field(default_factory=list)
        concurrency: int = 4

    class FormatterConfig(BaseModel):
        color: bool = True
        emoji: bool = True

    class FormatterConfigs(BaseModel):
        human: FormatterConfig = Field(default_factory=FormatterConfig)
        # other formatters...

    class OmniBaseConfig(BaseModel):
        validators: ValidatorConfig = Field(default_factory=ValidatorConfig)
        formatters: FormatterConfigs = Field(default_factory=FormatterConfigs)
        # other sections...
        
        class Config:
            extra = "forbid"  # Prevent unknown fields
    ```

    ### Dynamic Reloading

    For long-running services, configuration can be dynamically reloaded without restart:

    ```python
    class ConfigManager:
        def __init__(self, config_path: str):
            self.config_path = config_path
            self.config = self._load_config()
            self.last_modified = os.path.getmtime(config_path)
        
        def _load_config(self) -> OmniBaseConfig:
            # Load and validate config
            # ...
            
        def get_config(self) -> OmniBaseConfig:
            # Check if config file has changed
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime > self.last_modified:
                try:
                    self.config = self._load_config()
                    self.last_modified = current_mtime
                except Exception as e:
                    # Log error but keep using existing config
                    pass
            
            return self.config
    ```

    ### Environment Variable Mapping

    Environment variables are automatically mapped to configuration paths using dot notation:

    ```
    OMNIBASE_VALIDATORS_CONCURRENCY=8 -> validators.concurrency = 8
    OMNIBASE_FORMATTERS_HUMAN_COLOR=false -> formatters.human.color = false
    ```

    This provides a consistent override mechanism across all deployment environments.

    ---

    ## Structured Observability Integration

    ```python
    # core/observability/logging.py
    import logging
    from typing import Dict, Any, Optional
    import json
    import datetime
    import threading
    from uuid import uuid4

    class StructuredLogRecord(logging.LogRecord):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.correlation_id = getattr(threading.current_thread(), 'correlation_id', None)
            self.component_id = None
            self.component_version = None
            self.execution_id = None

    class StructuredLogger(logging.Logger):
        def makeRecord(self, *args, **kwargs):
            return StructuredLogRecord(*args, **kwargs)

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
                "correlation_id": getattr(record, "correlation_id", None),
                "component_id": getattr(record, "component_id", None),
                "component_version": getattr(record, "component_version", None),
                "execution_id": getattr(record, "execution_id", None),
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = {
                    "type": record.exc_info[0].__name__,
                    "message": str(record.exc_info[1]),
                    "traceback": self.formatException(record.exc_info),
                }
                
            # Add any extra attributes
            for key, value in record.__dict__.items():
                if key not in ["args", "asctime", "created", "exc_info", "exc_text", 
                              "filename", "funcName", "id", "levelname", "levelno",
                              "lineno", "module", "msecs", "message", "msg", 
                              "name", "pathname", "process", "processName", 
                              "relativeCreated", "stack_info", "thread", "threadName",
                              "correlation_id", "component_id", "component_version", 
                              "execution_id"]:
                    log_data[key] = value
                    
            return json.dumps(log_data)

    # Set up logging
    def configure_structured_logging(level=logging.INFO):
        logging.setLoggerClass(StructuredLogger)
        logger = logging.getLogger("omnibase")
        logger.setLevel(level)
        
        # Console handler with JSON formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)
        
        return logger

    # core/observability/metrics.py
    from typing import Dict, Any, Optional, List, Union
    import time

    class Metric:
        def __init__(self, name: str, value: Union[int, float], tags: Dict[str, str] = None):
            self.name = name
            self.value = value
            self.tags = tags or {}
            self.timestamp = time.time()
        
        def to_dict(self) -> Dict[str, Any]:
            return {
                "name": self.name,
                "value": self.value,
                "tags": self.tags,
                "timestamp": self.timestamp,
            }

    class MetricsCollector:
        _instance = None
        
        @classmethod
        def get_instance(cls):
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
        
        def add_reporter(self, reporter):
            self.reporters.append(reporter)
        
        def record(self, metric: Metric):
            for reporter in self.reporters:
                reporter.report(metric)

    class StdoutMetricsReporter:
        def report(self, metric: Metric):
            print(f"METRIC: {metric.to_dict()}")

    class TimerContext:
        def __init__(self, name: str, tags: Dict[str, str] = None):
            self.name = name
            self.tags = tags or {}
            self.start_time = None
            
        def __enter__(self):
            self.start_time = time.time()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            metric = Metric(
                name=f"{self.name}.duration",
                value=duration,
                tags=self.tags
            )
            MetricsCollector.get_instance().record(metric)

    # core/observability/tracing.py
    import time
    from typing import Dict, Any, Optional, List
    import uuid
    import threading
    import contextvars
    import json

    # Use contextvars for context propagation across async boundaries
    current_span = contextvars.ContextVar('current_span', default=None)

    class Span:
        def __init__(
            self, 
            name: str, 
            parent_id: Optional[str] = None,
            trace_id: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None
        ):
            self.name = name
            self.span_id = str(uuid.uuid4())
            self.trace_id = trace_id or str(uuid.uuid4())
            self.parent_id = parent_id
            self.tags = tags or {}
            self.start_time = time.time()
            self.end_time = None
            self.events = []
            
        def add_event(self, name: str, attributes: Dict[str, Any] = None):
            self.events.append({
                "name": name,
                "timestamp": time.time(),
                "attributes": attributes or {}
            })
            
        def set_tag(self, key: str, value: str):
            self.tags[key] = value
            
        def finish(self):
            self.end_time = time.time()
            TraceReporter.get_instance().report(self)
            
        def to_dict(self) -> Dict[str, Any]:
            return {
                "name": self.name,
                "span_id": self.span_id,
                "trace_id": self.trace_id,
                "parent_id": self.parent_id,
                "tags": self.tags,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration": (self.end_time - self.start_time) if self.end_time else None,
                "events": self.events
            }

    class TraceReporter:
        _instance = None
        
        @classmethod
        def get_instance(cls):
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
        
        def __init__(self):
            self.reporters = []
        
        def add_reporter(self, reporter):
            self.reporters.append(reporter)
        
        def report(self, span: Span):
            for reporter in self.reporters:
                reporter.report(span)

    class StdoutTraceReporter:
        def report(self, span: Span):
            print(f"SPAN: {json.dumps(span.to_dict())}")

    def start_span(name: str, tags: Dict[str, str] = None) -> Span:
        parent = current_span.get()
        
        span = Span(
            name=name,
            parent_id=parent.span_id if parent else None,
            trace_id=parent.trace_id if parent else None,
            tags=tags
        )
        
        token = current_span.set(span)
        span._token = token  # Keep reference to token
        
        return span

    class TracingContext:
        def __init__(self, name: str, tags: Dict[str, str] = None):
            self.name = name
            self.tags = tags or {}
            self.span = None
            
        def __enter__(self):
            self.span = start_span(self.name, self.tags)
            return self.span
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.span.set_tag("error", "true")
                self.span.set_tag("error.type", exc_type.__name__)
                self.span.set_tag("error.message", str(exc_val))
            
            self.span.finish()
            
            # Restore parent span
            parent = current_span.get()
            if parent != self.span:  # Span was changed within the context
                pass  # Leave it unchanged
            else:
                # Reset to previous parent
                current_span.reset(self.span._token)
    ```

    ---

    ## Future Roadmap & Research Areas

    While the current design provides a solid foundation, several advanced areas deserve exploration in future iterations:

    ### 1. Machine Learning Integration

    - **Artifact Classification:** Use ML to automatically classify and tag artifacts based on content.
    - **Anomaly Detection:** Learn normal patterns of validator/tool behavior to flag unusual results.
    - **Optimization Suggestions:** Analyze pipelines to suggest more efficient ordering or parallelization.
    - **Predictive Maintenance:** Predict when components might fail based on error patterns.

    ### 2. Data Processing Pipelines

    - **Stream Processing:** Support continuous data streams as both inputs and outputs.
    - **Windowing Operations:** Allow validators/tools to operate on time or count windows of data.
    - **Incremental Processing:** Enable processing only deltas/changes rather than full artifacts.
    - **Backpressure Mechanisms:** Advanced flow control for high-volume data pipelines.

    ### 3. Advanced Security Models

    - **Formal Verification:** Use formal methods to verify security properties of critical components.
    - **Dynamic Privilege Adjustment:** Modify permissions based on execution history and risk assessment.
    - **Taint Tracking:** Track data flow to detect potentially unsafe transformations.
    - **Homomorphic Operations:** Enable computations on encrypted data without decryption.

    ### 4. Distributed System Enhancements

    - **Consensus Algorithms:** Support for distributed consensus on registry state.
    - **Vector Clocks:** Implement vector clocks for ordering events in distributed environments.
    - **Gossip Protocols:** Efficient information dissemination across federated registries.
    - **Conflict-Free Replicated Data Types (CRDTs):** For eventual consistency in distributed registries.

    ### 5. Human-Agent Collaboration Models

    - **Feedback Loops:** Structured mechanisms for humans to provide feedback on agent-generated artifacts.
    - **Explanation Generation:** Generate human-understandable explanations for complex transformations.
    - **Intent Recognition:** Infer user intent to suggest appropriate validator/tool chains.
    - **Trust Calibration:** Adjust autonomy based on historical performance and human feedback.

    These research areas represent directions for evolution beyond the core architecture, focusing on advanced capabilities that may become critical as the system matures.

    ---

    ## Immediate Implementation Priorities

    To transform this design into working code, the following components should be prioritized:

    1. **Core Protocol Definitions**: Implement the basic `Artifact`, `ExecutionContext`, and `Result` protocols with proper versioning.

    2. **Registry Implementation**: Build the basic registry infrastructure with metadata validation and querying capabilities.

    3. **Orchestrator Framework**: Implement the orchestrator pattern with support for both sync and async execution.

    4. **Error Handling Framework**: Establish the error taxonomy and structured error objects.

    5. **CLI Foundation**: Create the CLI entry points with the unified output formats.

    6. **Security Model**: Implement the capability-based security model for sandbox execution.

    7. **Observability Foundations**: Set up structured logging, metrics collection, and tracing frameworks.

    8. **Testing Framework**: Build test utilities for validating protocol compliance and component behavior.

    With these foundational components in place, the system can begin to support real validators and tools while maintaining the architecture principles established in the design.

    ---

> This document is a living spec. Submit PRs or direct edits for review.

