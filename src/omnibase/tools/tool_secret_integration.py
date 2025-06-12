"""
ONEX Secret Management Integration Tool.

Provides utilities for migrating existing components to use secure secret management,
validating secret configurations, and integrating with ONEX service management.
"""

from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import logging
from pydantic import BaseModel, Field, SecretStr

from omnibase.model.model_secret_management import (
    SecretManager, 
    ModelSecretConfig, 
    ModelKafkaSecureConfig,
    ModelDatabaseSecureConfig,
    get_secret_manager
)
from omnibase.model.model_external_service_config import (
    ModelExternalServiceConfig,
    ModelKafkaConnectionConfig,
    ModelDatabaseConnectionConfig
)


class ModelSecretMigrationResult(BaseModel):
    """Result of secret migration operation."""
    success: bool = Field(..., description="Whether migration was successful")
    migrated_services: List[str] = Field(default_factory=list, description="List of services migrated")
    errors: List[str] = Field(default_factory=list, description="List of migration errors")
    warnings: List[str] = Field(default_factory=list, description="List of migration warnings")
    secure_fields_count: int = Field(default=0, description="Number of fields secured with SecretStr")


class ModelSecretValidationResult(BaseModel):
    """Result of secret validation operation."""
    valid: bool = Field(..., description="Whether all secrets are valid")
    missing_secrets: List[str] = Field(default_factory=list, description="List of missing required secrets")
    insecure_fields: List[str] = Field(default_factory=list, description="List of fields that should use SecretStr")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")


