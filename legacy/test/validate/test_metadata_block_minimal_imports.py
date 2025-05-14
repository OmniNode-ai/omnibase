# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_metadata_block_minimal_imports"
# namespace: "omninode.tools.test_metadata_block_minimal_imports"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:14+00:00"
# last_modified_at: "2025-05-05T13:00:14+00:00"
# entrypoint: "test_metadata_block_minimal_imports.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

def test_metadata_block_minimal_imports():
    # Import and minimally exercise each metadata-related module
    import foundation.model.model_metadata as mm
    import foundation.script.metadata.metadata_stamper as ms
    import foundation.script.metadata.metadata_block_utils as mbu
    import foundation.util.util_metadata_block_extractor as mbe
    import foundation.util.util_metadata_block_extractor_registry as mber
    import foundation.template.metadata.metadata_template_blocks as mtb
    import foundation.template.metadata.metadata_template_registry as mtr
    import foundation.script.validate.validate_metadata_block_registry as vbr
    import foundation.script.validate.python.python_validate_metadata_block as pvmb
    import foundation.script.validate.yaml.yaml_validate_metadata_block as yvmb
    import foundation.script.validate.markdown.markdown_validate_metadata_block as mvmb

    # Exercise at least one symbol from each module
    assert hasattr(mm, "MetadataBlockModel")
    assert hasattr(ms, "MetadataStamper")
    assert hasattr(mbu, "extract_metadata_block")
    assert hasattr(mbe, "MetadataBlockExtractor")
    assert hasattr(mber, "get_extractor")
    assert hasattr(mtb, "MINIMAL_METADATA")
    assert hasattr(mtr, "MetadataTemplateRegistry")
    assert hasattr(mtr, "MetadataRegistryTemplate")
    assert hasattr(vbr, "MetadataValidateBlockRegistry")
    assert hasattr(pvmb, "PythonValidateMetadataBlock")
    assert hasattr(yvmb, "YamlValidateMetadataBlock")
    assert hasattr(mvmb, "MarkdownValidateMetadataBlock") 