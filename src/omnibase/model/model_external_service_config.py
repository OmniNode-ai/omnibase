from typing import Any, Dict, Optional, List, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path
import re


# === Service-Specific Connection Config Models ===

class ModelKafkaConnectionConfig(BaseModel):
    """Validated connection configuration for Kafka services."""
    bootstrap_servers: str = Field(
        "localhost:9092",
        description="Kafka bootstrap servers",
        pattern=r"^[a-zA-Z0-9\-\.,:\s]+$",
        max_length=500
    )
    topic_prefix: Optional[str] = Field(
        None,
        description="Prefix for Kafka topics",
        pattern=r"^[a-zA-Z0-9_\-]+$",
        max_length=100
    )
    consumer_group: Optional[str] = Field(
        None,
        description="Kafka consumer group ID",
        pattern=r"^[a-zA-Z0-9_\-]+$",
        max_length=100
    )
    timeout_ms: int = Field(
        5000,
        description="Connection timeout in milliseconds",
        ge=1000,
        le=60000
    )
    security_protocol: Optional[str] = Field(
        "PLAINTEXT",
        description="Security protocol for Kafka connection",
        pattern=r"^(PLAINTEXT|SSL|SASL_PLAINTEXT|SASL_SSL)$"
    )
    sasl_username: Optional[str] = Field(
        None,
        description="SASL username for authentication",
        max_length=100
    )
    sasl_password: Optional[str] = Field(
        None,
        description="SASL password for authentication",
        max_length=200
    )
    ssl_keyfile: Optional[str] = Field(
        None,
        description="Path to SSL key file",
        max_length=500
    )
    ssl_certfile: Optional[str] = Field(
        None,
        description="Path to SSL certificate file",
        max_length=500
    )
    ssl_cafile: Optional[str] = Field(
        None,
        description="Path to SSL CA file",
        max_length=500
    )


class ModelDatabaseConnectionConfig(BaseModel):
    """Validated connection configuration for database services."""
    host: str = Field(
        "localhost",
        description="Database host",
        pattern=r"^[a-zA-Z0-9\-\.]+$",
        max_length=255
    )
    port: int = Field(
        5432,
        description="Database port",
        ge=1,
        le=65535
    )
    database: str = Field(
        ...,
        description="Database name",
        pattern=r"^[a-zA-Z0-9_\-]+$",
        max_length=100
    )
    username: str = Field(
        ...,
        description="Database username",
        pattern=r"^[a-zA-Z0-9_\-]+$",
        max_length=100
    )
    password: Optional[str] = Field(
        None,
        description="Database password",
        max_length=200
    )
    ssl_mode: Optional[str] = Field(
        "prefer",
        description="SSL mode for database connection",
        pattern=r"^(disable|allow|prefer|require|verify-ca|verify-full)$"
    )
    connection_timeout: int = Field(
        30,
        description="Connection timeout in seconds",
        ge=1,
        le=300
    )


class ModelRestApiConnectionConfig(BaseModel):
    """Validated connection configuration for REST API services."""
    base_url: str = Field(
        ...,
        description="Base URL for the REST API",
        pattern=r"^https?://[a-zA-Z0-9\-\.:]+(/.*)?$",
        max_length=500
    )
    api_key: Optional[str] = Field(
        None,
        description="API key for authentication",
        max_length=200
    )
    bearer_token: Optional[str] = Field(
        None,
        description="Bearer token for authentication",
        max_length=500
    )
    timeout_seconds: int = Field(
        30,
        description="Request timeout in seconds",
        ge=1,
        le=300
    )
    max_retries: int = Field(
        3,
        description="Maximum number of retries",
        ge=0,
        le=10
    )
    headers: Optional[Dict[str, str]] = Field(
        None,
        description="Additional HTTP headers"
    )

    @field_validator('headers')
    @classmethod
    def validate_headers(cls, v):
        if v is not None:
            # Limit number of headers and their sizes
            if len(v) > 20:
                raise ValueError("Too many headers (max 20)")
            for key, value in v.items():
                if len(key) > 100 or len(value) > 500:
                    raise ValueError("Header key or value too long")
        return v


