<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: guide-security-monitoring.md
version: 1.0.0
uuid: 9b0b44f1-1019-450e-99b9-6d8295303770
author: OmniNode Team
created_at: 2025-05-27T09:05:28.791614
last_modified_at: 2025-05-27T17:26:52.043298
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: c463323a2cd2d19635d55a9e3acfa635e8c348f3ccc989b60c9c9915f0da5878
entrypoint: python@guide-security-monitoring.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.guide_security_monitoring
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Security Monitoring and Compliance

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Security monitoring, incident response, and compliance for the ONEX platform  
> **Audience:** Security engineers, compliance teams, incident responders  
> **Enforcement:** All ONEX deployments must implement these monitoring and compliance patterns

---

## Overview

This document defines security monitoring, incident response, and compliance frameworks for the ONEX platform. For network security architecture, see the [Security Architecture Design](architecture-security-design.md).

**See Also:**
- [Security Overview](reference-security-overview.md) - Architecture and authentication
- [Security Implementation Guide](guide-security-implementation.md) - Practical implementation details
- [Security Architecture Design](architecture-security-design.md) - Network security architecture

---

## Security Monitoring

### Security Event Logging

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

class SecurityAuditLogger:
    """Logger for security events and audit trails."""
    
    def __init__(self, logger_name: str = "onex.security"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        # Configure structured logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_authentication_event(
        self,
        user_id: str,
        event_type: str,  # login, logout, failed_login
        source_ip: str,
        user_agent: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log authentication event."""
        
        event_data = {
            "event_category": "authentication",
            "event_type": event_type,
            "user_id": user_id,
            "source_ip": source_ip,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "additional_data": additional_data or {}
        }
        
        self.logger.info(
            f"Authentication event: {event_type}",
            extra={"security_event": json.dumps(event_data)}
        )
    
    def log_authorization_event(
        self,
        user_id: str,
        resource: str,
        action: str,
        result: str,  # allowed, denied
        reason: Optional[str] = None
    ) -> None:
        """Log authorization event."""
        
        event_data = {
            "event_category": "authorization",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "result": result,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(
            f"Authorization {result}: {action} on {resource}",
            extra={"security_event": json.dumps(event_data)}
        )
    
    def log_node_execution_event(
        self,
        user_id: str,
        node_name: str,
        node_version: str,
        execution_id: str,
        result: str,  # success, failure, timeout
        duration_ms: int
    ) -> None:
        """Log node execution event."""
        
        event_data = {
            "event_category": "node_execution",
            "user_id": user_id,
            "node_name": node_name,
            "node_version": node_version,
            "execution_id": execution_id,
            "result": result,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(
            f"Node execution {result}: {node_name}@{node_version}",
            extra={"security_event": json.dumps(event_data)}
        )
```

### Security Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Security metrics
authentication_attempts = Counter(
    'onex_authentication_attempts_total',
    'Total authentication attempts',
    ['method', 'result']
)

authorization_checks = Counter(
    'onex_authorization_checks_total',
    'Total authorization checks',
    ['resource_type', 'action', 'result']
)

node_execution_security = Counter(
    'onex_node_execution_security_events_total',
    'Security events during node execution',
    ['event_type', 'severity']
)

active_sessions = Gauge(
    'onex_active_sessions',
    'Number of active user sessions'
)

security_scan_duration = Histogram(
    'onex_security_scan_duration_seconds',
    'Time spent on security scans',
    ['scan_type']
)
```

### Monitoring Configuration

```yaml
# Security monitoring configuration
monitoring:
  security_events:
    enabled: true
    retention_days: 90
    
    alerts:
      failed_authentication:
        threshold: 5
        window: "5m"
        severity: "warning"
      
      privilege_escalation:
        threshold: 1
        window: "1m"
        severity: "critical"
      
      suspicious_node_execution:
        threshold: 10
        window: "10m"
        severity: "warning"
  
  compliance:
    audit_log_retention: 365  # days
    encryption_at_rest: true
    encryption_in_transit: true
    access_log_all_requests: true
```

---

## Vulnerability Management

### Security Scanning

```python
import subprocess
import json
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Vulnerability:
    """Vulnerability information."""
    id: str
    severity: str
    description: str
    affected_component: str
    fix_available: bool
    cvss_score: float

class VulnerabilityScanner:
    """Security vulnerability scanner."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scan_tools = config.get("scan_tools", ["trivy", "safety"])
    
    def scan_dependencies(self, project_path: str) -> List[Vulnerability]:
        """Scan project dependencies for vulnerabilities."""
        vulnerabilities = []
        
        for tool in self.scan_tools:
            if tool == "safety":
                vulnerabilities.extend(self._scan_with_safety(project_path))
            elif tool == "trivy":
                vulnerabilities.extend(self._scan_with_trivy(project_path))
        
        return vulnerabilities
    
    def _scan_with_safety(self, project_path: str) -> List[Vulnerability]:
        """Scan with Safety tool."""
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return []  # No vulnerabilities found
            
            # Parse safety output
            vulnerabilities = []
            for vuln_data in json.loads(result.stdout):
                vulnerabilities.append(Vulnerability(
                    id=vuln_data.get("id", ""),
                    severity=self._map_safety_severity(vuln_data.get("severity")),
                    description=vuln_data.get("advisory", ""),
                    affected_component=vuln_data.get("package_name", ""),
                    fix_available=bool(vuln_data.get("fixed_in")),
                    cvss_score=float(vuln_data.get("cvss", 0.0))
                ))
            
            return vulnerabilities
            
        except Exception as e:
            print(f"Safety scan failed: {e}")
            return []
    
    def _scan_with_trivy(self, project_path: str) -> List[Vulnerability]:
        """Scan with Trivy tool."""
        # Implementation for Trivy scanning
        pass
    
    def _map_safety_severity(self, severity: str) -> str:
        """Map Safety severity to standard levels."""
        mapping = {
            "high": "HIGH",
            "medium": "MEDIUM", 
            "low": "LOW"
        }
        return mapping.get(severity.lower(), "UNKNOWN")
```

---

## Monitoring Best Practices

### Implementation Guidelines

1. **Event Collection**
   - Collect security events from all system components
   - Use structured logging formats (JSON) for better parsing
   - Implement real-time event streaming for critical events
   - Ensure log integrity and tamper protection

2. **Alerting Strategy**
   - Define clear alert thresholds based on risk assessment
   - Implement alert escalation procedures
   - Use multiple notification channels for redundancy
   - Regular review and tuning of alert rules

3. **Metrics and Dashboards**
   - Create role-specific security dashboards
   - Track key security performance indicators (KPIs)
   - Implement trend analysis for proactive threat detection
   - Regular dashboard reviews and updates

### Integration with Incident Response

For comprehensive incident response procedures and compliance frameworks, see the [Incident Response and Compliance Guide](guide-incident-response.md).

### Monitoring Checklist

- [ ] Security event logging enabled for all components
- [ ] Real-time alerting configured for critical events
- [ ] Security metrics collection and visualization
- [ ] Log retention policies implemented
- [ ] Alert escalation procedures defined
- [ ] Regular monitoring system health checks
- [ ] Security dashboard access controls configured
- [ ] Monitoring system backup and recovery procedures

---

## See Also

- [Security Overview](reference-security-overview.md) - Architecture overview and authentication protocols
- [Security Implementation Guide](guide-security-implementation.md) - Practical implementation details
- [Security Architecture Design](architecture-security-design.md) - Network security architecture
- [Monitoring Guide](monitoring.md) - General monitoring and alerting