class ToolSecretIntegration:
    """Tool for integrating secure secret management with ONEX components."""
    
    def __init__(self, secret_manager: Optional[SecretManager] = None):
        self.secret_manager = secret_manager or get_secret_manager()
        self.logger = logging.getLogger(__name__)
    
    def migrate_external_service_config(
        self, 
        config: ModelExternalServiceConfig
    ) -> ModelSecretMigrationResult:
        """
        Migrate an external service config to use secure secret management.
        
        Args:
            config: External service configuration to migrate
            
        Returns:
            Migration result with success status and details
        """
        result = ModelSecretMigrationResult(success=True)
        
        try:
            if config.service_type == "event_bus" and isinstance(config.connection_config, ModelKafkaConnectionConfig):
                # Migrate Kafka configuration
                secure_config = self._migrate_kafka_config(config.connection_config)
                if secure_config:
                    result.migrated_services.append("kafka")
                    result.secure_fields_count += self._count_secure_fields(secure_config)
                    
            elif config.service_type == "database" and isinstance(config.connection_config, ModelDatabaseConnectionConfig):
                # Migrate database configuration
                secure_config = self._migrate_database_config(config.connection_config)
                if secure_config:
                    result.migrated_services.append("database")
                    result.secure_fields_count += self._count_secure_fields(secure_config)
            
            else:
                result.warnings.append(f"Unknown service type for migration: {config.service_type}")
                
        except Exception as e:
            result.success = False
            result.errors.append(f"Migration failed: {str(e)}")
            self.logger.error(f"Secret migration failed: {e}")
        
        return result
    
    def _migrate_kafka_config(self, config: ModelKafkaConnectionConfig) -> Optional[ModelKafkaSecureConfig]:
        """Migrate Kafka config to secure version."""
        try:
            # Convert plain text credentials to SecretStr
            sasl_password = None
            if hasattr(config, 'sasl_password') and config.sasl_password:
                if isinstance(config.sasl_password, str):
                    sasl_password = SecretStr(config.sasl_password)
                else:
                    sasl_password = config.sasl_password
            
            return ModelKafkaSecureConfig(
                bootstrap_servers=config.bootstrap_servers,
                security_protocol=getattr(config, 'security_protocol', 'PLAINTEXT'),
                sasl_username=getattr(config, 'sasl_username', None),
                sasl_password=sasl_password,
                ssl_keyfile_path=getattr(config, 'ssl_keyfile', None),
                ssl_certfile_path=getattr(config, 'ssl_certfile', None),
                ssl_cafile_path=getattr(config, 'ssl_cafile', None),
            )
        except Exception as e:
            self.logger.error(f"Failed to migrate Kafka config: {e}")
            return None
    
    def _migrate_database_config(self, config: ModelDatabaseConnectionConfig) -> Optional[ModelDatabaseSecureConfig]:
        """Migrate database config to secure version."""
        try:
            # Convert plain text password to SecretStr
            password = config.password
            if isinstance(password, str):
                password = SecretStr(password)
            
            return ModelDatabaseSecureConfig(
                host=config.host,
                port=config.port,
                database=config.database,
                username=config.username,
                password=password,
                ssl_enabled=getattr(config, 'ssl_enabled', False),
            )
        except Exception as e:
            self.logger.error(f"Failed to migrate database config: {e}")
            return None
    
    def _count_secure_fields(self, config: Any) -> int:
        """Count the number of SecretStr fields in a configuration."""
        count = 0
        if hasattr(config, '__dict__'):
            for value in config.__dict__.values():
                if isinstance(value, SecretStr):
                    count += 1
        return count
    
    def validate_secret_configuration(
        self, 
        config_dict: Dict[str, Any]
    ) -> ModelSecretValidationResult:
        """
        Validate a configuration dictionary for proper secret handling.
        
        Args:
            config_dict: Configuration dictionary to validate
            
        Returns:
            Validation result with recommendations
        """
        result = ModelSecretValidationResult(valid=True)
        
        # Define sensitive field patterns
        sensitive_patterns = {
            'password', 'token', 'key', 'secret', 'credential',
            'api_key', 'bearer_token', 'sasl_password', 'ssl_password',
            'private_key', 'cert_key', 'auth_token'
        }
        
        def check_recursive(data: Any, path: str = ""):
            """Recursively check for insecure credential storage."""
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Check if this looks like a sensitive field
                    if any(pattern in key.lower() for pattern in sensitive_patterns):
                        if isinstance(value, str) and value:
                            # Found plain text credential
                            result.insecure_fields.append(current_path)
                            result.valid = False
                        elif value is None:
                            # Missing required credential
                            result.missing_secrets.append(current_path)
                    
                    # Recurse into nested structures
                    if isinstance(value, (dict, list)):
                        check_recursive(value, current_path)
                        
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_recursive(item, f"{path}[{i}]")
        
        check_recursive(config_dict)
        
        # Generate recommendations
        if result.insecure_fields:
            result.recommendations.append(
                f"Convert {len(result.insecure_fields)} plain text credential fields to use Pydantic SecretStr"
            )
        
        if result.missing_secrets:
            result.recommendations.append(
                f"Provide values for {len(result.missing_secrets)} missing credential fields"
            )
        
        if result.valid:
            result.recommendations.append("Configuration follows secure credential handling best practices")
        
        return result
    
    def generate_env_template(
        self, 
        services: List[str],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate a .env template for the specified services.
        
        Args:
            services: List of service names to include
            output_path: Optional path to write the template file
            
        Returns:
            Generated .env template content
        """
        template_lines = [
            "# ONEX Environment Configuration",
            "# Generated template for secure credential management",
            "# Copy this file to .env and fill in your values",
            "# DO NOT commit .env files to version control",
            "",
        ]
        
        if "kafka" in services:
            template_lines.extend([
                "# === Kafka Configuration ===",
                "ONEX_KAFKA_BOOTSTRAP_SERVERS=localhost:9092",
                "ONEX_KAFKA_SECURITY_PROTOCOL=PLAINTEXT",
                "# ONEX_KAFKA_SASL_USERNAME=your_username",
                "# ONEX_KAFKA_SASL_PASSWORD=your_password",
                "# ONEX_KAFKA_SSL_KEYFILE_PATH=/path/to/client.key",
                "# ONEX_KAFKA_SSL_KEYFILE_PASSWORD=your_key_password",
                "# ONEX_KAFKA_SSL_CERTFILE_PATH=/path/to/client.crt",
                "# ONEX_KAFKA_SSL_CAFILE_PATH=/path/to/ca.crt",
                "",
            ])
        
        if "database" in services:
            template_lines.extend([
                "# === Database Configuration ===",
                "ONEX_DB_HOST=localhost",
                "ONEX_DB_PORT=5432",
                "ONEX_DB_DATABASE=onex_dev",
                "ONEX_DB_USERNAME=onex_user",
                "ONEX_DB_PASSWORD=your_secure_password",
                "ONEX_DB_SSL_ENABLED=false",
                "# ONEX_DB_SSL_CERT_PATH=/path/to/client.crt",
                "# ONEX_DB_SSL_KEY_PATH=/path/to/client.key",
                "# ONEX_DB_SSL_KEY_PASSWORD=your_ssl_key_password",
                "",
            ])
        
        if "api" in services:
            template_lines.extend([
                "# === API Configuration ===",
                "# ONEX_API_KEY=your_api_key",
                "# ONEX_API_BASE_URL=https://api.example.com",
                "# ONEX_API_BEARER_TOKEN=your_bearer_token",
                "",
            ])
        
        # Add common ONEX settings
        template_lines.extend([
            "# === ONEX System Configuration ===",
            "ONEX_LOG_LEVEL=debug",
            "ONEX_EVENT_BUS_TYPE=kafka",
            "ONEX_TRACE=1",
            "",
        ])
        
        template_content = "\n".join(template_lines)
        
        if output_path:
            output_path.write_text(template_content)
            self.logger.info(f"Generated .env template at {output_path}")
        
        return template_content
    
    def audit_service_security(
        self, 
        service_configs: List[ModelExternalServiceConfig]
    ) -> Dict[str, ModelSecretValidationResult]:
        """
        Audit multiple service configurations for security compliance.
        
        Args:
            service_configs: List of service configurations to audit
            
        Returns:
            Dictionary mapping service names to validation results
        """
        audit_results = {}
        
        for config in service_configs:
            # Convert to dict for validation
            config_dict = config.model_dump()
            
            # Validate the configuration
            validation_result = self.validate_secret_configuration(config_dict)
            audit_results[config.service_name] = validation_result
            
            self.logger.info(
                f"Audited service '{config.service_name}': "
                f"{'SECURE' if validation_result.valid else 'INSECURE'}"
            )
        
        return audit_results
    
    def get_masked_config_for_logging(
        self, 
        config: Union[ModelKafkaSecureConfig, ModelDatabaseSecureConfig, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get a masked version of configuration safe for logging.
        
        Args:
            config: Configuration to mask
            
        Returns:
            Masked configuration dictionary
        """
        if hasattr(config, 'get_masked_dict'):
            return config.get_masked_dict()
        elif isinstance(config, dict):
            return self.secret_manager.mask_sensitive_data(config)
        else:
            # Convert to dict and mask
            config_dict = config.model_dump() if hasattr(config, 'model_dump') else dict(config)
            return self.secret_manager.mask_sensitive_data(config_dict) 