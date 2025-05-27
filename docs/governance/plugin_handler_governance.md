# Plugin & Handler Governance

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define governance, review processes, and placement guidelines for handlers and plugins in the ONEX ecosystem  
> **Audience:** Contributors, maintainers, plugin developers, system architects  

---

## Overview

This document establishes the governance framework for handlers and plugins in the ONEX system, including review processes, placement guidelines, quality standards, and architectural review requirements. It ensures consistent quality, security, and maintainability across the ONEX ecosystem.

---

## Handler Classification & Placement Guidelines

### Core Handlers (Priority: 100)

**Definition:** Essential system functionality required for ONEX operation.

**Criteria:**
- Critical for system operation (e.g., `.onexignore`, `.gitignore`)
- No dependencies on external libraries beyond Python standard library
- Stable, well-tested functionality
- Used across multiple nodes and contexts
- Security-critical or performance-critical functionality

**Location:** `src/omnibase/handlers/`

**Examples:**
- `IgnoreFileHandler` - Processes `.onexignore` and `.gitignore` files
- System configuration handlers
- Security-related file processors

**Review Requirements:**
- Architectural review required
- Security review for any file system operations
- Performance impact assessment
- Comprehensive test coverage (>95%)
- Documentation review

### Runtime Handlers (Priority: 50)

**Definition:** Standard file type support for common ONEX ecosystem files.

**Criteria:**
- Handles common file types in ONEX ecosystem (`.py`, `.md`, `.yaml`)
- Well-established, stable functionality
- Minimal external dependencies (prefer standard library)
- Broad applicability across nodes
- Mature, production-ready implementations

**Location:** `src/omnibase/runtimes/onex_runtime/v1_0_0/handlers/`

**Examples:**
- `PythonHandler` - Processes Python files
- `MarkdownHandler` - Processes Markdown files
- `MetadataYAMLHandler` - Processes YAML metadata files

**Review Requirements:**
- Code review by 2+ maintainers
- Test coverage >90%
- Performance benchmarking for large files
- Documentation and usage examples
- Integration test validation

### Node-Local Handlers (Priority: 10)

**Definition:** Node-specific functionality that doesn't belong in shared locations.

**Criteria:**
- Specific to particular node's requirements
- Does not conflict with existing handlers
- Properly scoped to node directory
- Limited reusability outside the node context
- Experimental or specialized functionality

**Location:** `src/omnibase/nodes/{node_name}/v{version}/handlers/`

**Examples:**
- Node-specific file format processors
- Custom validation logic for node inputs
- Specialized transformation handlers

**Review Requirements:**
- Code review by 1+ maintainer
- Test coverage >80%
- Documentation within node
- No conflicts with existing handlers
- Proper scoping validation

### Plugin Handlers (Priority: 0)

**Definition:** Third-party or experimental functionality loaded via entry points.

**Criteria:**
- Third-party developed or experimental
- Loaded via setuptools entry points
- May have external dependencies
- Optional functionality
- Community-contributed or organization-specific

**Location:** External packages with entry point configuration

**Examples:**
- Organization-specific file processors
- Experimental format handlers
- Third-party integrations

**Review Requirements:**
- Plugin package review
- Entry point configuration validation
- Documentation and installation guide
- Security review for external dependencies
- Compatibility testing

---

## Review Process

### Standard Review Process

1. **Initial Submission**
   - PR created with complete PR template
   - All required checklist items completed
   - CI checks passing

2. **Automated Validation**
   - Pre-commit hooks pass
   - Handler metadata enforcement tests pass
   - Type checking and linting pass
   - Test coverage meets requirements

3. **Code Review**
   - Reviewer assignment based on handler type
   - Code quality and standards compliance
   - Test coverage and quality review
   - Documentation review

4. **Approval & Merge**
   - Required approvals obtained
   - Final CI validation
   - Merge to appropriate branch

### Architectural Review Process

**Triggers:** Changes requiring architectural review include:
- New protocols or interfaces
- Changes to core handler registry or plugin system
- Breaking changes to existing APIs
- New node types or major node modifications
- Changes to CI/CD pipeline or testing infrastructure
- New external dependencies
- Performance-critical changes
- Security-related changes

**Process:**
1. **Architectural Review Request**
   - Label PR with `needs-architectural-review`
   - Provide detailed architectural impact assessment
   - Include performance and security implications

2. **Review Committee**
   - Minimum 2 maintainers with architectural expertise
   - Domain expert if specialized knowledge required
   - Security expert for security-related changes

