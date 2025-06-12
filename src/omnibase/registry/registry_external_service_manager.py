from typing import Dict, Optional, List
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

from omnibase.model.model_external_service_config import ModelExternalServiceConfig, SecurityUtils
from omnibase.enums.enum_dependency_mode import DependencyModeEnum
from omnibase.core.core_errors import OnexError, CoreErrorCode
from omnibase.protocol.protocol_logger import ProtocolLogger


class RegistryExternalServiceHealthResult:
    """
    Result of an external service health check.
    Contains health status, timing, and diagnostic information.
    """
    
    def __init__(
        self, 
        service_name: str, 
        is_healthy: bool, 
        response_time_ms: Optional[float] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        self.service_name = service_name
        self.is_healthy = is_healthy
        self.response_time_ms = response_time_ms
        self.error_message = error_message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def __repr__(self) -> str:
        status = "HEALTHY" if self.is_healthy else "UNHEALTHY"
        return f"HealthResult({self.service_name}: {status})"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "service_name": self.service_name,
            "is_healthy": self.is_healthy,
            "response_time_ms": self.response_time_ms,
            "error_message": self.error_message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class RegistryRateLimiter:
    """Simple rate limiter for health check operations."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[datetime]] = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed under rate limiting."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key] 
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self._requests[key]) >= self.max_requests:
            return False
        
        # Record this request
        self._requests[key].append(now)
        return True
    
    def get_remaining_requests(self, key: str) -> int:
        """Get number of remaining requests in current window."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key] 
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(self._requests[key]))


