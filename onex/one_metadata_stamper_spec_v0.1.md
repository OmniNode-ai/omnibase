---

version: v0.1
status: Active
last\_updated: 2025-05-14
-------------------------

# OmniNode Metadata Stamper Specification — v0.1

This document defines the minimum viable metadata standard for OmniNode-compatible nodes, tools, agents, and transformers. It enables registry registration, trust enforcement, platform targeting, and lifecycle governance.

## 📦 Purpose

The metadata header supports:

* Static analysis and trust classification
* Registry-based discovery and validation
* Signature and provenance tracking
* Runtime policy enforcement
* Compatibility with distributed platforms and CI

## 🧱 Structure

The metadata block must be placed at the top of the file, inside language-specific comment delimiters. For Python:

```python
# === OmniNode:Tool_Metadata ===
...
# === /OmniNode:Tool_Metadata ===
```

All metadata values must be YAML-compatible and statically parseable.

## ✅ Minimal Required Keys

```yaml
metadata_version: 0.1
name: github_sniper_agent
namespace: omninode.agents.discovery
version: 0.1.2
entrypoint: main.py
protocols_supported:
  - O.N.E. v0.1
```

## 🔐 Trust & Signatures

```yaml
signature_alg: ed25519
signature_format: hex
signed_by: omninode:jonah
encryption:
  encrypted_fields: []
  encryption_alg: none
```

## 🎯 Platform & Runtime

```yaml
platform_matrix:
  - os: linux
    arch: amd64
    python: "3.11"
  - os: macos
    arch: arm64
    python: "3.12"
runtime_constraints:
  sandboxed: true
  privileged: false
  requires_network: true
  requires_gpu: false
```

## 🛡️ Policy Enforcement

```yaml
policy:
  network_access: true
  allowed_endpoints:
    - github.com
    - pypi.org
  resource_limits:
    memory: "512mb"
    threads: 2
  compliance_requirements:
    - gdpr
    - iso27001
```

## 🧪 CI & Test Metadata

```yaml
test_suite: true
test_status: passing
coverage: 91.2
ci_url: https://ci.omninode.dev/github-sniper/status
```

## 📦 Registry Support

```yaml
registry_url: https://registry.omninode.dev/github-sniper-agent
dynamic_fields:
  - trust_score
  - last_registry_sync
  - registry_classification
```

## 🌐 Comment Delimiters by Language

| Language | Start Delimiter                     | End Delimiter                        |
| -------- | ----------------------------------- | ------------------------------------ |
| Python   | `# === OmniNode:Tool_Metadata ===`  | `# === /OmniNode:Tool_Metadata ===`  |
| JS/TS    | `/* === OmniNode:Tool_Metadata ===` | `=== /OmniNode:Tool_Metadata === */` |
| Rust     | `// === OmniNode:Tool_Metadata ===` | `// === /OmniNode:Tool_Metadata ===` |
| Go       | `// === OmniNode:Tool_Metadata ===` | `// === /OmniNode:Tool_Metadata ===` |

## 🛠 Tooling (Planned)

* CLI Validator: `omninode-meta-lint`
* Pre-commit hook for metadata compliance
* CI Integration for metadata schema conformance

## 🔄 Future Enhancements

* Manifest signing and federation sync
* Metadata inheritance (`extends:`)
* Public trust graph linkages
* Auto-generation from runtime environment

---

This is the active v0.1 baseline for OmniNode Metadata Stamper support. All metadata blocks stamped in tools or agents must conform to this schema unless explicitly versioned otherwise.
