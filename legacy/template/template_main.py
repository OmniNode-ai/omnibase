# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "template_main"
# namespace: "omninode.tools.template_main"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:31+00:00"
# last_modified_at: "2025-05-05T13:00:31+00:00"
# entrypoint: "template_main.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Main application module for {{container_name}}.

This module contains the main FastAPI application instance.
"""

import uvicorn
from api.routes import router as api_router
from config.settings import settings
from fastapi import FastAPI
from foundation import Foundation

# Initialize foundation instance
foundation = Foundation(service_name="{{container_name}}")

# Create FastAPI application
app = FastAPI(
    title="{{container_name}} API",
    description="{{description}}",
    version="0.1.0",
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Application events
@app.on_event("startup")
async def startup_event():
    """Execute startup tasks."""
    await foundation.initialize()
    await foundation.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Execute shutdown tasks."""
    await foundation.stop()


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=settings.debug,
    )