3. **Review Criteria**
   - Alignment with ONEX architectural principles
   - Impact on system performance and scalability
   - Security implications
   - Backward compatibility considerations
   - Long-term maintenance implications

4. **Decision & Documentation**
   - Approval/rejection with detailed rationale
   - Architectural decision record (ADR) if significant
   - Migration plan for breaking changes

---

## Quality Standards

### Code Quality Requirements

**All Handlers Must:**
- Implement all required metadata properties
- Follow canonical naming conventions
- Implement all required protocol methods
- Include comprehensive error handling
- Have proper type annotations
- Follow project coding standards

**Testing Requirements:**
- Core Handlers: >95% test coverage
- Runtime Handlers: >90% test coverage
- Node-Local Handlers: >80% test coverage
- Plugin Handlers: >70% test coverage

**Documentation Requirements:**
- Comprehensive docstrings
- Usage examples
- Supported file types documentation
- Migration guides for replacements
- API documentation updates

### Performance Standards

**Benchmarking Requirements:**
- Core and Runtime handlers must include performance benchmarks
- Large file handling tests (>1MB, >10MB)
- Memory usage profiling
- Concurrent access testing

**Performance Thresholds:**
- File processing: <100ms for files <1MB
- Memory usage: <50MB peak for typical operations
- No memory leaks in long-running operations

### Security Standards

**Security Review Required For:**
- File system operations
- External network access
- Data parsing from untrusted sources
- Cryptographic operations
- Privilege escalation

**Security Requirements:**
- Input validation and sanitization
- Safe file path handling
- Error message sanitization (no sensitive data leakage)
- Secure defaults
- Audit logging for security-relevant operations

---

## Conflict Resolution

### Handler Conflicts

**Priority-Based Resolution:**
1. Core Handlers (100) - Highest priority
2. Runtime Handlers (50) - Medium priority
3. Node-Local Handlers (10) - Low priority
4. Plugin Handlers (0) - Lowest priority

**Conflict Resolution Process:**
1. **Detection:** Registry detects conflicting handlers
2. **Notification:** Warning logged with conflict details
3. **Resolution:** Higher priority handler takes precedence
4. **Override:** Explicit override flag can force lower priority

**Best Practices:**
- Avoid conflicts through careful design
- Use specific file patterns when possible
- Document known conflicts and resolutions
- Provide migration paths for replaced handlers

### Dispute Resolution

**Process for Disputes:**
1. **Discussion:** Open discussion in PR or issue
2. **Mediation:** Maintainer mediation if needed
3. **Technical Committee:** Escalation to technical committee
4. **Final Decision:** Project lead final decision if needed

---

## Maintenance & Lifecycle

### Handler Lifecycle

**States:**
- **Active:** Fully supported and maintained
- **Deprecated:** Marked for removal, migration path provided
- **Legacy:** Maintained for compatibility only
- **Removed:** No longer available

**Deprecation Process:**
1. **Notice:** Deprecation notice in documentation and logs
2. **Migration:** Migration guide and tooling provided
3. **Grace Period:** Minimum 2 release cycles
4. **Removal:** Handler removed from codebase

### Maintenance Responsibilities

**Core Handlers:**
- Maintained by core team
- Regular security and performance reviews
- Immediate bug fix response

**Runtime Handlers:**
- Maintained by core team or designated maintainers
- Regular maintenance and updates
- Community contribution welcome

**Node-Local Handlers:**
- Maintained by node owners
- Core team provides guidance and review
- Node-specific maintenance schedule

**Plugin Handlers:**
- Maintained by plugin authors
- Community support and contribution
- Core team provides plugin framework support

---

## Entry Point Configuration

### Plugin Entry Points

**Configuration in `pyproject.toml`:**
```toml
[project.entry-points."omnibase.handlers"]
my_custom_handler = "my_package.handlers:MyCustomHandler"
```

**Configuration in `setup.cfg`:**
```ini
[options.entry_points]
omnibase.handlers =
    my_custom_handler = my_package.handlers:MyCustomHandler
```

### Discovery Mechanism

**Registry Discovery:**
- Automatic discovery via entry points
- Manual registration for development
- Environment variable overrides
- Configuration file registration

**Loading Order:**
1. Core handlers (built-in)
2. Runtime handlers (built-in)
3. Node-local handlers (if applicable)
4. Plugin handlers (entry points)

---

## Documentation Requirements

### Handler Documentation

**Required Documentation:**
- Handler purpose and scope
- Supported file types and patterns
- Configuration options
- Usage examples
- Performance characteristics
- Known limitations

