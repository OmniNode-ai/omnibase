# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# schema_version: 1.0.0
# name: python_validate_file_filters
# namespace: omninode.tools.python_validate_file_filters
# meta_type: model
# version: 0.1.0
# author: OmniNode Team
# owner: jonah@omninode.ai
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-05-03T22:59:58+00:00
# last_modified_at: 2025-05-03T22:59:58+00:00
# entrypoint: python_validate_file_filters.py
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

VALIDATOR_FILE_FILTERS = {
    # Python validators
    "absolute_imports": lambda f: f.endswith(".py"),
    "env_secrets": lambda f: f.endswith(
        (
            ".py",
            ".env",
            ".yaml",
            ".yml",
            ".json",
            ".toml",
            ".ini",
            ".conf",
            ".sh",
            ".bash",
            ".zsh",
            "Dockerfile",
            "docker-compose.yml",
        )
    ),
    "security": lambda f: f.endswith(".py"),
    "code_quality": lambda f: f.endswith(".py"),
    "test_coverage": lambda f: f.endswith(".py"),
    "logger_extra": lambda f: f.endswith(".py"),
    "style": lambda f: f.endswith(".py"),
    # YAML/metadata validators
    "metadata_block": lambda f: f.endswith((".yaml", ".yml")),
    "profile_schema": lambda f: f.endswith((".yaml", ".yml")),
    "container_yaml": lambda f: f.endswith(("container.yaml", "container.yml")),
    "registry_consistency": lambda f: f.endswith((".yaml", ".yml")),
    # Docker/compose validators
    "dockerfile": lambda f: f.endswith("Dockerfile"),
    "compose": lambda f: f.endswith(("docker-compose.yml", "docker-compose.yaml")),
    # Add more as needed
}