# === Security Utilities ===

class SecurityUtils:
    """Utility functions for security operations."""
    
    SENSITIVE_FIELD_PATTERNS = [
        r'.*password.*',
        r'.*token.*',
        r'.*key.*',
        r'.*secret.*',
        r'.*credential.*',
        r'.*auth.*'
    ]
    
    @classmethod
    def mask_sensitive_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive fields in configuration data for logging."""
        if not isinstance(data, dict):
            return data
            
        masked_data = {}
        for key, value in data.items():
            key_lower = key.lower()
            is_sensitive = any(
                re.match(pattern, key_lower, re.IGNORECASE) 
                for pattern in cls.SENSITIVE_FIELD_PATTERNS
            )
            
            if is_sensitive and value is not None:
                if isinstance(value, str) and len(value) > 0:
                    # Show first 2 and last 2 characters, mask the rest
                    if len(value) <= 4:
                        masked_data[key] = "***"
                    else:
                        masked_data[key] = f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
                else:
                    masked_data[key] = "***"
            else:
                masked_data[key] = value
                
        return masked_data
    
    @classmethod
    def validate_service_name(cls, service_name: str) -> bool:
        """Validate service name format."""
        if not service_name or len(service_name) > 100:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_\-]+$', service_name))
    
    @classmethod
    def validate_service_type(cls, service_type: str) -> bool:
        """Validate service type against known types."""
        valid_types = {
            'event_bus', 'kafka', 'database', 'postgres', 'mysql', 
            'rest_api', 'http', 'redis', 'mongodb', 'elasticsearch'
        }
        return service_type.lower() in valid_types


class ModelExternalServiceConfig(BaseModel):
    """
    Canonical model for external service configuration in scenarios.
    Used when dependency_mode is 'real' to configure connections to external services.
    Enhanced with security validation and service-specific configuration schemas.
    """
    service_name: str = Field(
        ..., 
        description="Name of the external service (e.g., 'kafka', 'database', 'api')",
        pattern=r"^[a-zA-Z0-9_\-]+$",
        max_length=100
    )
    service_type: str = Field(
        ..., 
        description="Type of service (e.g., 'event_bus', 'database', 'rest_api')",
        pattern=r"^[a-zA-Z0-9_\-]+$",
        max_length=50
    )
    connection_config: Union[
        ModelKafkaConnectionConfig,
        ModelDatabaseConnectionConfig, 
        ModelRestApiConnectionConfig,
        Dict[str, Any]  # Fallback for unknown service types
    ] = Field(
        default_factory=dict,
        description="Service-specific connection configuration with validation"
    )
    health_check_enabled: bool = Field(
        True, 
        description="Whether to perform health checks before using this service"
    )
    health_check_timeout: int = Field(
        5, 
        description="Timeout in seconds for health check operations",
        ge=1,
        le=300
    )
    required: bool = Field(
        True,
        description="Whether this service is required for the scenario. If False, gracefully degrade if unavailable."
    )
    retry_config: Optional['ModelRetryConfig'] = Field(
        None,
        description="Retry configuration for service operations"
    )

    @model_validator(mode='before')
    @classmethod
    def validate_connection_config_by_service_type(cls, values):
        """Validate connection_config based on service_type."""
        if not isinstance(values, dict):
            return values
            
        service_type = values.get('service_type', '').lower()
        connection_config = values.get('connection_config', {})
        
        # If connection_config is already a validated model, keep it
        if isinstance(connection_config, (ModelKafkaConnectionConfig, ModelDatabaseConnectionConfig, ModelRestApiConnectionConfig)):
            return values
        
        # Validate based on service type
        if service_type in ['kafka', 'event_bus']:
            try:
                values['connection_config'] = ModelKafkaConnectionConfig(**connection_config)
            except Exception as e:
                raise ValueError(f"Invalid Kafka connection config: {e}")
        elif service_type in ['database', 'postgres', 'mysql']:
            try:
                values['connection_config'] = ModelDatabaseConnectionConfig(**connection_config)
            except Exception as e:
                raise ValueError(f"Invalid database connection config: {e}")
        elif service_type in ['rest_api', 'http']:
            try:
                values['connection_config'] = ModelRestApiConnectionConfig(**connection_config)
            except Exception as e:
                raise ValueError(f"Invalid REST API connection config: {e}")
        # For unknown service types, keep as dict but validate it's not too large
        elif isinstance(connection_config, dict):
            if len(connection_config) > 50:
                raise ValueError("Connection config has too many fields (max 50)")
            for key, value in connection_config.items():
                if isinstance(key, str) and len(key) > 100:
                    raise ValueError(f"Connection config key too long: {key}")
                if isinstance(value, str) and len(value) > 1000:
                    raise ValueError(f"Connection config value too long for key: {key}")
        
        return values

    @field_validator('service_name')
    @classmethod
    def validate_service_name_security(cls, v):
        """Additional security validation for service name."""
        if not SecurityUtils.validate_service_name(v):
            raise ValueError("Invalid service name format")
        return v

    @field_validator('service_type')
    @classmethod
    def validate_service_type_security(cls, v):
        """Additional security validation for service type."""
        if not SecurityUtils.validate_service_type(v):
            raise ValueError(f"Unknown or invalid service type: {v}")
        return v

    def get_masked_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive fields masked for logging."""
        config_dict = self.dict()
        if isinstance(config_dict.get('connection_config'), dict):
            config_dict['connection_config'] = SecurityUtils.mask_sensitive_data(
                config_dict['connection_config']
            )
        return config_dict

    def get_connection_string_safe(self) -> str:
        """Get a safe connection string for logging (no credentials)."""
        if isinstance(self.connection_config, ModelKafkaConnectionConfig):
            return f"kafka://{self.connection_config.bootstrap_servers}"
        elif isinstance(self.connection_config, ModelDatabaseConnectionConfig):
            return f"db://{self.connection_config.host}:{self.connection_config.port}/{self.connection_config.database}"
        elif isinstance(self.connection_config, ModelRestApiConnectionConfig):
            return f"api://{self.connection_config.base_url}"
        else:
            return f"{self.service_type}://[configured]"