**Location:**
- Core/Runtime: `docs/handlers/{handler_name}.md`
- Node-Local: `docs/nodes/{node_name}/handlers.md`
- Plugin: Plugin package documentation

### API Documentation

**Requirements:**
- Complete API reference
- Method signatures and return types
- Error conditions and handling
- Thread safety considerations
- Performance implications

---

## Compliance & Enforcement

### CI Enforcement

**Automated Checks:**
- Handler metadata enforcement
- Test coverage validation
- Performance regression detection
- Security vulnerability scanning
- Documentation completeness

**Enforcement Points:**
- Pre-commit hooks
- CI pipeline validation
- Release gate checks
- Periodic compliance audits

### Monitoring & Metrics

**Metrics Tracked:**
- Handler usage statistics
- Performance metrics
- Error rates and types
- Test coverage trends
- Security incident tracking

**Reporting:**
- Monthly handler health reports
- Performance trend analysis
- Security audit results
- Community contribution metrics

---

## Migration & Compatibility

### Backward Compatibility

**Requirements:**
- Maintain API compatibility within major versions
- Provide migration tools for breaking changes
- Document all compatibility implications
- Support legacy handlers during transition

### Migration Support

**Tools Provided:**
- Handler migration utilities
- Configuration conversion tools
- Automated testing for migrations
- Documentation and guides

**Process:**
1. **Assessment:** Impact analysis of changes
2. **Planning:** Migration strategy and timeline
3. **Implementation:** Migration tools and documentation
4. **Validation:** Testing and verification
5. **Deployment:** Phased rollout with monitoring

---

## Plugin Development Guidelines

### Plugin Package Structure

```
my_onex_plugin/
├── src/
│   └── my_onex_plugin/
│       ├── __init__.py
│       ├── handlers/
│       │   ├── __init__.py
│       │   └── my_handler.py
│       └── tests/
│           └── test_my_handler.py
├── pyproject.toml
├── README.md
└── LICENSE
```

### Plugin Registration

```python
# In my_handler.py
from omnibase.core.protocols import FileHandlerProtocol

class MyCustomHandler:
    """Custom handler for specific file types."""
    
    def can_handle(self, file_path: Path) -> bool:
        """Determine if this handler can process the file."""
        return file_path.suffix == '.myext'
    
    def process(self, file_path: Path, content: str) -> str:
        """Process the file content."""
        # Implementation here
        return processed_content
```

### Plugin Testing

```python
# In test_my_handler.py
import pytest
from my_onex_plugin.handlers.my_handler import MyCustomHandler

def test_can_handle():
    handler = MyCustomHandler()
    assert handler.can_handle(Path("test.myext"))
    assert not handler.can_handle(Path("test.txt"))

def test_process():
    handler = MyCustomHandler()
    result = handler.process(Path("test.myext"), "test content")
    assert result == "processed test content"
```

---

## Best Practices

### Handler Design

1. **Single Responsibility:** Each handler should handle one file type or pattern
2. **Fail Fast:** Validate inputs early and provide clear error messages
3. **Idempotent Operations:** Ensure operations can be safely repeated
4. **Resource Management:** Properly handle file handles and memory
5. **Error Handling:** Use ONEX error taxonomy and structured errors

### Performance Optimization

1. **Lazy Loading:** Load resources only when needed
2. **Caching:** Cache expensive operations appropriately
3. **Streaming:** Use streaming for large files
4. **Profiling:** Include performance benchmarks
5. **Memory Management:** Monitor and optimize memory usage

### Security Considerations

1. **Input Validation:** Validate all inputs thoroughly
2. **Path Sanitization:** Prevent path traversal attacks
3. **Privilege Minimization:** Use least privilege principle
4. **Audit Logging:** Log security-relevant operations
5. **Dependency Management:** Keep dependencies minimal and updated

---

## Conclusion

This governance framework ensures that handlers and plugins in the ONEX ecosystem maintain high quality, security, and performance standards while providing clear guidelines for contributors and maintainers. Regular review and updates of this document ensure it remains relevant and effective as the system evolves.

For questions about handler development or governance, please refer to the [Contributing Guide](../contributing.md) or reach out to the maintainer team.

---

## References

- [Handler Protocols](../reference-handlers-protocol.md)
- [Handler Registry](../reference-handlers-registry.md)
- [Handler Implementation](../guide-handlers-implementation.md)
- [Contributing Guidelines](../contributing.md)
- [Security Overview](../reference-security-overview.md)
- [Testing Standards](../testing.md)

---

**Note:** This governance framework is designed to balance innovation with stability, ensuring the ONEX ecosystem remains robust and extensible while maintaining high quality standards. 