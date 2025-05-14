"""
foundation.bootstrap.bootstrap

Canonical bootstrap module for unified DI container setup and registry population.
All top-level scripts (validators, tools, fixtures, templates) must import and call bootstrap() for consistent initialization.
"""

from foundation.script.tool.tool_registry import ToolRegistry
from foundation.registry.base_registry import BaseRegistry
from foundation.registry.cli_registry import BaseRegistry as CliRegistry
from foundation.registry.utility_registry import BaseRegistry as UtilityRegistry
from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.script.validate.validate_metadata_block_registry import MetadataValidateBlockRegistry
from foundation.model.model_metadata import MetadataBlockModel

def initialize_di():
    """Register core DI bindings (logger, config, utility registry, etc.)."""
    # Example: DI container pattern (replace with actual DI framework if present)
    global di_container
    di_container = {}
    di_container['tool_registry'] = ToolRegistry()
    di_container['utility_registry'] = UtilityRegistry()
    di_container['cli_registry'] = CliRegistry()
    di_container['template_registry'] = MetadataRegistryTemplate()
    di_container['metadata_validate_block_registry'] = MetadataValidateBlockRegistry()

def populate_registry():
    """Register all known tools, validators, fixtures, templates."""
    # Example: populate registries after instantiation
    # Tool registrations
    from foundation.script.metadata.metadata_stamper import MetadataStamper
    di_container['tool_registry'].register(
        name="metadata_stamper",
        tool_cls=MetadataStamper,
        meta={
            "name": "metadata_stamper",
            "version": "0.1.0",
            "description": "OmniNode Metadata Stamper Tool (inserts/repairs metadata blocks in source files)",
            "entrypoint": "foundation.script.metadata.metadata_stamper",
            "type": "tool",
            "namespace": "omninode.tools.metadata_stamper",
            "protocols_supported": ["O.N.E. v0.1"],
            "author": "OmniNode Team",
            "owner": "jonah@omninode.ai",
        },
    )
    # Add other tool/validator/template registrations as needed

def bootstrap():
    """Run DI and registry initialization. Idempotent."""
    initialize_di()
    populate_registry()

def health_check():
    """Verify registry/DI readiness."""
    # TODO: Implement health check logic
    return True

if __name__ == "__main__":
    # Basic test: import and call bootstrap
    try:
        bootstrap()
        print("[bootstrap] Success: bootstrap() ran without error.")
    except Exception as e:
        print(f"[bootstrap] ERROR: {e}") 