# ONEX Canonical Error Taxonomy

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the canonical error codes, categories, and handling patterns for all ONEX validation failures  
> **Audience:** Tool developers, CI/CD systems, node authors, maintainers  
> **Enforcement:** All ONEX tools and validators must use these error codes

---

## Overview

This document defines the canonical error taxonomy for the ONEX system. All validation failures, CI errors, and tool errors must use these standardized error codes to ensure consistent error handling, reporting, and automation.

## Error Code Structure

Error codes follow the pattern: `{CATEGORY}{NUMBER}`

- **Category:** 2-3 letter prefix indicating error domain
- **Number:** 3-digit sequential number within category

Example: `SC001` = Schema Category, Error #001

## Error Categories

### Schema Validation (SC)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `SC001` | Invalid JSON/YAML syntax | Error | Fix syntax errors in file |
| `SC002` | Schema validation failed | Error | Ensure file matches required schema |
| `SC003` | Missing required field | Error | Add missing required field |
| `SC004` | Invalid field type | Error | Correct field type to match schema |
| `SC005` | Invalid enum value | Error | Use valid enum value from schema |
| `SC006` | Field value out of range | Error | Adjust value to be within valid range |
| `SC007` | Invalid pattern match | Error | Ensure field matches required pattern |
| `SC008` | Schema version mismatch | Warning | Update to compatible schema version |
| `SC009` | Deprecated field usage | Warning | Migrate to recommended field |
| `SC010` | Unknown field present | Warning | Remove unknown field or update schema |

### Lifecycle Management (LC)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `LC001` | Invalid lifecycle value | Error | Use one of: draft, active, deprecated, archived |
| `LC002` | Missing required field for lifecycle state | Error | Add required field (see lifecycle policy) |
| `LC003` | Invalid lifecycle transition | Error | Follow allowed transition rules |
| `LC004` | Missing approval for transition | Error | Obtain required approvals |
| `LC005` | Deprecated node missing replacement | Error | Add `deprecated_by` field with valid UUID |
| `LC006` | Archived node missing reason | Error | Add `archived_reason` field |
| `LC007` | Draft node in production registry | Warning | Move to development registry or promote |
| `LC008` | Lifecycle transition without notice | Warning | Provide required notice period |

### Metadata Validation (MD)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `MD001` | Missing metadata block | Error | Add ONEX metadata block to file |
| `MD002` | Invalid metadata format | Error | Fix metadata block format |
| `MD003` | Hash mismatch | Error | Regenerate hash or fix content |
| `MD004` | Invalid UUID format | Error | Use RFC 4122-compliant UUID |
| `MD005` | Invalid timestamp format | Error | Use ISO 8601 timestamp format |
| `MD006` | Missing version field | Error | Add semantic version field |
| `MD007` | Invalid version format | Error | Use semantic versioning (x.y.z) |
| `MD008` | Namespace violation | Error | Use valid namespace pattern |
| `MD009` | Duplicate UUID detected | Error | Generate unique UUID |
| `MD010` | Metadata version incompatible | Warning | Update to compatible metadata version |

### File System (FS)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `FS001` | File not found | Error | Ensure file exists at specified path |
| `FS002` | Directory not found | Error | Create directory or fix path |
| `FS003` | Permission denied | Error | Fix file/directory permissions |
| `FS004` | File is empty | Warning | Add content or mark as intentionally empty |
| `FS005` | File too large | Warning | Reduce file size or split content |
| `FS006` | Invalid file extension | Warning | Use expected file extension |
| `FS007` | Symbolic link detected | Warning | Use direct file reference |
| `FS008` | Binary file in text context | Error | Use appropriate handler for binary files |
| `FS009` | Encoding error | Error | Fix file encoding (use UTF-8) |
| `FS010` | Path too long | Error | Shorten file path |

### Registry Management (RG)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `RG001` | Artifact not found in registry | Error | Register artifact or fix reference |
| `RG002` | Duplicate artifact registration | Error | Use unique artifact identifier |
| `RG003` | Invalid artifact type | Error | Use supported artifact type |
| `RG004` | Missing .onextree file | Error | Generate .onextree manifest |
| `RG005` | .onextree out of sync | Error | Regenerate .onextree manifest |
| `RG006` | Circular dependency detected | Error | Remove circular dependencies |
| `RG007` | Missing dependency | Error | Add missing dependency or remove reference |
| `RG008` | Version conflict | Error | Resolve version compatibility issues |
| `RG009` | Registry corruption detected | Error | Rebuild registry from source |
| `RG010` | WIP artifact in production | Warning | Complete development or remove from production |

