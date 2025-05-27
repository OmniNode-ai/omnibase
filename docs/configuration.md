<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: configuration.md
version: 1.0.0
uuid: c16d0ed5-32dc-4f4d-ab7c-48d10928d6a3
author: OmniNode Team
created_at: 2025-05-27T05:45:49.344119
last_modified_at: 2025-05-27T17:26:51.795655
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b6bea5821c2ae391d004862c6ea6f56298482f6e83efc880a0476b224540b9fb
entrypoint: python@configuration.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.configuration
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase Configuration System Specification

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Canonical, protocol-aligned configuration system for the OmniBase/ONEX platform

---

## Overview

This document defines the canonical configuration system for the OmniBase/ONEX platform. All agent, validator, tool, model, node, and environment configuration requirements, APIs, and best practices are specified here.

The `FoundationConfigManager` provides centralized, protocol-compliant configuration management across all OmniNode subsystems—including agents, tools, validators, models, nodes, security policies, and execution environments.

---

## Core Concepts

### 1. Protocol-Aware Namespacing

All configuration keys follow the O.N.E. Protocol hierarchy:

```text
validator.foundation.lint.strict_mode
agent.product.RESEARCH.max_depth
tool.deepseek_coder.context_limit
model.mixtral8x22b.quantization
node.security.firewall.enabled
env.dev.messagebus.retry_policy
```

Supports deep nesting and structured resolution:

```text
validator.<container>.<validator_name>.<setting>
agent.<role>.<mode>.<setting>
tool.<name>.<setting>
model.<name>.<setting>
node.<type>.<name>.<setting>
env.<env_name>.<subsystem>.<setting>
```

### 2. Layered Configuration Resolution

Configuration is resolved using four prioritized layers:

1. `defaults/` — static default values
2. `config/` — environment YAML/JSON files
3. `ENV` — environment variables
4. `runtime` — programmatic/CLI overrides

Supports fallback and inheritance by context:

```text
container.foundation EXECUTE mode:
  > env.dev.container.foundation
  > env.dev.default
  > container.foundation.default
  > global.default
```

### 3. Schema Enforcement per Namespace

Each configuration namespace must register a schema:

```python
FoundationConfigManager.register_schema("validator.lint", LintValidatorSchema)
```

Schemas (Pydantic-based) enforce:

* Type safety
* Required fields
* Defaults
* Validation logic

### 4. Override Tracking & Auditing

Tracks config source, layer, and change history:

```python
config.get("validator.foundation.lint.strict_mode")
# Value: False
# Source: ENV (VALIDATOR_LINT_STRICT_MODE=false)
# Layer: env.dev.container.foundation
```

Built-in audit tools:

* `config.audit_changes()`
* `config.view_resolution_path(key)`
* `config.list_overrides()`

### 5. Injection & CLI Integration

* DI injection for services and tools
* CLI overrides via `--set key=value`
* Execution profiles: `--profile ci`, `--profile safe_mode`

---

## Implementation

### FoundationConfigManager APIs

```python
class FoundationConfigManager:
    def get(self, key: str, context: Optional[Context] = None) -> Any:
        """Get configuration value with context-aware resolution"""
        
    def set(self, key: str, value: Any, source: str) -> None:
        """Set configuration value with source tracking"""
        
    def register_schema(self, namespace: str, schema: BaseModel) -> None:
        """Register Pydantic schema for namespace validation"""
        
    def load_profile(self, name: str) -> None:
        """Load predefined configuration profile"""
        
    def list_overrides(self) -> Dict[str, Any]:
        """List all configuration overrides and their sources"""
        
    def audit_changes(self) -> List[ConfigChange]:
        """Get audit trail of configuration changes"""
        
    def view_resolution_path(self, key: str) -> List[str]:
        """Show resolution path for configuration key"""
        
    def enable_watch_mode(self) -> None:
        """Enable live configuration reloading"""
```

### Configuration Loaders

All loaders implement the `BaseConfigLoader` interface:

```python
class BaseConfigLoader(ABC):
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load configuration from source"""
        
    @abstractmethod
    def watch(self, callback: Callable) -> None:
        """Watch for configuration changes"""
```

#### Available Loaders

* **`FileLoader`**: YAML/JSON configuration files
* **`EnvLoader`**: Environment variables (e.g., `VALIDATOR_LINT_STRICT_MODE`)
* **`InMemoryLoader`**: Runtime and CLI overrides
* **`RemoteLoader`**: External configuration sources (Consul, etcd, Redis)

### Configuration Schema Example

```python
from pydantic import BaseModel, Field
from typing import Optional

class LintValidatorSchema(BaseModel):
    strict_mode: bool = Field(default=False, description="Enable strict validation")
    max_line_length: int = Field(default=88, ge=1, le=200)
    ignore_patterns: List[str] = Field(default_factory=list)
    custom_rules: Optional[Dict[str, Any]] = None

# Register schema
config_manager.register_schema("validator.lint", LintValidatorSchema)
```

### CLI Integration

```bash
# Get configuration value
onex config get validator.foundation.lint.strict_mode

# Set configuration value
onex config set validator.foundation.lint.strict_mode true

# List all configuration
onex config list

# Validate configuration against schemas
onex config validate

# Export configuration
onex config export --format yaml

# View audit trail
onex config audit

# Load configuration profile
onex config profile ci
```

### Profile-Based Configuration

