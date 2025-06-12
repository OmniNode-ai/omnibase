from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from omnibase.registry.registry_external_service_manager import RegistryExternalServiceHealthResult


class PreConditionStatusEnum(str, Enum):
    """Status of a pre-condition check."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    SKIPPED = "skipped"
    ERROR = "error"


class ModelServicePreConditionResult(BaseModel):
    """Result of a single service pre-condition check."""
    service_name: str = Field(..., description="Name of the external service")
    status: PreConditionStatusEnum = Field(..., description="Pre-condition check status")
    is_required: bool = Field(..., description="Whether this service is required for the scenario")
    response_time_ms: Optional[float] = Field(None, description="Health check response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if check failed")
    details: Dict = Field(default_factory=dict, description="Additional diagnostic details")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the check was performed")
    
    @classmethod
    def from_health_result(
        cls, 
        health_result: RegistryExternalServiceHealthResult, 
        is_required: bool
    ) -> "ModelServicePreConditionResult":
        """Create from a health check result."""
        if health_result.is_healthy:
            status = PreConditionStatusEnum.HEALTHY
        else:
            status = PreConditionStatusEnum.UNHEALTHY
            
        return cls(
            service_name=health_result.service_name,
            status=status,
            is_required=is_required,
            response_time_ms=health_result.response_time_ms,
            error_message=health_result.error_message,
            details=health_result.details,
            timestamp=health_result.timestamp
        )
    
    def get_status_icon(self) -> str:
        """Get a visual status indicator."""
        icons = {
            PreConditionStatusEnum.HEALTHY: "✓",
            PreConditionStatusEnum.UNHEALTHY: "✗", 
            PreConditionStatusEnum.SKIPPED: "⚠",
            PreConditionStatusEnum.ERROR: "⊘"
        }
        return icons.get(self.status, "?")


class ModelScenarioPreConditionResult(BaseModel):
    """
    Canonical model for scenario pre-condition validation results.
    Contains structured reporting of all service health checks and timing metrics.
    """
    scenario_name: str = Field(..., description="Name of the scenario being validated")
    overall_status: PreConditionStatusEnum = Field(..., description="Overall pre-condition status")
    services_checked: List[ModelServicePreConditionResult] = Field(
        default_factory=list, 
        description="Results for each service checked"
    )
    total_check_time_ms: float = Field(..., description="Total time for all pre-condition checks")
    required_services_healthy: bool = Field(..., description="Whether all required services are healthy")
    optional_services_count: int = Field(0, description="Number of optional services checked")
    required_services_count: int = Field(0, description="Number of required services checked")
    skipped_reason: Optional[str] = Field(None, description="Reason if pre-conditions were skipped")
    timestamp: datetime = Field(default_factory=datetime.now, description="When pre-condition validation started")
    
    def should_skip_scenario(self) -> bool:
        """Determine if the scenario should be skipped based on pre-condition results."""
        if self.overall_status == PreConditionStatusEnum.SKIPPED:
            return True
        
        # Skip if any required service is unhealthy
        for service_result in self.services_checked:
            if service_result.is_required and service_result.status == PreConditionStatusEnum.UNHEALTHY:
                return True
                
        return False
    
    def get_summary_message(self) -> str:
        """Get a human-readable summary of pre-condition results."""
        if self.overall_status == PreConditionStatusEnum.SKIPPED:
            return f"⚠ Pre-conditions skipped: {self.skipped_reason}"
        
        healthy_count = sum(1 for s in self.services_checked if s.status == PreConditionStatusEnum.HEALTHY)
        total_count = len(self.services_checked)
        
        if self.required_services_healthy:
            return f"✓ Pre-conditions passed: {healthy_count}/{total_count} services healthy ({self.total_check_time_ms:.1f}ms)"
        else:
            unhealthy_services = [s.service_name for s in self.services_checked 
                                if s.is_required and s.status == PreConditionStatusEnum.UNHEALTHY]
            return f"✗ Pre-conditions failed: Required services unhealthy: {', '.join(unhealthy_services)}"
    
    def get_detailed_log_entries(self) -> List[str]:
        """Get detailed log entries for each service check."""
        entries = []
        for service_result in self.services_checked:
            icon = service_result.get_status_icon()
            required_text = "REQUIRED" if service_result.is_required else "OPTIONAL"
            time_text = f"({service_result.response_time_ms:.1f}ms)" if service_result.response_time_ms else ""
            
            if service_result.status == PreConditionStatusEnum.HEALTHY:
                entries.append(f"{icon} {service_result.service_name} [{required_text}] HEALTHY {time_text}")
            elif service_result.status == PreConditionStatusEnum.UNHEALTHY:
                error_text = f": {service_result.error_message}" if service_result.error_message else ""
                entries.append(f"{icon} {service_result.service_name} [{required_text}] UNHEALTHY{error_text}")
            elif service_result.status == PreConditionStatusEnum.SKIPPED:
                entries.append(f"{icon} {service_result.service_name} [{required_text}] SKIPPED")
            else:
                entries.append(f"{icon} {service_result.service_name} [{required_text}] ERROR")
                
        return entries 