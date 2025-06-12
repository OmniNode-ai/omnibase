"""
ONEX Secret Management Models and Utilities.

Provides secure credential handling with Pydantic SecretStr, environment variable
integration, and .env file support for development workflows.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, SecretStr, field_validator
from enum import Enum
import logging

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available. .env file support disabled.")


class SecretBackendEnum(str, Enum):
    """Supported secret backend types."""
    ENVIRONMENT = "environment"
    DOTENV = "dotenv"
    VAULT = "vault"
    KUBERNETES = "kubernetes"
    FILE = "file"


class ModelSecretConfig(BaseModel):
    """Configuration for secret management backend."""
    backend: SecretBackendEnum = Field(
        default=SecretBackendEnum.ENVIRONMENT,
        description="Secret backend type"
    )
    dotenv_path: Optional[Path] = Field(
        default=None,
        description="Path to .env file for development"
    )
    vault_url: Optional[str] = Field(
        default=None,
        description="Vault server URL"
    )
    vault_token: Optional[SecretStr] = Field(
        default=None,
        description="Vault authentication token"
    )
    auto_load_dotenv: bool = Field(
        default=True,
        description="Automatically load .env file if present"
    )


class ModelSecureCredentials(BaseModel):
    """Base model for secure credential handling."""
    
    @classmethod
    def load_from_env(cls, env_prefix: str = "ONEX_") -> "ModelSecureCredentials":
        """Load credentials from environment variables with prefix."""
        raise NotImplementedError("Subclasses must implement load_from_env")
    
    def get_masked_dict(self) -> Dict[str, Any]:
        """Get dictionary representation with secrets masked."""
        data = self.model_dump()
        return self._mask_secrets_recursive(data)
    
    def _mask_secrets_recursive(self, data: Any) -> Any:
        """Recursively mask SecretStr fields in data structure."""
        if isinstance(data, dict):
            return {
                key: self._mask_secrets_recursive(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._mask_secrets_recursive(item) for item in data]
        elif isinstance(data, SecretStr):
            return "***MASKED***"
        else:
            return data


class ModelKafkaSecureConfig(ModelSecureCredentials):
    """Secure Kafka configuration with SecretStr for sensitive fields."""
    
    bootstrap_servers: str = Field(
        ...,
        description="Kafka bootstrap servers (comma-separated)",
        pattern=r"^[a-zA-Z0-9\-\.:,\s]+$",
        max_length=500
    )
    security_protocol: str = Field(
        default="PLAINTEXT",
        description="Security protocol",
        pattern=r"^(PLAINTEXT|SSL|SASL_PLAINTEXT|SASL_SSL)$"
    )
    sasl_username: Optional[str] = Field(
        default=None,
        description="SASL username",
        max_length=100
    )
    sasl_password: Optional[SecretStr] = Field(
        default=None,
        description="SASL password (secured)"
    )
    ssl_keyfile_path: Optional[str] = Field(
        default=None,
        description="Path to SSL key file",
        max_length=500
    )
    ssl_keyfile_password: Optional[SecretStr] = Field(
        default=None,
        description="SSL key file password (secured)"
    )
    ssl_certfile_path: Optional[str] = Field(
        default=None,
        description="Path to SSL certificate file",
        max_length=500
    )
    ssl_cafile_path: Optional[str] = Field(
        default=None,
        description="Path to SSL CA file",
        max_length=500
    )
    
    @classmethod
    def load_from_env(cls, env_prefix: str = "ONEX_KAFKA_") -> "ModelKafkaSecureConfig":
        """Load Kafka config from environment variables."""
        return cls(
            bootstrap_servers=os.getenv(f"{env_prefix}BOOTSTRAP_SERVERS", "localhost:9092"),
            security_protocol=os.getenv(f"{env_prefix}SECURITY_PROTOCOL", "PLAINTEXT"),
            sasl_username=os.getenv(f"{env_prefix}SASL_USERNAME"),
            sasl_password=SecretStr(os.getenv(f"{env_prefix}SASL_PASSWORD")) if os.getenv(f"{env_prefix}SASL_PASSWORD") else None,
            ssl_keyfile_path=os.getenv(f"{env_prefix}SSL_KEYFILE_PATH"),
            ssl_keyfile_password=SecretStr(os.getenv(f"{env_prefix}SSL_KEYFILE_PASSWORD")) if os.getenv(f"{env_prefix}SSL_KEYFILE_PASSWORD") else None,
            ssl_certfile_path=os.getenv(f"{env_prefix}SSL_CERTFILE_PATH"),
            ssl_cafile_path=os.getenv(f"{env_prefix}SSL_CAFILE_PATH"),
        )


class ModelDatabaseSecureConfig(ModelSecureCredentials):
    """Secure database configuration with SecretStr for sensitive fields."""
    
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
        default=False,
        description="Whether to use SSL connection"
    )
    ssl_cert_path: Optional[str] = Field(
        default=None,
        description="Path to SSL certificate",
        max_length=500
    )
    ssl_key_path: Optional[str] = Field(
        default=None,
        description="Path to SSL key file",
        max_length=500
    )
    ssl_key_password: Optional[SecretStr] = Field(
        default=None,
        description="SSL key password (secured)"
    )
    
    @classmethod
    def load_from_env(cls, env_prefix: str = "ONEX_DB_") -> "ModelDatabaseSecureConfig":
        """Load database config from environment variables."""
        password = os.getenv(f"{env_prefix}PASSWORD")
        if not password:
            raise ValueError(f"Database password required: {env_prefix}PASSWORD")
        
        ssl_key_password = os.getenv(f"{env_prefix}SSL_KEY_PASSWORD")
        
        return cls(
            host=os.getenv(f"{env_prefix}HOST", "localhost"),
            port=int(os.getenv(f"{env_prefix}PORT", "5432")),
            database=os.getenv(f"{env_prefix}DATABASE", "onex_dev"),
            username=os.getenv(f"{env_prefix}USERNAME", "onex_user"),
            password=SecretStr(password),
            ssl_enabled=os.getenv(f"{env_prefix}SSL_ENABLED", "false").lower() == "true",
            ssl_cert_path=os.getenv(f"{env_prefix}SSL_CERT_PATH"),
            ssl_key_path=os.getenv(f"{env_prefix}SSL_KEY_PATH"),
            ssl_key_password=SecretStr(ssl_key_password) if ssl_key_password else None,
        )


class SecretManager:
    """Centralized secret management for ONEX."""
    
    def __init__(self, config: ModelSecretConfig):
        self.config = config
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file if configured."""
        if not self.config.auto_load_dotenv or not DOTENV_AVAILABLE:
            return
        
        # Look for .env file in current directory or specified path
        env_path = self.config.dotenv_path or Path(".env")
        
        if env_path.exists():
            load_dotenv(env_path)
            logging.info(f"Loaded environment variables from {env_path}")
        else:
            # Try common locations
            for common_path in [Path(".env"), Path(".env.local"), Path("config/.env")]:
                if common_path.exists():
                    load_dotenv(common_path)
                    logging.info(f"Loaded environment variables from {common_path}")
                    break
    
    def get_kafka_config(self) -> ModelKafkaSecureConfig:
        """Get secure Kafka configuration."""
        return ModelKafkaSecureConfig.load_from_env()
    
    def get_database_config(self) -> ModelDatabaseSecureConfig:
        """Get secure database configuration."""
        return ModelDatabaseSecureConfig.load_from_env()
    
    def mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in dictionary for logging."""
        sensitive_keys = {
            'password', 'token', 'key', 'secret', 'credential',
            'api_key', 'bearer_token', 'sasl_password', 'ssl_password',
            'ssl_key_password', 'private_key'
        }
        
        masked_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                masked_data[key] = self.mask_sensitive_data(value)
            elif isinstance(value, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
                masked_data[key] = "***MASKED***"
            else:
                masked_data[key] = value
        
        return masked_data


# Global secret manager instance
_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """Get global secret manager instance."""
    global _secret_manager
    if _secret_manager is None:
        config = ModelSecretConfig()
        _secret_manager = SecretManager(config)
    return _secret_manager


def init_secret_manager(config: ModelSecretConfig) -> SecretManager:
    """Initialize global secret manager with custom config."""
    global _secret_manager
    _secret_manager = SecretManager(config)
    return _secret_manager 