class RegistryBaseExternalServiceChecker(ABC):
    """Abstract base class for external service health checkers."""
    
    def __init__(self, logger: Optional[ProtocolLogger] = None):
        self.logger = logger
    
    @abstractmethod
    async def check_health(self, config: ModelExternalServiceConfig) -> RegistryExternalServiceHealthResult:
        """Check if the external service is healthy and available."""
        pass
    
    @abstractmethod
    def supports_service_type(self, service_type: str) -> bool:
        """Check if this checker supports the given service type."""
        pass
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message if logger is available."""
        if self.logger:
            self.logger.log(f"[{self.__class__.__name__}] {message}")


class RegistryKafkaServiceChecker(RegistryBaseExternalServiceChecker):
    """Health checker for Kafka services."""
    
    def supports_service_type(self, service_type: str) -> bool:
        """Check if this checker supports Kafka-related service types."""
        return service_type.lower() in ["event_bus", "kafka", "message_queue"]
    
    async def check_health(self, config: ModelExternalServiceConfig) -> RegistryExternalServiceHealthResult:
        """Check Kafka broker health."""
        start_time = datetime.now()
        
        # Log with masked configuration
        masked_config = config.get_masked_config()
        safe_connection = config.get_connection_string_safe()
        self.log(f"Checking Kafka health at {safe_connection}")
        
        try:
            # Import Kafka dependencies
            try:
                from aiokafka import AIOKafkaProducer
                from aiokafka.errors import KafkaError
            except ImportError as e:
                return RegistryExternalServiceHealthResult(
                    service_name=config.service_name,
                    is_healthy=False,
                    error_message=f"Kafka dependencies not available: {e}"
                )
            
            # Get connection configuration safely
            if hasattr(config.connection_config, 'bootstrap_servers'):
                bootstrap_servers = config.connection_config.bootstrap_servers
                timeout_ms = getattr(config.connection_config, 'timeout_ms', 5000)
            else:
                # Fallback for dict-based config
                connection_config = config.connection_config or {}
                bootstrap_servers = connection_config.get("bootstrap_servers", "localhost:9092")
                timeout_ms = connection_config.get("timeout_ms", 5000)
            
            self.log(f"Connecting to Kafka at {bootstrap_servers} (timeout: {timeout_ms}ms)")
            
            # Create producer for health check
            producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                request_timeout_ms=timeout_ms,
                api_version="auto"
            )
            
            try:
                # Start producer (this will connect and fetch metadata)
                await asyncio.wait_for(producer.start(), timeout=timeout_ms/1000)
                
                # Get cluster metadata to verify connection
                # The start() method already validates connection, so if we get here, it's healthy
                metadata = producer.client.cluster
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                # Success - Kafka is reachable
                broker_count = len(metadata.brokers())
                topic_count = len(metadata.topics())
                
                self.log(f"Kafka health check passed: {broker_count} brokers, {topic_count} topics")
                
                return RegistryExternalServiceHealthResult(
                    service_name=config.service_name,
                    is_healthy=True,
                    response_time_ms=response_time,
                    details={
                        "broker_count": broker_count,
                        "topic_count": topic_count,
                        "bootstrap_servers": bootstrap_servers,  # Safe to log (no credentials)
                        "api_version": str(producer.client.api_version)
                    }
                )
                
            finally:
                try:
                    await producer.stop()
                except Exception:
                    pass  # Ignore stop errors
                    
        except asyncio.TimeoutError:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log(f"Kafka health check timeout after {response_time}ms")
            return RegistryExternalServiceHealthResult(
                service_name=config.service_name,
                is_healthy=False,
                response_time_ms=response_time,
                error_message=f"Connection timeout after {timeout_ms}ms"
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            # Mask any sensitive information in error messages
            error_msg = str(e)
            if any(sensitive in error_msg.lower() for sensitive in ['password', 'token', 'key', 'secret']):
                error_msg = "Authentication or connection error (details masked for security)"
            
            self.log(f"Kafka health check failed: {error_msg}")
            return RegistryExternalServiceHealthResult(
                service_name=config.service_name,
                is_healthy=False,
                response_time_ms=response_time,
                error_message=error_msg
            )


class RegistryExternalServiceManager:
    """
    Manager for external service validation, health checks, and lifecycle operations.
    Used by the registry resolver to validate services before running real dependency scenarios.
    Enhanced with rate limiting and security features.
    """
    
    def __init__(self, logger: Optional[ProtocolLogger] = None):
        self.logger = logger
        self._health_checkers: List[RegistryBaseExternalServiceChecker] = []
        self._health_cache: Dict[str, RegistryExternalServiceHealthResult] = {}
        self._cache_ttl_seconds = 60  # Cache health results for 1 minute
        self._rate_limiter = RegistryRateLimiter(max_requests=20, window_seconds=60)  # 20 requests per minute
        self._register_default_checkers()
    
    def _register_default_checkers(self) -> None:
        """Register default service health checkers."""
        self.register_health_checker(RegistryKafkaServiceChecker(self.logger))
    
    def register_health_checker(self, checker: RegistryBaseExternalServiceChecker) -> None:
        """Register a health checker for a specific service type."""
        self._health_checkers.append(checker)
        if self.logger:
            self.logger.log(f"[RegistryExternalServiceManager] Registered health checker: {checker.__class__.__name__}")
    
    def _get_cache_key(self, config: ModelExternalServiceConfig) -> str:
        """Generate cache key for health check result."""
        # Use safe connection string for cache key (no credentials)
        safe_connection = config.get_connection_string_safe()
        return f"{config.service_name}:{config.service_type}:{safe_connection}"
    
    def _get_rate_limit_key(self, config: ModelExternalServiceConfig) -> str:
        """Generate rate limiting key for service."""
        return f"{config.service_type}:{config.service_name}"
    
    def _is_cache_valid(self, result: RegistryExternalServiceHealthResult) -> bool:
        """Check if cached health result is still valid."""
        age = datetime.now() - result.timestamp
        return age < timedelta(seconds=self._cache_ttl_seconds)
    
    async def validate_service_availability(self, config: ModelExternalServiceConfig) -> RegistryExternalServiceHealthResult:
        """
        Validate that an external service is available and healthy.
        Uses caching and rate limiting to prevent abuse.
        """
        # Check rate limiting first
        rate_limit_key = self._get_rate_limit_key(config)
        if not self._rate_limiter.is_allowed(rate_limit_key):
            remaining = self._rate_limiter.get_remaining_requests(rate_limit_key)
            return RegistryExternalServiceHealthResult(
                service_name=config.service_name,
                is_healthy=False,
                error_message=f"Rate limit exceeded. {remaining} requests remaining in current window."
            )
        
        if not config.health_check_enabled:
            # Health check disabled - assume healthy
            return RegistryExternalServiceHealthResult(
                service_name=config.service_name,
                is_healthy=True,
                details={"health_check": "disabled"}
            )
        
        # Check cache first
        cache_key = self._get_cache_key(config)
        if cache_key in self._health_cache:
            cached_result = self._health_cache[cache_key]
            if self._is_cache_valid(cached_result):
                if self.logger:
                    self.logger.log(f"[RegistryExternalServiceManager] Using cached health result for {config.service_name}")
                return cached_result
        
        # Find appropriate health checker
        checker = None
        for health_checker in self._health_checkers:
            if health_checker.supports_service_type(config.service_type):
                checker = health_checker
                break
        
        if not checker:
            result = RegistryExternalServiceHealthResult(
                service_name=config.service_name,
                is_healthy=False,
                error_message=f"No health checker available for service type: {config.service_type}"
            )
        else:
            # Perform health check with timeout
            timeout = config.health_check_timeout or 10
            try:
                result = await asyncio.wait_for(
                    checker.check_health(config), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                result = RegistryExternalServiceHealthResult(
                    service_name=config.service_name,
                    is_healthy=False,
                    error_message=f"Health check timeout after {timeout} seconds"
                )
            except Exception as e:
                # Mask sensitive information in error messages
                error_msg = str(e)
                if any(sensitive in error_msg.lower() for sensitive in ['password', 'token', 'key', 'secret']):
                    error_msg = "Health check failed (details masked for security)"
                
                result = RegistryExternalServiceHealthResult(
                    service_name=config.service_name,
                    is_healthy=False,
                    error_message=error_msg
                )
        
        # Cache result
        self._health_cache[cache_key] = result
        
        if self.logger:
            status = "✓ HEALTHY" if result.is_healthy else "✗ UNHEALTHY"
            safe_connection = config.get_connection_string_safe()
            self.logger.log(f"[RegistryExternalServiceManager] {config.service_name} ({safe_connection}): {status}")
            if result.error_message:
                self.logger.log(f"[RegistryExternalServiceManager] Error: {result.error_message}")
        
        return result
    
    async def validate_all_services(
        self, 
        services: Dict[str, ModelExternalServiceConfig]
    ) -> Dict[str, RegistryExternalServiceHealthResult]:
        """Validate health of all external services concurrently."""
        if not services:
            return {}
        
        if self.logger:
            self.logger.log(f"[RegistryExternalServiceManager] Validating {len(services)} external services")
        
        # Run health checks concurrently
        tasks = []
        service_names = []
        for service_name, config in services.items():
            tasks.append(self.validate_service_availability(config))
            service_names.append(service_name)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build results dictionary
        health_results = {}
        for i, result in enumerate(results):
            service_name = service_names[i]
            if isinstance(result, Exception):
                health_results[service_name] = RegistryExternalServiceHealthResult(
                    service_name=service_name,
                    is_healthy=False,
                    error_message=f"Health check exception: {result}"
                )
            else:
                health_results[service_name] = result
        
        # Log summary
        healthy_count = sum(1 for r in health_results.values() if r.is_healthy)
        total_count = len(health_results)
        if self.logger:
            self.logger.log(f"[RegistryExternalServiceManager] Health check results: {healthy_count}/{total_count} healthy")
        
        return health_results
    
    def are_all_services_healthy(self, health_results: Dict[str, RegistryExternalServiceHealthResult]) -> bool:
        """Check if all services in the results are healthy."""
        return all(result.is_healthy for result in health_results.values())
    
    def get_unhealthy_services(self, health_results: Dict[str, RegistryExternalServiceHealthResult]) -> List[str]:
        """Get list of unhealthy service names."""
        return [name for name, result in health_results.items() if not result.is_healthy]
    
    async def wait_for_service_ready(
        self, 
        config: ModelExternalServiceConfig, 
        max_wait_seconds: int = 30,
        check_interval_seconds: int = 2
    ) -> bool:
        """
        Wait for a service to become healthy, with polling.
        Returns True if service becomes healthy, False if timeout.
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < max_wait_seconds:
            result = await self.validate_service_availability(config)
            if result.is_healthy:
                return True
            
            if self.logger:
                self.logger.log(f"[RegistryExternalServiceManager] Waiting for {config.service_name} to become healthy...")
            
            await asyncio.sleep(check_interval_seconds)
        
        return False
    
    def clear_health_cache(self) -> None:
        """Clear all cached health check results."""
        self._health_cache.clear()
        if self.logger:
            self.logger.log("[RegistryExternalServiceManager] Health check cache cleared")


# Global instance
_global_external_service_manager: Optional[RegistryExternalServiceManager] = None


def get_external_service_manager(logger: Optional[ProtocolLogger] = None) -> RegistryExternalServiceManager:
    """Get the global external service manager instance."""
    global _global_external_service_manager
    if _global_external_service_manager is None:
        _global_external_service_manager = RegistryExternalServiceManager(logger)
    return _global_external_service_manager 