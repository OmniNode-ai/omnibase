# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "template_routes"
# namespace: "omninode.tools.template_routes"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:30+00:00"
# last_modified_at: "2025-05-05T13:00:30+00:00"
# entrypoint: "template_routes.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
API routes for {{container_name}}.

This module contains the API routes for the {{container_name}} service.
"""

from fastapi import APIRouter
from foundation.api.utils import standardized_response

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint."""
    return standardized_response(data={"message": "Welcome to {{container_name}} API"})


@router.get("/status")
async def status():
    """Service status endpoint."""
    return standardized_response(data={"status": "operational"})