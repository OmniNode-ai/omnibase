from typing import Any, Dict, Optional, List, Union
from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
from pathlib import Path
import re
import os

from omnibase.enums.enum_dependency_mode import DependencyModeEnum


# === Service-Specific Connection Config Models ===

class ModelKafkaConnectionConfig(BaseModel):
    """Validated connection configuration for Kafka services."""
    bootstrap_servers: str = Field(
        ...,
        description="Kafka bootstrap servers (comma-separated)",
        pattern=r"^[a-zA-Z0-9\-\.:,\s]+$",
        max_length=500
    )
    topic_prefix: Optional[str] = Field(
        None,
        description="Prefix for topic names",
        pattern=r"^[a-zA-Z0-9_\-]*$",
        max_length=50
    )
    consumer_group: Optional[str] = Field(
        None,
        description="Consumer group ID",
        pattern=r"^[a-zA-Z0-9_\-]*$",
        max_length=100
    )
    timeout_ms: int = Field(
        5000,
        description="Connection timeout in milliseconds",
        ge=1000,
        le=300000
    )
    security_protocol: str = Field(
        "PLAINTEXT",
        description="Security protocol (PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)",
        pattern=r"^(PLAINTEXT|SSL|SASL_PLAINTEXT|SASL_SSL)$"
    )
    sasl_username: Optional[str] = Field(
        None,
        description="SASL username for authentication",
        max_length=100
    )
    sasl_password: Optional[SecretStr] = Field(
        None,
        description="SASL password for authentication (secured)"
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

    def apply_environment_overrides(self) -> 'ModelKafkaConnectionConfig':
        """Apply environment variable overrides for CI/local testing."""
        overrides = {}
        
        # Environment variable mappings
        env_mappings = {
            'ONEX_KAFKA_BOOTSTRAP_SERVERS': 'bootstrap_servers',
            'ONEX_KAFKA_SECURITY_PROTOCOL': 'security_protocol',
            'ONEX_KAFKA_SASL_USERNAME': 'sasl_username',
            'ONEX_KAFKA_SASL_PASSWORD': 'sasl_password',
            'ONEX_KAFKA_SSL_KEYFILE': 'ssl_keyfile',
            'ONEX_KAFKA_SSL_CERTFILE': 'ssl_certfile',
            'ONEX_KAFKA_SSL_CAFILE': 'ssl_cafile',
            'ONEX_KAFKA_TIMEOUT_MS': 'timeout_ms',
            'ONEX_KAFKA_TOPIC_PREFIX': 'topic_prefix',
            'ONEX_KAFKA_CONSUMER_GROUP': 'consumer_group',
        }
        
        for env_var, field_name in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # Type conversion for numeric fields
                if field_name == 'timeout_ms':
                    try:
                        overrides[field_name] = int(env_value)
                    except ValueError:
                        continue  # Skip invalid values
                else:
                    overrides[field_name] = env_value
        
        if overrides:
            # Create new instance with overrides
            current_data = self.model_dump()
            current_data.update(overrides)
            return ModelKafkaConnectionConfig(**current_data)
        
        return self


class ModelDatabaseConnectionConfig(BaseModel):
    """Validated connection configuration for database services."""
    host: str = Field(
        ...,
        description="Database host",
        pattern=r"^[a-zA-Z0-9\-\.]+$",
        max_length=255
    )
    port: int = Field(
        ...,
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
        max_length=100
    )
    password: SecretStr = Field(
        ...,
        description="Database password (secured)"
    )
    ssl_enabled: bool = Field(
        False,
        description="Whether to use SSL connection"
    )
    connection_timeout: int = Field(
        30,
        description="Connection timeout in seconds",
        ge=1,
        le=300
    )

    def apply_environment_overrides(self) -> 'ModelDatabaseConnectionConfig':
        """Apply environment variable overrides for CI/local testing."""
        overrides = {}
        
        # Environment variable mappings
        env_mappings = {
            'ONEX_DB_HOST': 'host',
            'ONEX_DB_PORT': 'port',
            'ONEX_DB_DATABASE': 'database',
            'ONEX_DB_USERNAME': 'username',
            'ONEX_DB_PASSWORD': 'password',
            'ONEX_DB_SSL_ENABLED': 'ssl_enabled',
            'ONEX_DB_CONNECTION_TIMEOUT': 'connection_timeout',
        }
        
        for env_var, field_name in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # Type conversion for different field types
                if field_name in ['port', 'connection_timeout']:
                    try:
                        overrides[field_name] = int(env_value)
                    except ValueError:
                        continue
                elif field_name == 'ssl_enabled':
                    overrides[field_name] = env_value.lower() in ('true', '1', 'yes', 'on')
                else:
                    overrides[field_name] = env_value
        
        if overrides:
            current_data = self.model_dump()
            current_data.update(overrides)
            return ModelDatabaseConnectionConfig(**current_data)
        
        return self


class ModelRestApiConnectionConfig(BaseModel):
    """Validated connection configuration for REST API services."""
    base_url: str = Field(
        ...,
        description="Base URL for the REST API",
        pattern=r"^https?://[a-zA-Z0-9\-\.:]+(/.*)?$",
        max_length=500
    )
    api_key: Optional[SecretStr] = Field(
        None,
        description="API key for authentication (secured)"
    )
    bearer_token: Optional[SecretStr] = Field(
        None,
        description="Bearer token for authentication (secured)"
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

    def apply_environment_overrides(self) -> 'ModelRestApiConnectionConfig':
        """Apply environment variable overrides for CI/local testing."""
        overrides = {}
        
        # Environment variable mappings
        env_mappings = {
            'ONEX_API_BASE_URL': 'base_url',
            'ONEX_API_KEY': 'api_key',
            'ONEX_API_BEARER_TOKEN': 'bearer_token',
            'ONEX_API_TIMEOUT_SECONDS': 'timeout_seconds',
            'ONEX_API_MAX_RETRIES': 'max_retries',
        }
        
        for env_var, field_name in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # Type conversion for numeric fields
                if field_name in ['timeout_seconds', 'max_retries']:
                    try:
                        overrides[field_name] = int(env_value)
                    except ValueError:
                        continue
                else:
                    overrides[field_name] = env_value
        
        if overrides:
            current_data = self.model_dump()
            current_data.update(overrides)
            return ModelRestApiConnectionConfig(**current_data)
        
        return self


# === Security Utilities ===

class SecurityUtils:
    """Utility class for credential masking and security operations."""
    
    @staticmethod
    def mask_credential(value: str, mask_char: str = "*", visible_chars: int = 2) -> str:
        """
        Mask a credential string, showing only the first and last few characters.
        
        Args:
            value: The credential to mask
            mask_char: Character to use for masking
            visible_chars: Number of characters to show at start and end
            
        Returns:
            Masked credential string
        """
        if not value or len(value) <= visible_chars * 2:
            return mask_char * len(value) if value else ""
        
        start = value[:visible_chars]
        end = value[-visible_chars:]
        middle_length = len(value) - (visible_chars * 2)
        middle = mask_char * middle_length
        
        return f"{start}{middle}{end}"
    
    @staticmethod
    def mask_dict_credentials(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively mask credential fields in a dictionary.
        
        Args:
            data: Dictionary that may contain credentials
            
        Returns:
            Dictionary with credentials masked
        """
        sensitive_fields = {
            'password', 'token', 'key', 'secret', 'credential', 
            'api_key', 'bearer_token', 'sasl_password', 'ssl_password'
        }
        
        masked_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                masked_data[key] = SecurityUtils.mask_dict_credentials(value)
            elif isinstance(value, str) and any(sensitive in key.lower() for sensitive in sensitive_fields):
                masked_data[key] = SecurityUtils.mask_credential(value)
            else:
                masked_data[key] = value
        
        return masked_data


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
    def validate_service_config(cls, values):
        """Validate that connection_config matches service_type."""
        if isinstance(values, dict):
            service_type = values.get('service_type', '').lower()
            connection_config = values.get('connection_config', {})
            
            # If connection_config is already a typed model, keep it
            if isinstance(connection_config, (ModelKafkaConnectionConfig, ModelDatabaseConnectionConfig, ModelRestApiConnectionConfig)):
                return values
            
            # Convert dict to appropriate typed model based on service_type
            if isinstance(connection_config, dict):
                if service_type in ['event_bus', 'kafka', 'message_queue']:
                    try:
                        values['connection_config'] = ModelKafkaConnectionConfig(**connection_config)
                    except Exception:
                        pass  # Keep as dict if validation fails
                elif service_type in ['database', 'db', 'postgresql', 'mysql']:
                    try:
                        values['connection_config'] = ModelDatabaseConnectionConfig(**connection_config)
                    except Exception:
                        pass
                elif service_type in ['rest_api', 'api', 'http', 'https']:
                    try:
                        values['connection_config'] = ModelRestApiConnectionConfig(**connection_config)
                    except Exception:
                        pass
        
        return values

    def get_masked_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive fields masked for logging."""
        config_dict = self.model_dump()
        
        # Mask the connection_config
        if isinstance(self.connection_config, dict):
            config_dict['connection_config'] = SecurityUtils.mask_dict_credentials(self.connection_config)
        else:
            # For typed models, convert to dict first then mask
            connection_dict = self.connection_config.model_dump() if hasattr(self.connection_config, 'model_dump') else {}
            config_dict['connection_config'] = SecurityUtils.mask_dict_credentials(connection_dict)
        
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

    def apply_environment_overrides(self) -> 'ModelExternalServiceConfig':
        """Apply environment variable overrides for CI/local testing."""
        # Apply overrides to connection_config if it supports them
        if hasattr(self.connection_config, 'apply_environment_overrides'):
            updated_connection_config = self.connection_config.apply_environment_overrides()
            
            # Create new instance with updated connection config
            current_data = self.model_dump()
            current_data['connection_config'] = updated_connection_config.model_dump()
            return ModelExternalServiceConfig(**current_data)
        
        return self


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