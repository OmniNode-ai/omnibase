from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.script.validate.python.python_validate_container import ContainerValidator
from foundation.script.validate.validate_registry import register_fixture
from foundation.fixture import BaseTestFixture

class ContainerValidatorFixture(BaseTestFixture, ProtocolValidateFixture):
    def get_fixture(self):
        # Loosen naming_pattern for test compatibility
        config = {
            "rules": {
                "required_files": ["Dockerfile", "README.md"],
                "naming_pattern": r".*",  # Allow any directory name for tests
                "max_dockerfile_size": 15,
                "init_py_rules": {
                    "required_patterns": ["*"],
                    "ignore_patterns": ["migrations*"]
                },
            }
        }
        return ContainerValidator(config=config)

register_fixture(
    name="container_validator_fixture",
    fixture=ContainerValidatorFixture,
    description="DI/registry-compliant fixture for ContainerValidator",
    interface=ProtocolValidateFixture,
) 