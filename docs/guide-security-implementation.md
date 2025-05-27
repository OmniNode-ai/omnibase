# ONEX Security Implementation Guide

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Practical implementation guide for authorization, secrets management, and secure node execution  
> **Audience:** Developers, DevOps engineers, security implementers  
> **Enforcement:** All ONEX components must implement these security patterns

---

## Overview

This guide provides practical implementation details for ONEX security features including authorization, secrets management, and secure node execution. For architecture overview and authentication, see the [Security Overview](reference-security-overview.md).

**See Also:**
- [Security Overview](reference-security-overview.md) - Architecture and authentication
- [Security Architecture Design](architecture-security-design.md) - Network security and monitoring

---

## Authorization

### Role-Based Access Control (RBAC)

#### Role Configuration
```yaml
# RBAC configuration
roles:
  admin:
    description: "Full system access"
    permissions:
      - "nodes:*"
      - "registry:*"
      - "config:*"
      - "users:*"
  
  developer:
    description: "Node development and testing"
    permissions:
      - "nodes:read"
      - "nodes:execute"
      - "nodes:create"
      - "registry:read"
      - "config:read"
  
  operator:
    description: "System operation and monitoring"
    permissions:
      - "nodes:read"
      - "nodes:execute"
      - "registry:read"
      - "monitoring:*"
      - "config:read"
  
  readonly:
    description: "Read-only access"
    permissions:
      - "nodes:read"
      - "registry:read"
      - "config:read"
```

#### Permission Implementation
```python
from enum import Enum
from typing import Set, List, Optional, Dict, Any
from dataclasses import dataclass

class Permission(Enum):
    """System permissions enumeration."""
    NODES_READ = "nodes:read"
    NODES_EXECUTE = "nodes:execute"
    NODES_CREATE = "nodes:create"
    NODES_DELETE = "nodes:delete"
    REGISTRY_READ = "registry:read"
    REGISTRY_WRITE = "registry:write"
    CONFIG_READ = "config:read"
    CONFIG_WRITE = "config:write"
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    MONITORING_READ = "monitoring:read"
    MONITORING_WRITE = "monitoring:write"

@dataclass
class User:
    """User with roles and permissions."""
    user_id: str
    roles: Set[str]
    permissions: Set[Permission]
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions
    
    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(perm in self.permissions for perm in permissions)

class AuthorizationService:
    """Authorization service for permission checking."""
    
    def __init__(self, rbac_config: Dict[str, Any]):
        self.roles = rbac_config.get("roles", {})
        self._build_permission_cache()
    
    def check_permission(
        self, 
        user: User, 
        permission: Permission,
        resource: Optional[str] = None
    ) -> bool:
        """Check if user has permission for resource."""
        if user.has_permission(permission):
            return True
        
        if resource and self._check_resource_permission(user, permission, resource):
            return True
        
        return False
    
    def require_permission(
        self, 
        user: User, 
        permission: Permission,
        resource: Optional[str] = None
    ) -> None:
        """Require user to have permission, raise exception if not."""
        if not self.check_permission(user, permission, resource):
            raise PermissionDeniedError(
                f"User {user.user_id} lacks permission {permission.value}"
            )
```

### Capability-Based Security

