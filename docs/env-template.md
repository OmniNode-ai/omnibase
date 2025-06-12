# ONEX Environment Configuration Template

Copy the content below to a `.env` file in your project root for development.

**⚠️ SECURITY WARNING:** Never commit `.env` files to version control!

```bash
# ONEX Development Environment Configuration
# Copy this content to .env and fill in your values
# DO NOT commit .env files to version control

# === Event Bus Configuration ===
ONEX_EVENT_BUS_TYPE=kafka
ONEX_KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ONEX_KAFKA_SECURITY_PROTOCOL=PLAINTEXT
ONEX_KAFKA_TOPICS=onex-default
ONEX_KAFKA_GROUP_ID=onex-dev-group

# Kafka Authentication (for production)
# ONEX_KAFKA_SASL_USERNAME=your_username
# ONEX_KAFKA_SASL_PASSWORD=your_password
# ONEX_KAFKA_SSL_KEYFILE_PATH=/path/to/client.key
# ONEX_KAFKA_SSL_KEYFILE_PASSWORD=your_key_password
# ONEX_KAFKA_SSL_CERTFILE_PATH=/path/to/client.crt
# ONEX_KAFKA_SSL_CAFILE_PATH=/path/to/ca.crt

# === Database Configuration ===
ONEX_DB_HOST=localhost
ONEX_DB_PORT=5432
ONEX_DB_DATABASE=onex_dev
ONEX_DB_USERNAME=onex_user
ONEX_DB_PASSWORD=onex_dev_password
ONEX_DB_SSL_ENABLED=false

# Database SSL (for production)
# ONEX_DB_SSL_CERT_PATH=/path/to/client.crt
# ONEX_DB_SSL_KEY_PATH=/path/to/client.key
# ONEX_DB_SSL_KEY_PASSWORD=your_ssl_key_password

# === API Configuration ===
# ONEX_API_KEY=your_api_key
# ONEX_API_BASE_URL=https://api.example.com
# ONEX_API_BEARER_TOKEN=your_bearer_token

# === Logging Configuration ===
ONEX_LOG_LEVEL=debug
ONEX_LOG_FORMAT=json
ONEX_ENABLE_CORRELATION_IDS=true
ONEX_INCLUDE_CALLER_INFO=true
ONEX_INCLUDE_TIMESTAMPS=true
ONEX_LOG_TARGETS=stdout

# === Development Settings ===
ONEX_TRACE=1
ONEX_CORRELATION_ID=dev-correlation-id

# === Service Management ===
ONEX_SERVICE_TIMEOUT=300
ONEX_SERVICE_HEALTH_CHECK_INTERVAL=30

# === Security Settings ===
ONEX_SECRET_BACKEND=dotenv
ONEX_VAULT_URL=https://vault.example.com
# ONEX_VAULT_TOKEN=your_vault_token

# === Node-Specific Settings ===
ONEX_SCENARIO_PATH=./scenarios
STAMPER_FIXTURE_PATH=./fixtures
STAMPER_FIXTURE_FORMAT=json

# === Namespace Configuration ===
OMNINODE_NAMESPACE_PREFIX=omnibase
```

## Usage

1. **Copy template to .env:**
   ```bash
   cp docs/env-template.md .env
   # Edit the .env file and remove the markdown formatting
   ```

2. **Install python-dotenv:**
   ```bash
   poetry add python-dotenv
   ```

3. **Use in your code:**
   ```python
   from omnibase.model.model_secret_management import get_secret_manager
   
   # Automatically loads .env file
   secret_manager = get_secret_manager()
   kafka_config = secret_manager.get_kafka_config()
   ```

## Security Best Practices

- **Development:** Use `.env` files for local development
- **CI/CD:** Use environment variables or secret injection
- **Production:** Use HashiCorp Vault, Kubernetes secrets, or cloud secret managers
- **Never:** Commit secrets to version control 