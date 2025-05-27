<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: execution_context.md
version: 1.0.0
uuid: 88a3ea8a-e193-46de-b0d6-3911487cb1e2
author: OmniNode Team
created_at: 2025-05-27T05:49:06.733369
last_modified_at: 2025-05-27T17:26:51.817734
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 3a3e88adf198ee11ea062a53209ae91e9834259502cfa938ae30a127acf88958
entrypoint: python@execution_context.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.execution_context
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase ExecutionContext, Capability, and Security Protocols

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** ExecutionContext protocol and capability enforcement for secure node execution  
> **Related:** [Core Protocols](./reference-protocols-core.md) and [Security Overview](./reference-security-overview.md)

---

## Overview

The ExecutionContext provides the shared runtime environment for all tools, validators, and tests. It implements capability-based security, configuration access, and observability features to ensure secure and traceable execution of ONEX nodes.

---

## ExecutionContext Protocol

`ExecutionContext` provides the shared runtime environment for all tools, validators, and tests.

### Responsibilities

- Provide access to configuration
- Expose secrets or capabilities in a controlled way
- Log execution details
- Trace correlation ID for observability
- Enforce capability-based permissions

### Protocol Definition

See also: [Core Protocols](./reference-protocols-core.md) for canonical interface definitions.

```python
from typing import Protocol, Any, Optional, UUID
import logging

class ExecutionContext(Protocol):
    __protocol_version__ = "1.0.0"

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback"""
        ...

    def get_capability(self, name: str) -> bool:
        """Check if capability is granted"""
        ...

    def get_correlation_id(self) -> UUID:
        """Get unique correlation ID for this execution"""
        ...

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get logger instance for this execution context"""
        ...

    def get_secret(self, name: str) -> Optional[str]:
        """Get secret value if capability allows"""
        ...

    def check_capability(self, capability_type: str, resource: str) -> bool:
        """Check specific capability for resource"""
        ...
```

### Implementation Example

```python
from dataclasses import dataclass
from typing import Dict, Any, Set
import uuid
import logging

@dataclass
class DefaultExecutionContext:
    """Default implementation of ExecutionContext"""
    
    config: Dict[str, Any]
    capabilities: Set[str]
    secrets: Dict[str, str]
    correlation_id: UUID
    logger: logging.Logger
    
    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
    
    def get_capability(self, name: str) -> bool:
        return name in self.capabilities
    
    def get_correlation_id(self) -> UUID:
        return self.correlation_id
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        if name:
            return self.logger.getChild(name)
        return self.logger
    
    def get_secret(self, name: str) -> Optional[str]:
        if not self.check_capability("secret.access", name):
            raise CapabilityError(f"Access denied to secret: {name}")
        return self.secrets.get(name)
    
    def check_capability(self, capability_type: str, resource: str) -> bool:
        capability = f"{capability_type}:{resource}"
        return capability in self.capabilities
```

---

## Capabilities

Capabilities represent fine-grained, declarative permissions granted to components at runtime. They follow the principle of least privilege and are enforced at the ExecutionContext level.

### Capability Types

| Type             | Example Resource     | Description |
|------------------|----------------------|-------------|
| `file.read`      | `/etc/config.yaml`   | Read access to specific files |
| `file.write`     | `/tmp/output.json`   | Write access to specific files |
| `network.connect`| `api.service.local`  | Network connection to specific hosts |
| `registry.read`  | `tools/*`            | Read access to registry components |
| `registry.write` | `tools/my_tool`      | Write access to registry components |
| `artifact.read`  | `abc123`             | Read access to specific artifacts |
| `artifact.write` | `def456`             | Write access to specific artifacts |
| `secret.access`  | `GITHUB_TOKEN`       | Access to specific secrets |
| `process.execute`| `/usr/bin/git`       | Execute specific processes |

### Capability Patterns

Capabilities support wildcard and prefix patterns:

```yaml
capabilities:
  - type: "file.read"
    resource: "/etc/config/*"      # All files in /etc/config/
  - type: "registry.read"
    resource: "tools/*"            # All tools in registry
  - type: "network.connect"
    resource: "*.example.com"      # All subdomains of example.com
  - type: "secret.access"
    resource: "API_*"              # All secrets starting with API_
```

---

## Capability Enforcement

### Enforcement Pattern

Before performing any privileged action, components must check capabilities:

```python
def read_config_file(context: ExecutionContext, file_path: str) -> str:
    """Read configuration file with capability check"""
    if not context.check_capability("file.read", file_path):
        raise CapabilityError(f"Access denied to file: {file_path}")
    
    with open(file_path, 'r') as f:
        return f.read()

def connect_to_api(context: ExecutionContext, host: str, port: int) -> None:
    """Connect to API with capability check"""
    resource = f"{host}:{port}"
    if not context.check_capability("network.connect", resource):
        raise CapabilityError(f"Network access denied to: {resource}")
    
    # Proceed with connection
    pass
```

### Capability Registry Format

Capabilities are defined in YAML format:

```yaml
# Node capability manifest
capabilities:
  - type: "file.read"
    resource: "/etc/omnibase/config.yaml"
    description: "Read main configuration file"
  - type: "registry.read"
    resource: "validators/*"
    description: "Read validator registry entries"
  - type: "secret.access"
    resource: "OMNIBASE_API_KEY"
    description: "Access API key for external services"
  - type: "network.connect"
    resource: "api.example.com:443"
    description: "Connect to external API"
```

### Capability Validation

Capabilities are validated at runtime and during CI:

```python
from omnibase.security import CapabilityValidator

def validate_node_capabilities(node_manifest: Dict[str, Any]) -> bool:
    """Validate node capability requirements"""
    validator = CapabilityValidator()
    
    for capability in node_manifest.get("capabilities", []):
        if not validator.is_valid_capability(capability):
            raise ValidationError(f"Invalid capability: {capability}")
    
    return True
```

---

## CapabilityContext Utilities

The ExecutionContext provides helper methods for common capability checks:

```python
class ExecutionContext(Protocol):
    def check_file_read(self, path: str) -> bool:
        """Check file read capability"""
        return self.check_capability("file.read", path)
    
    def check_file_write(self, path: str) -> bool:
        """Check file write capability"""
        return self.check_capability("file.write", path)
    
    def check_network_connect(self, host: str, port: int = None) -> bool:
        """Check network connection capability"""
        resource = f"{host}:{port}" if port else host
        return self.check_capability("network.connect", resource)
    
    def check_registry_access(self, name: str, mode: str = "read") -> bool:
        """Check registry access capability"""
        return self.check_capability(f"registry.{mode}", name)
    
    def check_artifact_access(self, artifact_id: str, mode: str = "read") -> bool:
        """Check artifact access capability"""
        return self.check_capability(f"artifact.{mode}", artifact_id)
    
    def check_secret_access(self, secret_name: str) -> bool:
        """Check secret access capability"""
        return self.check_capability("secret.access", secret_name)
```

### Usage Examples

```python
def process_file(context: ExecutionContext, input_path: str, output_path: str):
    """Process file with capability checks"""
    # Check read capability
    if not context.check_file_read(input_path):
        raise CapabilityError(f"Cannot read file: {input_path}")
    
    # Check write capability
    if not context.check_file_write(output_path):
        raise CapabilityError(f"Cannot write file: {output_path}")
    
    # Proceed with file processing
    with open(input_path, 'r') as infile:
        content = infile.read()
    
    processed_content = process_content(content)
    
    with open(output_path, 'w') as outfile:
        outfile.write(processed_content)
```

---

## Secrets Handling

Secrets are managed through the ExecutionContext with capability-based access control.

### Secret Access Pattern

```python
def get_api_token(context: ExecutionContext) -> str:
    """Get API token with capability check"""
    token = context.get_secret("API_TOKEN")
    if token is None:
        raise SecretAccessError("API_TOKEN not available")
    return token

def authenticate_service(context: ExecutionContext, service_name: str):
    """Authenticate with external service"""
    secret_name = f"{service_name.upper()}_API_KEY"
    
    if not context.check_secret_access(secret_name):
        raise CapabilityError(f"Access denied to secret: {secret_name}")
    
    api_key = context.get_secret(secret_name)
    if not api_key:
        raise SecretAccessError(f"Secret not found: {secret_name}")
    
    # Use API key for authentication
    return authenticate_with_key(api_key)
```

### Secret Sources

Secrets can be injected from various sources:

- **Environment variables**: `OMNIBASE_SECRET_NAME`
- **File mounts**: `/run/secrets/secret_name`
- **Secret managers**: HashiCorp Vault, AWS Secrets Manager, etc.
- **Temporary files**: Secure temporary file mounts

### Secret Auditing

All secret accesses are automatically audited:

