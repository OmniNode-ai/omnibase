"""
Service Manager Tool for ONEX Development Services

Provides automated lifecycle management for development services including:
- Docker Compose service orchestration
- Service health monitoring and readiness polling
- Environment variable configuration
- Service discovery and dependency validation
"""

import asyncio
import subprocess
import time
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum
from pydantic import BaseModel, Field

import yaml
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context
from omnibase.enums.log_level import LogLevelEnum


class ServiceStatusEnum(str, Enum):
    """Status of a development service."""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceTypeEnum(str, Enum):
    """Type of development service."""
    KAFKA = "kafka"
    POSTGRES = "postgres"
    REDIS = "redis"
    ZOOKEEPER = "zookeeper"
    KAFKA_UI = "kafka-ui"
    PGADMIN = "pgadmin"


class ModelServiceConfig(BaseModel):
    """Configuration for a development service."""
    name: str = Field(..., description="Service name")
    service_type: ServiceTypeEnum = Field(..., description="Type of service")
    container_name: str = Field(..., description="Docker container name")
    ports: List[int] = Field(default_factory=list, description="Exposed ports")
    health_check_url: Optional[str] = Field(None, description="Health check endpoint")
    health_check_command: Optional[List[str]] = Field(None, description="Health check command")
    dependencies: List[str] = Field(default_factory=list, description="Service dependencies")
    required: bool = Field(True, description="Whether service is required for development")
    startup_timeout: int = Field(60, description="Startup timeout in seconds")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variable overrides")


class ModelServiceStatus(BaseModel):
    """Status information for a development service."""
    name: str = Field(..., description="Service name")
    status: ServiceStatusEnum = Field(..., description="Current status")
    container_id: Optional[str] = Field(None, description="Docker container ID")
    uptime: Optional[int] = Field(None, description="Uptime in seconds")
    health_check_status: Optional[str] = Field(None, description="Health check result")
    ports: List[int] = Field(default_factory=list, description="Exposed ports")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    last_checked: Optional[str] = Field(None, description="Last health check timestamp")


class ModelServiceManagerResult(BaseModel):
    """Result of a service manager operation."""
    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Operation result message")
    services: List[ModelServiceStatus] = Field(default_factory=list, description="Service status list")
    operation_time_ms: Optional[int] = Field(None, description="Operation duration in milliseconds")
    errors: List[str] = Field(default_factory=list, description="Error messages")