### State Contract (ST)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `ST001` | Invalid state contract format | Error | Fix state contract YAML/JSON format |
| `ST002` | Missing input state definition | Error | Define input state schema |
| `ST003` | Missing output state definition | Error | Define output state schema |
| `ST004` | State contract version mismatch | Error | Update state contract version |
| `ST005` | Invalid state transition | Error | Ensure valid state transformation |
| `ST006` | Required state field missing | Error | Add required state field |
| `ST007` | State field type mismatch | Error | Fix state field type |
| `ST008` | State contract not found | Error | Create or reference valid state contract |
| `ST009` | Incompatible state contracts | Error | Ensure state contract compatibility |
| `ST010` | State validation failed | Error | Fix state data to match contract |

### Testing (TS)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `TS001` | Test coverage below threshold | Error | Increase test coverage |
| `TS002` | Test failure detected | Error | Fix failing tests |
| `TS003` | Missing test file | Warning | Add test file for component |
| `TS004` | Invalid test structure | Error | Fix test file structure |
| `TS005` | Test timeout | Error | Optimize test performance or increase timeout |
| `TS006` | Mock dependency failure | Error | Fix mock configuration |
| `TS007` | Fixture loading error | Error | Fix test fixture |
| `TS008` | Test data validation failed | Error | Fix test data format |
| `TS009` | Integration test failure | Error | Fix integration test setup |
| `TS010` | Performance test failure | Warning | Optimize performance or adjust thresholds |

### CI/CD Pipeline (CI)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `CI001` | Build failure | Error | Fix build configuration or dependencies |
| `CI002` | Linting failure | Error | Fix code style issues |
| `CI003` | Type checking failure | Error | Fix type annotations |
| `CI004` | Security scan failure | Error | Address security vulnerabilities |
| `CI005` | Dependency vulnerability | Warning | Update vulnerable dependencies |
| `CI006` | Pre-commit hook failure | Error | Fix pre-commit hook issues |
| `CI007` | Deployment failure | Error | Fix deployment configuration |
| `CI008` | Environment setup failure | Error | Fix CI environment configuration |
| `CI009` | Artifact upload failure | Warning | Fix artifact storage configuration |
| `CI010` | Notification failure | Warning | Fix notification configuration |

### Node Execution (NE)

| Code | Description | Severity | Resolution |
|------|-------------|----------|------------|
| `NE001` | Node execution failure | Error | Fix node implementation |
| `NE002` | Invalid input state | Error | Provide valid input state |
| `NE003` | Output state validation failed | Error | Fix node output generation |
| `NE004` | Node timeout | Error | Optimize node performance or increase timeout |
| `NE005` | Resource limit exceeded | Error | Optimize resource usage |
| `NE006` | Dependency unavailable | Error | Ensure dependencies are available |
| `NE007` | Runtime error | Error | Fix runtime exception in node |
| `NE008` | Memory limit exceeded | Error | Optimize memory usage |
| `NE009` | Network error | Error | Fix network connectivity issues |
| `NE010` | Permission error | Error | Fix execution permissions |

## Error Severity Levels

### Error
- **Impact:** Blocks execution or produces incorrect results
- **Action:** Must be fixed before proceeding
- **CI Behavior:** Fails the build/pipeline

### Warning
- **Impact:** May cause issues but doesn't block execution
- **Action:** Should be addressed but doesn't block deployment
- **CI Behavior:** Logs warning but allows pipeline to continue

### Info
- **Impact:** Informational only
- **Action:** No action required
- **CI Behavior:** Logs information for reference

## Error Response Format

All tools must return errors in this standardized format:

```json
{
  "error_code": "SC002",
  "severity": "error",
  "message": "Schema validation failed",
  "details": "Field 'lifecycle' is required but missing",
  "file_path": "src/example/node.py",
  "line_number": 15,
  "column_number": 5,
  "suggestion": "Add 'lifecycle: active' to metadata block",
  "documentation_url": "https://docs.example.com/errors/SC002"
}
```

### Required Fields
- `error_code`: Canonical error code from this taxonomy
- `severity`: One of: error, warning, info
- `message`: Human-readable error description
- `file_path`: Path to file where error occurred (if applicable)