#### Execution Context Capabilities
```python
from typing import Protocol, Set
from dataclasses import dataclass

class Capability(Protocol):
    """Protocol for security capabilities."""
    
    def check_access(self, resource: str, operation: str) -> bool:
        """Check if capability allows access to resource."""
        ...

@dataclass
class FileCapability:
    """File system access capability."""
    allowed_paths: Set[str]
    operations: Set[str]  # read, write, execute
    
    def check_access(self, resource: str, operation: str) -> bool:
        """Check file access permission."""
        if operation not in self.operations:
            return False
        
        for allowed_path in self.allowed_paths:
            if resource.startswith(allowed_path):
                return True
        
        return False

@dataclass
class NetworkCapability:
    """Network access capability."""
    allowed_hosts: Set[str]
    allowed_ports: Set[int]
    protocols: Set[str]  # http, https, tcp, udp
    
    def check_access(self, resource: str, operation: str) -> bool:
        """Check network access permission."""
        # Implementation for network access validation
        pass

class SecureExecutionContext:
    """Execution context with capability-based security."""
    
    def __init__(self, capabilities: List[Capability]):
        self.capabilities = capabilities
    
    def check_file_access(self, path: str, operation: str) -> bool:
        """Check if file access is allowed."""
        for cap in self.capabilities:
            if isinstance(cap, FileCapability):
                if cap.check_access(path, operation):
                    return True
        return False
    
    def check_network_access(self, url: str, operation: str) -> bool:
        """Check if network access is allowed."""
        for cap in self.capabilities:
            if isinstance(cap, NetworkCapability):
                if cap.check_access(url, operation):
                    return True
        return False
```

---

## Secrets Management

### Secret Storage Configuration
```yaml
# Secrets management configuration
secrets:
  backend: "vault"  # vault, k8s, env, file
  vault:
    url: "https://vault.example.com"
    auth_method: "kubernetes"
    mount_path: "secret"
    namespace: "onex"
  
  encryption:
    algorithm: "AES-256-GCM"
    key_rotation_days: 90
  
  access_control:
    require_approval: true
    approval_threshold: 2
    audit_all_access: true
```

### Secret Management Implementation
```python
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import base64
from cryptography.fernet import Fernet

class SecretBackend(ABC):
    """Abstract base class for secret backends."""
    
    @abstractmethod
    def get_secret(self, path: str) -> Optional[str]:
        """Retrieve secret from backend."""
        pass
    
    @abstractmethod
    def set_secret(self, path: str, value: str) -> bool:
        """Store secret in backend."""
        pass
    
    @abstractmethod
    def delete_secret(self, path: str) -> bool:
        """Delete secret from backend."""
        pass

class VaultBackend(SecretBackend):
    """HashiCorp Vault backend implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = self._initialize_vault_client()
    
    def get_secret(self, path: str) -> Optional[str]:
        """Retrieve secret from Vault."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.config["mount_path"]
            )
            return response["data"]["data"].get("value")
        except Exception:
            return None
    
    def set_secret(self, path: str, value: str) -> bool:
        """Store secret in Vault."""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={"value": value},
                mount_point=self.config["mount_path"]
            )
            return True
        except Exception:
            return False

class SecretsManager:
    """Centralized secrets management service."""
    
    def __init__(self, backend: SecretBackend):
        self.backend = backend
        self.encryption_key = self._load_encryption_key()
    
    def get_secret(self, path: str, decrypt: bool = True) -> Optional[str]:
        """Retrieve and optionally decrypt secret."""
        secret = self.backend.get_secret(path)
        if secret and decrypt:
            return self._decrypt(secret)
        return secret
    
    def set_secret(self, path: str, value: str, encrypt: bool = True) -> bool:
        """Encrypt and store secret."""
        if encrypt:
            value = self._encrypt(value)
        return self.backend.set_secret(path, value)
    
    def _encrypt(self, value: str) -> str:
        """Encrypt secret value."""
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt secret value."""
        f = Fernet(self.encryption_key)
        encrypted_bytes = base64.b64decode(encrypted_value.encode())
        return f.decrypt(encrypted_bytes).decode()
```

---

## Secure Node Execution

### Sandboxing Configuration
```yaml
# Node execution security
execution:
  sandbox:
    enabled: true
    type: "container"  # container, chroot, vm
    resource_limits:
      memory: "512Mi"
      cpu: "500m"
      disk: "1Gi"
      network_bandwidth: "10Mbps"
  
  capabilities:
    file_system:
      read_only_paths: ["/usr", "/lib", "/bin"]
      writable_paths: ["/tmp", "/var/tmp"]
      forbidden_paths: ["/etc/passwd", "/etc/shadow"]
    
    network:
      allowed_domains: ["api.example.com"]
      blocked_domains: ["malicious.com"]
      allowed_ports: [80, 443, 8080]
```