class ToolServiceManager:
    """
    Tool for managing ONEX development services via Docker Compose.
    
    Provides automated lifecycle management including:
    - Service startup/shutdown with dependency ordering
    - Health monitoring and readiness polling
    - Service discovery and status reporting
    - Environment variable configuration
    """
    
    def __init__(self, compose_file: Path = None, node_id: str = "tool_service_manager", config_file: Path = None):
        self.compose_file = compose_file or Path("docker-compose.dev.yml")
        self.config_file = config_file or Path("config/services.yaml")
        self.node_id = node_id
        self.services_config = self._load_service_configurations()
        
    def _load_service_configurations(self) -> Dict[str, ModelServiceConfig]:
        """Load service configurations from external YAML file."""
        configs = {}
        
        try:
            # Try to load from external config file
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[ToolServiceManager] Loaded service configurations from {self.config_file}",
                    context=make_log_context(node_id=self.node_id)
                )
                
                # Parse service configurations
                for service_name, service_config in config_data.get('services', {}).items():
                    try:
                        # Convert YAML config to ModelServiceConfig
                        config = ModelServiceConfig(
                            name=service_config['name'],
                            service_type=ServiceTypeEnum(service_config['service_type']),
                            container_name=service_config['container_name'],
                            ports=service_config.get('ports', []),
                            health_check_command=service_config.get('health_check_command'),
                            dependencies=service_config.get('dependencies', []),
                            required=service_config.get('required', True),
                            startup_timeout=service_config.get('startup_timeout', 60),
                            environment_variables=service_config.get('environment_variables', {})
                        )
                        configs[service_name] = config
                        
                    except Exception as e:
                        emit_log_event_sync(
                            LogLevelEnum.WARNING,
                            f"[ToolServiceManager] Failed to parse service config for {service_name}: {e}",
                            context=make_log_context(node_id=self.node_id)
                        )
                
                return configs
                
            else:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[ToolServiceManager] Config file {self.config_file} not found, using fallback configurations",
                    context=make_log_context(node_id=self.node_id)
                )
                
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[ToolServiceManager] Failed to load config file {self.config_file}: {e}",
                context=make_log_context(node_id=self.node_id)
            )
        
        # Fallback to minimal hardcoded configurations if external config fails
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[ToolServiceManager] Using fallback service configurations",
            context=make_log_context(node_id=self.node_id)
        )
        
        configs["kafka"] = ModelServiceConfig(
            name="kafka",
            service_type=ServiceTypeEnum.KAFKA,
            container_name="onex-kafka",
            ports=[9092, 9101],
            health_check_command=["kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"],
            dependencies=["zookeeper"],
            startup_timeout=120
        )
        
        configs["zookeeper"] = ModelServiceConfig(
            name="zookeeper",
            service_type=ServiceTypeEnum.ZOOKEEPER,
            container_name="onex-zookeeper",
            ports=[2181],
            health_check_command=["bash", "-c", "echo 'ruok' | nc localhost 2181"],
            startup_timeout=60
        )
        
        return configs
    
    async def start_services(self, service_names: Optional[List[str]] = None, correlation_id: Optional[str] = None) -> ModelServiceManagerResult:
        """
        Start development services with dependency ordering.
        
        Args:
            service_names: List of service names to start (None for all)
            correlation_id: Correlation ID for logging
            
        Returns:
            Service manager result with status information
        """
        start_time = time.time()
        
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[ToolServiceManager] Starting services: {service_names or 'all'}",
            context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
        )
        
        try:
            # Determine services to start
            if service_names is None:
                services_to_start = list(self.services_config.keys())
            else:
                services_to_start = service_names
            
            # Resolve dependencies and create startup order
            startup_order = self._resolve_startup_order(services_to_start)
            
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"[ToolServiceManager] Startup order: {startup_order}",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
            )
            
            # Start services in dependency order
            started_services = []
            errors = []
            
            for service_name in startup_order:
                try:
                    await self._start_single_service(service_name, correlation_id)
                    started_services.append(service_name)
                    
                    # Wait for service to be ready
                    await self._wait_for_service_ready(service_name, correlation_id)
                    
                except Exception as e:
                    error_msg = f"Failed to start service {service_name}: {e}"
                    errors.append(error_msg)
                    emit_log_event_sync(
                        LogLevelEnum.ERROR,
                        f"[ToolServiceManager] {error_msg}",
                        context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
                    )
            
            # Get final status of all services
            service_statuses = await self.get_service_status(correlation_id=correlation_id)
            
            operation_time = int((time.time() - start_time) * 1000)
            success = len(errors) == 0
            
            result = ModelServiceManagerResult(
                success=success,
                message=f"Started {len(started_services)} services" + (f" with {len(errors)} errors" if errors else ""),
                services=service_statuses.services,
                operation_time_ms=operation_time,
                errors=errors
            )
            
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[ToolServiceManager] Service startup completed: {result.message}",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
            )
            
            return result
            
        except Exception as e:
            operation_time = int((time.time() - start_time) * 1000)
            error_msg = f"Service startup failed: {e}"
            
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[ToolServiceManager] {error_msg}",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
            )
            
            return ModelServiceManagerResult(
                success=False,
                message=error_msg,
                operation_time_ms=operation_time,
                errors=[error_msg]
            )
    
    async def stop_services(self, service_names: Optional[List[str]] = None, correlation_id: Optional[str] = None) -> ModelServiceManagerResult:
        """
        Stop development services with reverse dependency ordering.
        
        Args:
            service_names: List of service names to stop (None for all)
            correlation_id: Correlation ID for logging
            
        Returns:
            Service manager result with status information
        """
        start_time = time.time()
        
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[ToolServiceManager] Stopping services: {service_names or 'all'}",
            context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
        )
        
        try:
            # Use docker-compose down for clean shutdown
            cmd = ["docker-compose", "-f", str(self.compose_file), "down"]
            if service_names:
                cmd.extend(service_names)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                operation_time = int((time.time() - start_time) * 1000)
                
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[ToolServiceManager] Services stopped successfully",
                    context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
                )
                
                return ModelServiceManagerResult(
                    success=True,
                    message="Services stopped successfully",
                    operation_time_ms=operation_time
                )
            else:
                error_msg = f"Failed to stop services: {result.stderr}"
                
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[ToolServiceManager] {error_msg}",
                    context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
                )
                
                return ModelServiceManagerResult(
                    success=False,
                    message=error_msg,
                    errors=[error_msg]
                )
                
        except Exception as e:
            operation_time = int((time.time() - start_time) * 1000)
            error_msg = f"Service shutdown failed: {e}"
            
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[ToolServiceManager] {error_msg}",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
            )
            
            return ModelServiceManagerResult(
                success=False,
                message=error_msg,
                operation_time_ms=operation_time,
                errors=[error_msg]
            )
    
    async def get_service_status(self, service_names: Optional[List[str]] = None, correlation_id: Optional[str] = None) -> ModelServiceManagerResult:
        """
        Get status of development services with parallel health checks for optimal performance.
        
        Args:
            service_names: Optional list of specific services to check
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            ModelServiceManagerResult with service status information
        """
        start_time = time.time()
        
        try:
            services_to_check = service_names or list(self.services_config.keys())
            
            # Run all service status checks in parallel for maximum performance
            tasks = [
                self._get_single_service_status(service_name, correlation_id)
                for service_name in services_to_check
            ]
            
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"[ToolServiceManager] Checking status of {len(services_to_check)} services in parallel",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
            )
            
            # Execute all status checks concurrently
            service_statuses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions from parallel execution
            final_statuses = []
            for i, result in enumerate(service_statuses):
                if isinstance(result, Exception):
                    # Convert exception to error status
                    service_name = services_to_check[i]
                    error_status = ModelServiceStatus(
                        name=service_name,
                        status=ServiceStatusEnum.UNKNOWN,
                        error_message=f"Status check failed: {result}",
                        ports=self.services_config.get(service_name, ModelServiceConfig(name=service_name, service_type=ServiceTypeEnum.KAFKA, container_name=service_name)).ports
                    )
                    final_statuses.append(error_status)
                else:
                    final_statuses.append(result)
            
            operation_time = int((time.time() - start_time) * 1000)
            
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[ToolServiceManager] Parallel status check completed in {operation_time}ms",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
            )
            
            return ModelServiceManagerResult(
                success=True,
                message=f"Retrieved status for {len(final_statuses)} services in {operation_time}ms (parallel execution)",
                services=final_statuses,
                operation_time_ms=operation_time
            )
            
        except Exception as e:
            operation_time = int((time.time() - start_time) * 1000)
            error_msg = f"Failed to get service status: {e}"
            
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[ToolServiceManager] {error_msg}",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
            )
            
            return ModelServiceManagerResult(
                success=False,
                message=error_msg,
                operation_time_ms=operation_time,
                errors=[error_msg]
            )
    
    def _resolve_startup_order(self, service_names: List[str]) -> List[str]:
        """Resolve service startup order based on dependencies."""
        ordered = []
        remaining = set(service_names)
        
        while remaining:
            # Find services with no unresolved dependencies
            ready = []
            for service_name in remaining:
                config = self.services_config.get(service_name)
                if not config:
                    continue
                    
                deps_satisfied = all(
                    dep in ordered or dep not in service_names
                    for dep in config.dependencies
                )
                
                if deps_satisfied:
                    ready.append(service_name)
            
            if not ready:
                # Circular dependency or missing dependency
                ready = list(remaining)  # Start remaining services anyway
            
            ordered.extend(ready)
            remaining -= set(ready)
        
        return ordered
    
    async def _start_single_service(self, service_name: str, correlation_id: Optional[str] = None):
        """Start a single service using docker-compose."""
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[ToolServiceManager] Starting service: {service_name}",
            context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
        )
        
        cmd = ["docker-compose", "-f", str(self.compose_file), "up", "-d", service_name]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            raise Exception(f"Docker compose failed: {result.stderr}")
    
    async def _wait_for_service_ready(self, service_name: str, correlation_id: Optional[str] = None):
        """Wait for a service to be ready with exponential backoff."""
        config = self.services_config.get(service_name)
        if not config:
            return
        
        timeout = config.startup_timeout
        start_time = time.time()
        backoff = 1
        
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[ToolServiceManager] Waiting for service {service_name} to be ready (timeout: {timeout}s)",
            context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
        )
        
        while time.time() - start_time < timeout:
            try:
                status = await self._get_single_service_status(service_name, correlation_id)
                if status.status == ServiceStatusEnum.RUNNING:
                    emit_log_event_sync(
                        LogLevelEnum.INFO,
                        f"[ToolServiceManager] Service {service_name} is ready",
                        context=make_log_context(node_id=self.node_id, correlation_id=correlation_id)
                    )
                    return
            except Exception:
                pass  # Continue waiting
            
            await asyncio.sleep(backoff)
            backoff = min(backoff * 1.5, 10)  # Exponential backoff with max 10s
        
        raise Exception(f"Service {service_name} failed to become ready within {timeout}s")
    
    async def _get_single_service_status(self, service_name: str, correlation_id: Optional[str] = None) -> ModelServiceStatus:
        """Get status of a single service with optimized container discovery."""
        config = self.services_config.get(service_name)
        if not config:
            return ModelServiceStatus(
                name=service_name,
                status=ServiceStatusEnum.UNKNOWN,
                error_message="Service configuration not found"
            )
        
        try:
            # Optimized: Get all containers in one call and filter locally
            # This is much faster than multiple docker ps calls
            cmd = ["docker", "ps", "-a", "--format", "{{.Names}}\t{{.ID}}\t{{.Status}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return ModelServiceStatus(
                    name=service_name,
                    status=ServiceStatusEnum.UNKNOWN,
                    error_message="Failed to check container status"
                )
            
            # Parse all containers and find matches
            container_info = None
            container_names_to_check = [config.container_name, service_name, f"onex-{service_name}"]
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 3:
                    container_name, container_id, container_status = parts[0], parts[1], parts[2]
                    
                    # Check if this container matches any of our expected names
                    if any(expected_name in container_name for expected_name in container_names_to_check):
                        container_info = (container_id, container_status)
                        break
            
            # If no container found, service is stopped
            if container_info is None:
                return ModelServiceStatus(
                    name=service_name,
                    status=ServiceStatusEnum.STOPPED,
                    ports=config.ports
                )
            
            # Parse container info
            container_id, container_status = container_info
            
            # Determine service status from container status
            if "Up" in container_status:
                status = ServiceStatusEnum.RUNNING
            elif "Exited" in container_status:
                status = ServiceStatusEnum.STOPPED
            elif "Restarting" in container_status:
                status = ServiceStatusEnum.STARTING
            else:
                status = ServiceStatusEnum.UNKNOWN
            
            # Run health check if service is running and health check is configured
            health_check_status = None
            if status == ServiceStatusEnum.RUNNING and config.health_check_command:
                try:
                    health_cmd = ["docker", "exec", container_id] + config.health_check_command
                    health_result = subprocess.run(health_cmd, capture_output=True, text=True, timeout=5)
                    health_check_status = "healthy" if health_result.returncode == 0 else "unhealthy"
                    
                    if health_check_status == "unhealthy":
                        status = ServiceStatusEnum.UNHEALTHY
                        
                except Exception:
                    health_check_status = "unknown"
            
            return ModelServiceStatus(
                name=service_name,
                status=status,
                container_id=container_id,
                health_check_status=health_check_status,
                ports=config.ports,
                last_checked=time.strftime("%Y-%m-%dT%H:%M:%S")
            )
            
        except Exception as e:
            return ModelServiceStatus(
                name=service_name,
                status=ServiceStatusEnum.UNKNOWN,
                error_message=str(e),
                ports=config.ports
            ) 