Profiles allow switching between predefined configuration sets:

```yaml
# profiles/ci.yaml
validator:
  foundation:
    lint:
      strict_mode: true
      max_line_length: 88
agent:
  timeout: 300
  retry_attempts: 3

# profiles/development.yaml
validator:
  foundation:
    lint:
      strict_mode: false
      max_line_length: 120
agent:
  timeout: 60
  retry_attempts: 1
```

Load profiles via CLI or programmatically:

```bash
onex config profile ci
```

```python
config_manager.load_profile("ci")
```

---

## Security & Compliance

### Secure Configuration Handling

* **`EncryptedStr`**: Special type for sensitive values
* **Log redaction**: Automatic masking of sensitive configuration in logs
* **Access control**: RBAC for configuration editing (when available)
* **Validation**: CI checks via `validate_configs.py`
* **Disaster recovery**: Profile fallback mechanisms

### Example Secure Configuration

```python
from omnibase.config import EncryptedStr

class DatabaseSchema(BaseModel):
    host: str
    port: int = 5432
    username: str
    password: EncryptedStr  # Automatically encrypted/decrypted
    ssl_cert_path: Optional[str] = None
```

### Environment Variable Mapping

Environment variables are automatically mapped to configuration keys:

```bash
# Environment variable
export VALIDATOR_LINT_STRICT_MODE=true

# Maps to configuration key
validator.lint.strict_mode
```

Mapping rules:
- Convert to lowercase
- Replace `_` with `.`
- Remove common prefixes (`OMNIBASE_`, `ONEX_`)

---

## Configuration Examples

### Basic Usage

```python
from omnibase.config import get_config_manager

config = get_config_manager()

# Get configuration with fallback
strict_mode = config.get("validator.lint.strict_mode", default=False)

# Get with context
timeout = config.get("agent.timeout", context={"env": "production"})

# Set runtime override
config.set("tool.max_retries", 5, source="cli")
```

### Schema Validation

```python
# Define schema
class AgentSchema(BaseModel):
    timeout: int = Field(ge=1, le=3600)
    max_retries: int = Field(ge=0, le=10)
    debug_mode: bool = False

# Register and validate
config.register_schema("agent", AgentSchema)

# This will raise ValidationError if invalid
config.set("agent.timeout", -1, source="test")  # Invalid: timeout must be >= 1
```

### Profile Management

```python
# Load CI profile
config.load_profile("ci")

# Check current overrides
overrides = config.list_overrides()
print(f"Active overrides: {overrides}")

# View resolution path
path = config.view_resolution_path("validator.lint.strict_mode")
print(f"Resolution path: {path}")
```

---

## Integration with ONEX CLI

### Configuration Commands

```bash
# View current configuration
onex config get validator.lint.strict_mode

# Set configuration with validation
onex config set validator.lint.max_line_length 100

# Load and validate entire configuration
onex config validate

# Export configuration for backup
onex config export --format yaml > backup.yaml

# Import configuration
onex config import backup.yaml

# Switch to CI profile
onex config profile ci

# View configuration audit trail
onex config audit --since "2025-01-01"
```

### Runtime Configuration Override

```bash
# Override configuration for single command
onex run my_node --set validator.lint.strict_mode=true

# Multiple overrides
onex run my_node \
  --set validator.lint.strict_mode=true \
  --set agent.timeout=300
```

---

## Best Practices

### For Node Developers

1. **Register schemas**: Always define and register Pydantic schemas for your configuration namespaces
2. **Use defaults**: Provide sensible defaults in your schemas
3. **Document configuration**: Include descriptions in schema fields
4. **Validate early**: Check configuration at startup, not during execution
5. **Use context**: Leverage context-aware resolution for environment-specific settings

### For System Administrators

1. **Use profiles**: Define profiles for different environments (dev, staging, prod)
2. **Audit regularly**: Review configuration changes and their sources
3. **Secure secrets**: Use `EncryptedStr` for sensitive configuration values
4. **Validate configuration**: Run `onex config validate` in CI/CD pipelines
5. **Monitor changes**: Set up alerts for unexpected configuration changes

### For CI/CD Integration

1. **Profile-based deployment**: Use different profiles for different environments
2. **Configuration validation**: Include `onex config validate` in CI checks
3. **Environment-specific overrides**: Use environment variables for deployment-specific settings
4. **Configuration drift detection**: Compare deployed configuration with expected profiles

---

## Error Handling

### Configuration Errors

```python
from omnibase.config.errors import (
    ConfigurationError,
    SchemaValidationError,
    ConfigurationNotFoundError
)

try:
    value = config.get("nonexistent.key")
except ConfigurationNotFoundError:
    # Handle missing configuration
    pass

try:
    config.set("validator.lint.timeout", "invalid", source="test")
except SchemaValidationError as e:
    # Handle validation error
    print(f"Validation failed: {e}")
```

### Common Error Scenarios

| Error | Cause | Resolution |
|-------|-------|------------|
| `SchemaValidationError` | Invalid value type or constraint | Check schema requirements |
| `ConfigurationNotFoundError` | Missing required configuration | Provide default or set value |
| `ProfileNotFoundError` | Unknown profile name | Check available profiles |
| `CircularReferenceError` | Configuration inheritance loop | Review configuration hierarchy |

---

> Configuration is the foundation of reliable systems. Make it explicit, validated, and auditable.