class ModelRetryConfig(BaseModel):
    """Configuration for retry behavior with external services."""
    max_attempts: int = Field(
        3, 
        description="Maximum number of retry attempts",
        ge=1,
        le=10
    )
    backoff_seconds: float = Field(
        1.0, 
        description="Base backoff time between retries",
        ge=0.1,
        le=60.0
    )
    exponential_backoff: bool = Field(
        True, 
        description="Whether to use exponential backoff"
    )


class ModelTemplateVariables(BaseModel):
    """
    Canonical model for scenario template variables.
    Used with scenario inheritance ('extends' field) for parameterized templates.
    """
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs for template variable substitution"
    )
    
    @field_validator('variables')
    @classmethod
    def validate_variables_size(cls, v):
        """Limit the size of template variables."""
        if len(v) > 100:
            raise ValueError("Too many template variables (max 100)")
        for key, value in v.items():
            if isinstance(key, str) and len(key) > 100:
                raise ValueError(f"Template variable key too long: {key}")
            if isinstance(value, str) and len(value) > 1000:
                raise ValueError(f"Template variable value too long for key: {key}")
        return v
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a template variable with optional default."""
        return self.variables.get(key, default)
    
    def set_variable(self, key: str, value: Any) -> None:
        """Set a template variable."""
        if len(key) > 100:
            raise ValueError("Template variable key too long")
        if isinstance(value, str) and len(value) > 1000:
            raise ValueError("Template variable value too long")
        self.variables[key] = value 