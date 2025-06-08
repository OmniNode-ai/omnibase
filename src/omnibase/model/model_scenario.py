from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator, field_validator
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.model.model_tool_collection import ToolCollection


class ArtifactTypeConfigModel(BaseModel):
    name: str = Field(
        ..., description="Artifact type name (e.g., nodes, cli_tools, modules)"
    )
    metadata_file: str = Field(
        ..., description="Canonical metadata filename for this artifact type"
    )
    version_pattern: Optional[str] = Field(
        None, description="Glob or pattern for version directories (e.g., v*)"
    )


class ScenarioConfigModel(BaseModel):
    scenario_name: str = Field(..., description="Human-readable scenario name")
    scenario_config_version: Optional[str] = Field(
        None, description="Canonical version for scenario config schema enforcement. Must match the expected version in the test harness or node."
    )
    description: Optional[str] = Field(None, description="Scenario description")
    scenario_type: Optional[str] = Field(
        None, description="Type of scenario (regression, chain, etc.)"
    )
    tags: Optional[List[str]] = Field(default_factory=list, description="Scenario tags")
    version: Optional[str] = Field(None, description="Scenario config version")
    created_by: Optional[str] = Field(None, description="Author or creator")
    node_versions: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Node version pins (name: version spec)"
    )
    artifact_types: Optional[List[ArtifactTypeConfigModel]] = Field(
        default_factory=list, description="Artifact type configs"
    )
    ignore_patterns: Optional[List[str]] = Field(
        default_factory=list, description="Glob patterns to ignore"
    )
    output_format: Optional[str] = Field(
        "yaml", description="Output format (yaml or json)"
    )
    include_metadata: Optional[bool] = Field(
        True, description="Whether to include/validate metadata"
    )
    output_path: Optional[str] = Field(
        ".onextree", description="Output path for manifest"
    )
    registry_tools: Optional[ToolCollection] = Field(
        default=None,
        description="Declarative mapping of tool names to tool implementations (ToolCollection) for scenario-driven registry injection. This is the canonical, type-safe way to specify tool wiring for each scenario."
    )
    trace_logging: Optional[bool] = Field(
        None, description="Enable trace logging for registry and scenario diagnostics"
    )

    @classmethod
    def introspect(cls):
        """
        Return the canonical Pydantic schema for this scenario config model.
        """
        return cls.schema()


class ScenarioChainStepModel(BaseModel):
    node: str = Field(..., description="Node name to execute")
    version: Optional[str] = Field(None, description="Node version spec")
    input: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Input arguments for the node"
    )
    expect: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Expected outputs/results"
    )


class ScenarioChainModel(BaseModel):
    scenario_name: str = Field(..., description="Human-readable scenario name")
    description: Optional[str] = Field(None, description="Scenario description")
    scenario_type: Optional[str] = Field(
        None, description="Type of scenario (chain, regression, etc.)"
    )
    tags: Optional[List[str]] = Field(default_factory=list, description="Scenario tags")
    version: Optional[str] = Field(None, description="Scenario chain version")
    created_by: Optional[str] = Field(None, description="Author or creator")
    config: Optional[str] = Field(
        None, description="Relative path to scenario config YAML"
    )
    chain: List[ScenarioChainStepModel] = Field(
        ..., description="Ordered list of scenario steps"
    )

    @field_validator("chain", mode="after")
    def chain_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Scenario chain must have at least one step")
        return v

    @classmethod
    def introspect(cls):
        """
        Return the canonical Pydantic schema for this scenario model.
        """
        return cls.schema()
