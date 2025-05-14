#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_docker_compose
# namespace: omninode.tools.validate_docker_compose
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:03+00:00
# last_modified_at: 2025-04-27T18:13:03+00:00
# entrypoint: validate_docker_compose.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_docker_compose.py containers.foundation.src.foundation.script.vali
dation.validate_docker_compose.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from foundation.protocol.protocol_validate import ProtocolValidate

def load_template() -> Dict:
    templates_dir = Path(__file__).parent.parent.parent / "templates"
    template_path = templates_dir / "DOCKER_COMPOSE_SERVICE_TEMPLATE.yml"
    with open(template_path) as f:
        return yaml.safe_load(f)


def check_service_config(service_name: str, config: Dict, template: Dict) -> List[str]:
    """Check if a service configuration follows the template standards."""
    errors = []

    # Required top-level keys
    required_keys = {"build", "environment", "volumes", "healthcheck"}

    # Check required keys
    for key in required_keys:
        if key not in config:
            errors.append(f"Service '{service_name}' is missing required key: {key}")

    # Check environment variables
    if "environment" in config:
        env_vars = set()
        for env in config["environment"]:
            if isinstance(env, str):
                env_vars.add(env.split("=")[0])
            elif isinstance(env, dict):
                env_vars.update(env.keys())

        required_env_vars = {"PYTHONPATH", "ENV"}

        for var in required_env_vars:
            if var not in env_vars:
                errors.append(
                    f"Service '{service_name}' is missing required environment variable: {var}"
                )

    # Check build configuration
    if "build" in config:
        if "context" not in config["build"]:
            errors.append(f"Service '{service_name}' build is missing context")
        if "dockerfile" not in config["build"]:
            errors.append(f"Service '{service_name}' build is missing dockerfile path")

    # Check volumes
    if "volumes" in config:
        source_mounted = False
        for volume in config["volumes"]:
            if "/app" in volume:
                source_mounted = True
                break
        if not source_mounted:
            errors.append(f"Service '{service_name}' must mount source code to /app")

    # Check healthcheck
    if "healthcheck" in config:
        required_health_keys = {"test", "interval", "timeout", "retries"}
        health_config = config["healthcheck"]

        for key in required_health_keys:
            if key not in health_config:
                errors.append(f"Service '{service_name}' healthcheck is missing: {key}")

    return errors


def check_networks(compose_config: Dict) -> List[str]:
    """Check if required networks are defined."""
    errors = []

    if "networks" not in compose_config:
        errors.append("Missing top-level networks configuration")
        return errors

    required_networks = {"platform-net"}
    defined_networks = set(compose_config["networks"].keys())

    for network in required_networks:
        if network not in defined_networks:
            errors.append(f"Missing required network: {network}")

    return errors


def check_dependencies(compose_config: Dict) -> List[str]:
    """Check if service dependencies are properly configured."""
    errors = []

    for service_name, config in compose_config.get("services", {}).items():
        if "depends_on" in config:
            deps = config["depends_on"]
            if isinstance(deps, dict):
                for dep, dep_config in deps.items():
                    if "condition" not in dep_config:
                        errors.append(
                            f"Service '{service_name}' dependency on '{dep}' should specify a condition"
                        )
            elif isinstance(deps, list):
                errors.append(
                    f"Service '{service_name}' should use healthcheck conditions in depends_on"
                )

    return errors


def main() -> int:
    """Main function to check Docker Compose configuration."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    try:
        template = load_template()
        compose_path = Path("docker-compose.yml")

        if not compose_path.is_file():
            logger.error("Error: docker-compose.yml not found")
            return 1

        with open(compose_path) as f:
            compose_config = yaml.safe_load(f)

        if not compose_config or "services" not in compose_config:
            logger.error("Error: Invalid docker-compose.yml format")
            return 1

        exit_code = 0

        # Check networks
        network_errors = check_networks(compose_config)
        if network_errors:
            logger.error("\nNetwork configuration errors:")
            for error in network_errors:
                logger.error(f"  - {error}")
            exit_code = 1

        # Check dependencies
        dependency_errors = check_dependencies(compose_config)
        if dependency_errors:
            logger.error("\nDependency configuration errors:")
            for error in dependency_errors:
                logger.error(f"  - {error}")
            exit_code = 1

        # Check each service
        for service_name, config in compose_config["services"].items():
            service_errors = check_service_config(service_name, config, template)
            if service_errors:
                logger.error(f"\nErrors in service '{service_name}':")
                for error in service_errors:
                    logger.error(f"  - {error}")
                exit_code = 1

        return exit_code

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


    name="docker_compose",
    version="v1",
    group="container",
    description="Validates docker-compose.yml for platform compliance.",
)
class DockerComposeValidator(ProtocolValidate):
    def get_name(self) -> str:
        return "docker_compose"

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="docker_compose",
            group="container",
            description="Validates docker-compose.yml for platform compliance.",
            version="v1",
        )

    def validate(self, target: Path, config: Optional[dict] = None):
        # This is a stub: in practice, you would call the main() logic and parse results
        # For now, just return a dummy result for registry completeness
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=[str(e) for e in self.errors],
            warnings=[str(w) for w in self.warnings],
            version="v1",
        )

    def _validate(self, *args, **kwargs):
        # Satisfy abstract method requirement
        return self.validate(*args, **kwargs)