### Secure Execution Implementation
```python
from typing import List, Dict, Any
import subprocess
import tempfile
import os

class NodeSandbox:
    """Secure sandbox for node execution."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.resource_limits = config.get("resource_limits", {})
        self.capabilities = config.get("capabilities", {})
    
    def execute_node(
        self, 
        node_path: str, 
        args: List[str],
        context: SecureExecutionContext
    ) -> Dict[str, Any]:
        """Execute node in secure sandbox."""
        
        # Create temporary execution environment
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up sandbox environment
            env = self._create_sandbox_environment(temp_dir)
            
            # Apply resource limits
            limits = self._create_resource_limits()
            
            # Execute with security constraints
            result = self._execute_with_constraints(
                node_path, args, env, limits, context
            )
            
            return result
    
    def _create_sandbox_environment(self, temp_dir: str) -> Dict[str, str]:
        """Create isolated environment for execution."""
        env = os.environ.copy()
        
        # Restrict environment variables
        sensitive_vars = ["AWS_SECRET_KEY", "DATABASE_PASSWORD"]
        for var in sensitive_vars:
            env.pop(var, None)
        
        # Set sandbox-specific variables
        env["SANDBOX_MODE"] = "true"
        env["TEMP_DIR"] = temp_dir
        
        return env
    
    def _create_resource_limits(self) -> Dict[str, Any]:
        """Create resource limit configuration."""
        return {
            "memory": self.resource_limits.get("memory", "512Mi"),
            "cpu": self.resource_limits.get("cpu", "500m"),
            "timeout": self.resource_limits.get("timeout", 300)
        }
    
    def _execute_with_constraints(
        self,
        node_path: str,
        args: List[str],
        env: Dict[str, str],
        limits: Dict[str, Any],
        context: SecureExecutionContext
    ) -> Dict[str, Any]:
        """Execute with security and resource constraints."""
        
        # Validate file access
        if not context.check_file_access(node_path, "execute"):
            raise SecurityError(f"Execution not allowed for {node_path}")
        
        try:
            # Execute with timeout and resource limits
            process = subprocess.run(
                [node_path] + args,
                env=env,
                timeout=limits["timeout"],
                capture_output=True,
                text=True
            )
            
            return {
                "exit_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "execution_time": limits["timeout"]
            }
            
        except subprocess.TimeoutExpired:
            raise SecurityError("Node execution timeout exceeded")
        except Exception as e:
            raise SecurityError(f"Node execution failed: {str(e)}")
```

---

## Security Best Practices

### Implementation Checklist
- [ ] Implement proper authentication for all endpoints
- [ ] Use RBAC for authorization with least privilege principle
- [ ] Store secrets securely using dedicated secret management
- [ ] Execute nodes in sandboxed environments with resource limits
- [ ] Validate all inputs and sanitize outputs
- [ ] Log all security-relevant events for audit
- [ ] Implement proper error handling without information leakage
- [ ] Use secure communication protocols (TLS/mTLS)
- [ ] Regular security testing and vulnerability assessments

### Common Security Patterns
1. **Input Validation**: Always validate and sanitize user inputs
2. **Output Encoding**: Properly encode outputs to prevent injection
3. **Error Handling**: Don't leak sensitive information in error messages
4. **Logging**: Log security events but not sensitive data
5. **Rate Limiting**: Implement rate limiting to prevent abuse

---

## See Also

- [Security Overview](reference-security-overview.md) - Architecture and authentication protocols
- [Security Architecture Design](architecture-security-design.md) - Network security and monitoring
- [Error Handling Guide](error_handling.md) - Secure error handling patterns
- [Node Development Guide](developer_guide.md) - Secure node development practices 