```python
def audit_secret_access(context: ExecutionContext, secret_name: str, success: bool):
    """Audit secret access attempt"""
    logger = context.get_logger("security.audit")
    correlation_id = context.get_correlation_id()
    
    logger.info(
        "Secret access attempt",
        extra={
            "correlation_id": str(correlation_id),
            "secret_name": secret_name,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## Error Types

```python
class CapabilityError(Exception):
    """Raised when capability check fails"""
    def __init__(self, message: str, capability: str = None, resource: str = None):
        super().__init__(message)
        self.capability = capability
        self.resource = resource

class SecretAccessError(Exception):
    """Raised when secret access fails"""
    def __init__(self, message: str, secret_name: str = None):
        super().__init__(message)
        self.secret_name = secret_name

class SandboxViolationError(Exception):
    """Raised when sandbox constraints are violated"""
    def __init__(self, message: str, violation_type: str = None):
        super().__init__(message)
        self.violation_type = violation_type
```

### Error Handling Examples

```python
def safe_file_operation(context: ExecutionContext, file_path: str):
    """Safely perform file operation with proper error handling"""
    try:
        if not context.check_file_read(file_path):
            raise CapabilityError(
                f"File read access denied: {file_path}",
                capability="file.read",
                resource=file_path
            )
        
        with open(file_path, 'r') as f:
            return f.read()
            
    except CapabilityError as e:
        logger = context.get_logger("security")
        logger.warning(f"Capability violation: {e}")
        raise
    
    except FileNotFoundError:
        raise SecretAccessError(f"File not found: {file_path}")
```

---

## Integration with ONEX CLI

### Capability Management

```bash
# Check node capabilities
onex node-info my_node --show-capabilities

# Validate capability manifest
onex validate capabilities my_node_capabilities.yaml

# Run node with specific capabilities
onex run my_node --capabilities file.read:/etc/config.yaml,network.connect:api.example.com

# Audit capability usage
onex audit capabilities --node my_node --since "2025-05-27"
```

### Security Validation

```bash
# Run security validation
onex run parity_validator_node --args='["--validation-types", "security_compliance"]'

# Check capability compliance
onex validate security --check-capabilities

# Generate security report
onex security report --format json > security_report.json
```

---

## Best Practices

### For Node Developers

1. **Principle of least privilege**: Request only necessary capabilities
2. **Explicit capability checks**: Always check capabilities before privileged operations
3. **Proper error handling**: Use structured error types for capability violations
4. **Audit logging**: Log security-relevant operations
5. **Secret hygiene**: Never log or expose secrets

### For System Administrators

1. **Capability review**: Regularly review and audit capability grants
2. **Secret rotation**: Implement regular secret rotation policies
3. **Access monitoring**: Monitor capability usage and violations
4. **Sandbox enforcement**: Use sandboxing for untrusted code execution
5. **Security scanning**: Regular security scans of node capabilities

### For Security

1. **Capability validation**: Validate all capability manifests
2. **Threat modeling**: Consider capability-based attack vectors
3. **Audit trails**: Maintain comprehensive audit logs
4. **Incident response**: Have procedures for capability violations
5. **Regular reviews**: Periodic security reviews of capability model

---

## Configuration Integration

### Capability Configuration

```yaml
# omnibase.yaml
security:
  capabilities:
    default_grants:
      - "file.read:/etc/omnibase/*"
      - "registry.read:*"
    
    restricted_capabilities:
      - "network.connect:*"
      - "process.execute:*"
      - "secret.access:*"
    
    audit:
      enabled: true
      log_level: "INFO"
      include_success: false  # Only log failures by default

  secrets:
    sources:
      - type: "environment"
        prefix: "OMNIBASE_SECRET_"
      - type: "file"
        path: "/run/secrets"
    
    audit:
      enabled: true
      redact_values: true
```

### Runtime Configuration

```python
from omnibase.config import get_config_manager
from omnibase.security import create_execution_context

def create_secure_context(node_name: str) -> ExecutionContext:
    """Create execution context with security configuration"""
    config = get_config_manager()
    
    # Load node-specific capabilities
    capabilities = config.get(f"nodes.{node_name}.capabilities", [])
    
    # Load secrets
    secrets = load_secrets_from_config(config)
    
    # Create context
    return create_execution_context(
        capabilities=capabilities,
        secrets=secrets,
        correlation_id=uuid.uuid4(),
        config=config
    )
```

---

> Permissions aren't toggles. They're contracts. Enforce them like you mean it.