### Optional Fields
- `details`: Additional context about the error
- `line_number`: Line number where error occurred
- `column_number`: Column number where error occurred
- `suggestion`: Suggested fix for the error
- `documentation_url`: Link to detailed error documentation

## Tool Integration

### CLI Tools
All CLI tools must:
1. Use canonical error codes
2. Return appropriate exit codes (0=success, 1=error, 2=warning)
3. Support `--format json` for machine-readable output
4. Include error code in human-readable output

### CI/CD Integration
CI systems must:
1. Parse error codes to determine build status
2. Aggregate errors by category for reporting
3. Support error filtering and suppression
4. Generate error reports with canonical codes

### IDE Integration
IDE plugins should:
1. Display errors with canonical codes
2. Provide quick fixes based on error suggestions
3. Link to error documentation
4. Support error filtering by severity

## Error Code Management

### Adding New Error Codes
1. Choose appropriate category prefix
2. Use next sequential number in category
3. Update this document with error details
4. Add error to validation tools
5. Create documentation page for error

### Deprecating Error Codes
1. Mark error as deprecated in this document
2. Maintain backward compatibility for 6 months
3. Update tools to use replacement error code
4. Remove deprecated code after deprecation period

### Error Code Versioning
- Error taxonomy follows semantic versioning
- Breaking changes require major version bump
- New error codes are minor version changes
- Documentation updates are patch version changes

## Examples

### Schema Validation Error
```bash
$ onex validate node.py
ERROR [SC002]: Schema validation failed
  File: src/example/node.py:15:5
  Details: Field 'lifecycle' is required but missing
  Suggestion: Add 'lifecycle: active' to metadata block
  Documentation: https://docs.example.com/errors/SC002
```

### Lifecycle Error
```bash
$ onex validate deprecated_node.py
ERROR [LC005]: Deprecated node missing replacement
  File: src/legacy/parser.py:12:1
  Details: Node marked as deprecated but 'deprecated_by' field is missing
  Suggestion: Add 'deprecated_by: <replacement-uuid>' to metadata
  Documentation: https://docs.example.com/errors/LC005
```

### Registry Error
```bash
$ onex registry validate
ERROR [RG005]: .onextree out of sync
  File: .onextree:45
  Details: File 'src/new_node.py' exists but not listed in .onextree
  Suggestion: Run 'onex run tree_generator_node' to update manifest
  Documentation: https://docs.example.com/errors/RG005
```

## Integration with ONEX CLI

### Error Validation Commands

```bash
# Validate specific error categories
onex validate --error-categories SC,MD,LC

# Check for specific error codes
onex validate --error-codes SC002,MD001

# Generate error report
onex validate --format json > error_report.json

# Filter by severity
onex validate --severity error

# Suppress specific errors
onex validate --suppress SC008,LC007
```

### Error Analysis

```bash
# Analyze error patterns
onex errors analyze --since "2025-01-01"

# Get error statistics
onex errors stats --by-category

# Export error taxonomy
onex errors taxonomy --format yaml > error_taxonomy.yaml
```

## Best Practices

### For Tool Developers

1. **Use canonical codes**: Always use error codes from this taxonomy
2. **Provide context**: Include file paths, line numbers, and suggestions
3. **Be consistent**: Use the same error code for the same type of issue
4. **Document errors**: Link to detailed error documentation
5. **Test error paths**: Ensure error handling is properly tested

### For CI/CD Integration

1. **Parse error codes**: Use error codes to determine build status
2. **Aggregate errors**: Group errors by category for reporting
3. **Support filtering**: Allow suppression of specific error codes
4. **Generate reports**: Create comprehensive error reports
5. **Track trends**: Monitor error patterns over time

### For Node Authors

1. **Understand error codes**: Familiarize yourself with common error codes
2. **Fix errors promptly**: Address errors as they occur
3. **Use suggestions**: Follow error suggestions for quick fixes
4. **Check documentation**: Refer to error documentation for details
5. **Test thoroughly**: Ensure your nodes pass all validations

---

## References

- [Lifecycle Policy](./lifecycle_policy.md)
- [Metadata Specification](./metadata.md)
- [Testing Standards](./testing.md)
- [Registry Management](./registry.md)

---

**Enforcement:** All ONEX tools and validators must implement this error taxonomy. Non-compliance will be flagged in code review and CI validation. 