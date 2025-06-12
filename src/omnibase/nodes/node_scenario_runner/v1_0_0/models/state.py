# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# contract_hash: 14f3a7a9fc4fa34c0e58fabaeaac667f6a83da8a23fe64ed134eb9772c92b9e9
# To regenerate: poetry run onex run schema_generator_node --args='["src/omnibase/nodes/node_scenario_runner/v1_0_0/contract.yaml", "src/omnibase/nodes/node_scenario_runner/v1_0_0/models/state.py"]'
from typing import Optional
from pydantic import BaseModel, field_validator
from enum import Enum
class StatusEnum(str, Enum):
    success = "success"
    failure = "failure"
    warning = "warning"


class ScenarioRunnerInputState(BaseModel):
    version: str  # Schema version for input state
    NODE_SCENARIO_RUNNER_REQUIRED_FIELD: str  # NODE_SCENARIO_RUNNER: Replace with your required input field
    NODE_SCENARIO_RUNNER_OPTIONAL_FIELD: Optional[str] = "NODE_SCENARIO_RUNNER_DEFAULT_VALUE"  # NODE_SCENARIO_RUNNER: Replace with your optional input field

    @field_validator("version", mode="before")
    @classmethod
    def parse_version(cls, v):
        from omnibase.model.model_semver import SemVerModel
        if isinstance(v, SemVerModel):
            return v
        if isinstance(v, str):
            return SemVerModel.parse(v)
        if isinstance(v, dict):
            return SemVerModel(**v)
        raise ValueError("version must be a string, dict, or SemVerModel")

class ScenarioRunnerOutputState(BaseModel):
    version: str  # Schema version for output state (matches input)
    status: StatusEnum  # Execution status  # Allowed: ['success', 'failure', 'warning']
    message: str  # Human-readable result message
    NODE_SCENARIO_RUNNER_OUTPUT_FIELD: Optional[str] = None  # NODE_SCENARIO_RUNNER: Replace with your output field

    @field_validator("version", mode="before")
    @classmethod
    def parse_version(cls, v):
        from omnibase.model.model_semver import SemVerModel
        if isinstance(v, SemVerModel):
            return v
        if isinstance(v, str):
            return SemVerModel.parse(v)
        if isinstance(v, dict):
            return SemVerModel(**v)
        raise ValueError("version must be a string, dict, or SemVerModel")
