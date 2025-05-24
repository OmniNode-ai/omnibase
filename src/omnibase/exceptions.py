# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: exceptions.py
# version: 1.0.0
# uuid: 49d462c4-feda-4cfb-9677-f3a86c309dc1
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163633
# last_modified_at: 2025-05-24T21:33:27.850298
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f89e49aafe14e2b1070a814594e68a3ab07382560c0e640552314bfec6b76868
# entrypoint: python@exceptions.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.exceptions
# meta_type: tool
# === /OmniNode:Metadata ===


class OmniBaseError(Exception):
    """
    Canonical base error for all ONEX/OmniBase exceptions.
    Extend for specific error types in core, tools, and schema modules.
    See docs/nodes/error_taxonomy.md for error taxonomy and codes.
    """

    pass
