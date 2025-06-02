# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.068968'
# description: Stamped by PythonHandler
# entrypoint: python://model_schema
# hash: 21464ac854e592e214a074cb4c66afb52d6f573e9be594aa2cb038d362589ea3
# last_modified_at: '2025-05-29T14:13:58.933955+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_schema.py
# namespace: python://omnibase.model.model_schema
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: bfe429b0-f04f-48dc-9001-655fb19f442f
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, RootModel


class SchemaPropertiesModel(RootModel[Dict[str, "SchemaPropertyModel"]]):
    """
    Strongly typed model for the properties field in a JSON schema.
    Wraps a dict of property names to SchemaPropertyModel.
    """

    pass


class RequiredFieldsModel(RootModel[List[str]]):
    """
    Strongly typed model for the required fields in a JSON schema.
    Wraps a list of required property names.
    """

    pass


class SchemaPropertyModel(BaseModel):
    """
    Strongly typed model for a single property in a JSON schema.
    Includes common JSON Schema fields and is extensible for M1+.
    """

    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Union[str, int, float, bool, list, dict]] = None
    enum: Optional[List[Union[str, int, float, bool]]] = None
    format: Optional[str] = None
    items: Optional["SchemaPropertyModel"] = None  # For array types
    properties: Optional[SchemaPropertiesModel] = None  # For object types
    required: Optional[RequiredFieldsModel] = None
    # Add more fields as needed for ONEX/M1+

    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}


class SchemaModel(BaseModel):
    """
    Strongly typed Pydantic model for ONEX JSON schema files.
    Includes canonical fields and is extensible for M1+.
    """

    schema_uri: Optional[str] = Field(None)
    title: Optional[str] = None
    type: Optional[str] = None
    properties: Optional[SchemaPropertiesModel] = None
    required: Optional[RequiredFieldsModel] = None
    # TODO: Add more fields and validation logic in M1+


SchemaPropertyModel.model_rebuild()
SchemaPropertiesModel.model_rebuild()
RequiredFieldsModel.model_rebuild()
