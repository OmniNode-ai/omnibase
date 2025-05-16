from pydantic import BaseModel, Field
from omnibase.model.model_enum_metadata import UriTypeEnum

class OnexUriModel(BaseModel):
    """
    Canonical Pydantic model for ONEX URIs.
    See docs/nodes/node_contracts.md and docs/nodes/structural_conventions.md for spec.
    """
    type: UriTypeEnum = Field(..., description="ONEX URI type (tool, validator, agent, model, plugin, schema, node)")
    namespace: str = Field(..., description="Namespace component of the URI")
    version_spec: str = Field(..., description="Version specifier (semver or constraint)")
    original: str = Field(..., description="Original URI string as provided") 