#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: 0.1
# name: validate_registry
# namespace: omninode.tools.validate_registry
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:58+00:00
# last_modified_at: 2025-04-27T18:12:58+00:00
# entrypoint: validate_registry.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Metadata ===

"""validate_registry.py
containers.foundation.src.foundation.script.validate.validate_registry.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import importlib
import pkgutil
from threading import RLock
from typing import Any, Dict, List, Optional, Type
import semver
import structlog
from foundation.util.util_file_output_writer import OutputWriter

from foundation.di.di_container import DIContainer
from foundation.protocol.protocol_validator_registry import ProtocolValidatorRegistry
from foundation.model.model_keyed import KeyedMetadataBlockModel
from foundation.model.model_metadata import MetadataBlockModel
from foundation.script.validate.validate_metadata_block_hash_registry import ValidateMetadataBlockHashRegistry
from foundation.registry.registry_metadata_block_hash import RegistryMetadataBlockHash


class ValidatorRegistry(ProtocolValidatorRegistry):
    """
    Registry for validator classes, following Foundation registry patterns.
    Implements ProtocolValidatorRegistry for interface consistency and static typing.
    """
    def __init__(self):
        self._validators = {}  # type: Dict[str, Dict[str, type]]
        self._metadata = {}    # type: Dict[str, Dict[str, dict]]
        self._language_registries = {}  # type: Dict[str, ProtocolValidatorRegistry]
        self._current_protocol_version = "0.1.0"  # Current protocol version

    def register(self, name: str, validator_cls: type, meta: dict) -> None:
        """Register a validator with its metadata."""
        if isinstance(meta, MetadataBlockModel):
            version = getattr(meta, "version", "v1")
        else:
            version = meta.get("version", "v1")
        if name not in self._validators:
            self._validators[name] = {}
            self._metadata[name] = {}
        self._validators[name][version] = validator_cls
        self._metadata[name][version] = meta

    def get_validator(self, name: str, version: Optional[str] = None) -> Optional[type]:
        """Get a validator by name and optional version. If version is None, returns latest version."""
        if name not in self._validators:
            return None
        if version is None:
            versions = list(self._validators[name].keys())
            if not versions:
                return None
            version = max(versions, key=self._parse_version)
        return self._validators[name].get(version)

    def list_validators(self) -> List[str]:
        """List all registered validator names."""
        return list(self._validators.keys())

    def get_all_metadata(self) -> KeyedMetadataBlockModel:
        """Get metadata for all validators as a KeyedMetadataBlockModel."""
        result = {}
        for name, versions in self._metadata.items():
            latest_version = max(versions.keys(), key=self._parse_version)
            meta = versions[latest_version]
            if isinstance(meta, MetadataBlockModel):
                result[name] = meta
            else:
                result[name] = MetadataBlockModel(**meta)
        return KeyedMetadataBlockModel(data=result)

    def register_language_registry(self, language: str, registry: ProtocolValidatorRegistry) -> None:
        """Register a language-specific registry."""
        self._language_registries[language] = registry

    def get_language_registry(self, language: str) -> Optional[ProtocolValidatorRegistry]:
        """Get a language-specific registry."""
        return self._language_registries.get(language)

    def get_validator_versions(self, name: str) -> List[str]:
        """Get all versions available for a validator."""
        if name not in self._validators:
            return []
        return sorted(self._validators[name].keys(), key=self._parse_version)

    def get_latest_version(self, name: str) -> Optional[str]:
        """Get the latest version of a validator."""
        versions = self.get_validator_versions(name)
        return versions[-1] if versions else None

    def check_version_compatibility(self, name: str, version: str) -> bool:
        """Check if a validator version is compatible with the current protocol version."""
        if name not in self._validators or version not in self._validators[name]:
            return False
        meta = self._metadata[name][version]
        if isinstance(meta, MetadataBlockModel):
            validator_protocol_version = getattr(meta, "protocol_version", "0.1.0")
        else:
            validator_protocol_version = meta.get("protocol_version", "0.1.0")
        return self._is_compatible_version(validator_protocol_version, self._current_protocol_version)

    def _parse_version(self, version: str) -> semver.VersionInfo:
        """Parse a version string into a semver.VersionInfo object."""
        # Remove 'v' prefix if present
        version = version.lstrip('v')
        return semver.VersionInfo.parse(version)

    def _is_compatible_version(self, version1: str, version2: str) -> bool:
        """Check if two versions are compatible (same major version)."""
        v1 = self._parse_version(version1)
        v2 = self._parse_version(version2)
        return v1.major == v2.major


# Create global instance
validate_registry = ValidatorRegistry()

# Register core validators
from foundation.script.validate.python.python_validate_registry import register_python_validators
register_python_validators()

# Register protocol compatibility validator
from foundation.script.validate.python.python_validate_protocol_compatibility import PythonValidateProtocolCompatibility
validate_registry.register(
    name="protocol_compatibility",
    validator_cls=PythonValidateProtocolCompatibility,
    meta=MetadataBlockModel(
        metadata_version="0.1",
        name="protocol_compatibility",
        namespace="omninode.tools.protocol_compatibility",
        version="1.0.0",
        entrypoint="python_validate_protocol_compatibility.py",
        protocols_supported=["O.N.E. v0.1"],
        author="OmniNode Team",
        owner="jonah@omninode.ai",
        copyright="Copyright (c) 2025 OmniNode.ai",
        created_at="2025-05-05T18:25:48+00:00",
        last_modified_at="2025-05-05T18:25:48+00:00",
        protocol_version="0.1.0",
        description="Validates that all registered validators are compatible with the current protocol version.",
        tags=["protocol", "compatibility", "python"],
        dependencies=[],
        config={}
    )
)


# === Fixture Registry ===
_fixture_registry = {}
_fixture_registry_lock = RLock()
_fixture_interface_registry = {}
_fixture_mode_registry = {}


def register_fixture(
    name: str,
    fixture: type,
    description: str = None,
    interface: type = None,
    mode: str = None,
):
    """Register a fixture class by name (and optionally by interface/mode)."""
    with _fixture_registry_lock:
        _fixture_registry[name] = fixture
        if interface is not None:
            _fixture_interface_registry[interface] = fixture
        if interface is not None and mode is not None:
            if interface not in _fixture_mode_registry:
                _fixture_mode_registry[interface] = {}
            _fixture_mode_registry[interface][mode] = fixture
        # Optionally store description if needed


def get_registered_fixture(name: str) -> type:
    """Return the registered fixture class by name, or raise KeyError if not found."""
    with _fixture_registry_lock:
        return _fixture_registry[name]


def get_fixture_by_interface(interface: type, mode: str = None) -> type:
    """Return the registered fixture class for the given interface and mode, or raise KeyError if not found."""
    with _fixture_registry_lock:
        if mode is not None:
            return _fixture_mode_registry[interface][mode]
        return _fixture_interface_registry[interface]


def get_registered_fixtures() -> Dict[str, type]:
    """Return a dict of all registered fixture classes by name."""
    with _fixture_registry_lock:
        return dict(_fixture_registry)


def register_validators_from_metadata(
    di_container: DIContainer,
    registry: ValidatorRegistry,
    validation_pkg: str = "foundation.script.validate",
):
    """
    Scan all modules in the validation package for validator classes with metadata stamps and register them with the DI container and registry.
    """
    for _, modname, ispkg in pkgutil.iter_modules(
        importlib.import_module(validation_pkg).__path__
    ):
        if ispkg:
            continue
        module = importlib.import_module(f"{validation_pkg}.{modname}")
        for attr in dir(module):
            obj = getattr(module, attr)
            if (
                isinstance(obj, type)
                and hasattr(obj, "metadata")
                and callable(getattr(obj, "metadata"))
            ):
                meta = obj.metadata()
                if isinstance(meta, MetadataBlockModel):
                    name = meta.name
                    version = getattr(meta, "version", "v1")
                else:
                    name = meta.get("name")
                    version = meta.get("version", "v1")
                registry.register(name, obj, meta)
                di_container.register(obj, obj)
    # Explicitly register PythonValidateChunk if not already registered
    try:
        from foundation.script.validate.python.python_validate_chunk import PythonValidateChunk
        di_container.register(PythonValidateChunk, lambda: PythonValidateChunk(config={}, logger=None))
    except ImportError:
        pass


def register_validators_with_di(di_container: DIContainer, registry: ValidatorRegistry):
    """
    Register all validators with the DI container and registry using metadata-driven registration.
    """
    register_validators_from_metadata(di_container, registry)


from foundation.script.validate.validate_directory_tree import ValidateDirectoryTree

ValidatorRegistry().register(
    name="directory_tree",
    validator_cls=ValidateDirectoryTree,
    meta={
        "name": "directory_tree",
        "version": "v1",
        "group": "structure",
        "description": "Validates directory tree structure against canonical paths and flexible directories.",
    },
)

validate_registry.register(
    name=ValidateMetadataBlockHashRegistry.metadata().name,
    validator_cls=lambda: ValidateMetadataBlockHashRegistry(RegistryMetadataBlockHash()),
    meta=ValidateMetadataBlockHashRegistry.metadata(),
)
