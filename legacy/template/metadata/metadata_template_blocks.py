# === OmniNode:Metadata ===
# metadata_version: "0.1"
# name: "metadata_template_blocks"
# namespace: "foundation.template.metadata"
# meta_type: "resource"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-12T00:00:00+00:00"
# last_modified_at: "2025-05-12T00:00:00+00:00"
# entrypoint: "metadata_template_blocks.py"
# protocols_supported: []
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Provides canonical metadata block string templates for use in stamping, registry, and code generation.
This file is a pure resource module and does not define any classes or logic.
"""

from typing import Final

#: Minimal metadata block template for Python/YAML/Markdown files.
MINIMAL_METADATA: Final[str] = """\
# === OmniNode:Metadata ===
metadata_version: "{metadata_version}"
schema_version: "{schema_version}"
name: "{name}"
namespace: "omninode.tools.{name}"
meta_type: "{meta_type}"
version: "{version}"
author: "{author}"
owner: "{owner}"
copyright: "{copyright}"
created_at: "{created_at}"
last_modified_at: "{last_modified_at}"
entrypoint: "{entrypoint}"
protocols_supported:
  - "{protocols_supported}"
protocol_class:
  - '{protocol_class}'
base_class:
  - '{base_class}'
mock_safe: {mock_safe}
# === /OmniNode:Metadata ===
"""

#: Extended metadata block template for advanced use cases.
EXTENDED_METADATA: Final[str] = """\
# === OmniNode:Metadata ===
metadata_version: "{metadata_version}"
schema_version: "{schema_version}"
name: "{name}"
title: "{title}"
uuid: "{uuid}"
version: "{version}"
status: "beta"
autoupdate: true
protocols_supported:
  - "{protocols_supported}"
protocol_class:
  - '{protocol_class}'
base_class:
  - '{base_class}'
mock_safe: {mock_safe}
namespace: "omninode.tools.{name}"
meta_type: "{meta_type}"
type: "{type}"
category: "tool.utility"
role: "unspecified"
description: |
  {description}
tags: ["{name}"]
author: "{author}"
owner: "{owner}"
authors: ["{author}"]
contact: "{contact}"
copyright: "{copyright}"
created_at: "{created_at}"
last_modified_at: "{last_modified_at}"
license: "MIT"
entrypoint: "{entrypoint}"
message_bus: "redis_streams"
dependencies: []
environment: ["python>=3.11"]
runtime_constraints: {{"sandboxed": true}}
test_suite: false
test_status: "unknown"
telemetry: {{"logging": true, "metrics": true}}
signature: ...
signature_alg: "ed25519"
signature_format: "hex"
signed_by: "{signed_by}"
last_updated: "{last_updated}"
# === /OmniNode:Metadata ===
"""
