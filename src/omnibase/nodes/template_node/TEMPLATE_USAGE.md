<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: TEMPLATE_USAGE.md
version: 1.0.0
uuid: 60fa966d-de4d-4893-808f-148d3f18fcad
author: OmniNode Team
created_at: 2025-05-24T09:38:58.931285
last_modified_at: 2025-05-24T13:39:57.886038
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 01c669a998fbc08369df2fe16436d8c21bb402668018d693c739adf07cf3e634
entrypoint: python@TEMPLATE_USAGE.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.TEMPLATE_USAGE
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Template Node Usage Guide

This guide explains how to use the `template_node` to create new ONEX nodes with proper structure and conventions.

## Quick Start

1. **Copy the template**:
   ```bash
   cp -r src/omnibase/nodes/template_node src/omnibase/nodes/your_node_name
   ```

2. **Run the replacement script** (see below for manual steps):
   ```bash
   # TODO: Create a script to automate template replacement
   # ./scripts/create_node_from_template.sh your_node_name "Your Node Description"
   ```

## Manual Replacement Steps

### 0. Remove Template Ignore File

**IMPORTANT: Delete the `.onexignore` file first!**

```bash
# Navigate to your new node directory
cd src/omnibase/nodes/your_node_name/v1_0_0

# Delete the template .onexignore file
rm .onexignore
```

**Why this step is critical:**
- The template contains a `.onexignore` file that prevents stamping/validation of template files
- This file ignores all template files with placeholder values and validation errors
- Keeping it would hide validation issues in your real node implementation
- Deleting it forces you to fix all template placeholders and validation errors

**What the .onexignore file was hiding:**
- Template placeholders (TEMPLATE-UUID-REPLACE-ME, TEMPLATE_AUTHOR, etc.)
- Invalid lifecycle states ("template")
- Pydantic Field usage issues
- Template validation errors that are intentional

### 1. Directory and File Renaming

```bash
# Navigate to your new node directory
cd src/omnibase/nodes/your_node_name/v1_0_0

# Rename the contract file
mv template_node_contract.yaml your_node_name_contract.yaml
```

### 2. Metadata Replacement

Replace all template placeholders in the following files:

#### In `node.onex.yaml`:
- `name: "template_node"` → `name: "your_node_name"`
- `uuid: "TEMPLATE-UUID-REPLACE-ME"` → Generate new UUID
- `author: "TEMPLATE_AUTHOR"` → Your name/organization
- `created_at: TEMPLATE_CREATED_AT` → Current timestamp
- `last_modified_at: TEMPLATE_LAST_MODIFIED_AT` → Current timestamp
- `description: "TEMPLATE: Replace with your node description"` → Your description
- `state_contract: "state_contract://template_node_contract.yaml"` → `state_contract://your_node_name_contract.yaml"`
- `lifecycle: "template"` → `"draft"` (or appropriate lifecycle)
- `hash: "TEMPLATE_HASH_TO_BE_COMPUTED"` → Will be computed by stamper
- `namespace: "omnibase.nodes.template_node"` → `"omnibase.nodes.your_node_name"`
- `tags: ["template", "REPLACE_WITH_YOUR_TAGS"]` → Your relevant tags

#### In `your_node_name_contract.yaml`:
- Update all `TEMPLATE_*` placeholders
- Define your actual input/output state schema
- Update examples to match your use case

#### In all Python files:
- Replace all metadata blocks with your information
- Update UUIDs, timestamps, descriptions, namespaces

### 3. Code Replacement

#### In `models/state.py`:
- `TemplateInputState` → `YourNodeInputState`
- `TemplateOutputState` → `YourNodeOutputState`
- `template_required_field` → Your actual field names
- `template_optional_field` → Your actual field names
- Update field types, descriptions, and validation

#### In `node.py`:
- `run_template_node` → `run_your_node_name`
- `TemplateInputState` → `YourNodeInputState`
- `TemplateOutputState` → `YourNodeOutputState`
- `node_id = "template_node"` → `node_id = "your_node_name"`
- Replace the template logic with your actual implementation
- Update CLI argument parser
- Update function docstrings

#### In `src/main.py`:
- Update imports to match your renamed functions and classes
- Update `__all__` exports

#### In `node_tests/test_template.py`:
- Rename file to `test_your_node_name.py`
- `run_template_node` → `run_your_node_name`
- `TemplateInputState` → `YourNodeInputState`
- `TemplateOutputState` → `YourNodeOutputState`
- Update test cases to match your node's functionality
- Update assertions to match your expected behavior

### 4. Documentation Updates

#### In `README.md`:
- Replace all template content with your node's documentation
- Update usage examples
- Update input/output tables
- Update file structure if different

#### In `TEMPLATE_USAGE.md`:
- Delete this file (it's only for the template)

## Field Replacement Reference

### Common Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `TEMPLATE_OWNER` | Your organization | `"MyCompany Team"` |
| `TEMPLATE_COPYRIGHT` | Copyright holder | `"MyCompany Team"` |
| `TEMPLATE_AUTHOR` | Your name | `"John Doe"` |
| `TEMPLATE_CREATED_AT` | ISO timestamp | `"2025-05-24T10:00:00Z"` |
| `TEMPLATE_LAST_MODIFIED_AT` | ISO timestamp | `"2025-05-24T10:00:00Z"` |
| `TEMPLATE-*-UUID-REPLACE-ME` | New UUID | Generate with `uuidgen` |
| `TEMPLATE_HASH_TO_BE_COMPUTED` | Leave as-is | Will be computed by stamper |

### Node-Specific Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `template_node` | Your node name | `"data_processor"` |
| `template_required_field` | Your field name | `"input_file_path"` |
| `template_optional_field` | Your field name | `"output_format"` |
| `TEMPLATE_DEFAULT_VALUE` | Your default | `"json"` |
| `run_template_node` | Your function name | `run_data_processor` |
| `TemplateInputState` | Your class name | `DataProcessorInputState` |
| `TemplateOutputState` | Your class name | `DataProcessorOutputState` |

## UUID Generation

Generate new UUIDs for all metadata blocks:

```bash
# On macOS/Linux
uuidgen

# Or using Python
python -c "import uuid; print(uuid.uuid4())"
```

## Validation

After making all replacements:

1. **Run tests**:
   ```bash
   pytest src/omnibase/nodes/your_node_name/v1_0_0/node_tests/
   ```

2. **Validate metadata**:
   ```bash
   python -m omnibase.tools.validator src/omnibase/nodes/your_node_name/
   ```

3. **Test CLI**:
   ```bash
   python -m omnibase.nodes.your_node_name.v1_0_0.node --help
   ```

4. **Run stamper** (to compute hashes):
   ```bash
   python -m omnibase.tools.stamper src/omnibase/nodes/your_node_name/
   ```

## Best Practices

1. **Follow naming conventions**: Use snake_case for all file and directory names
2. **Update all metadata**: Don't leave any template placeholders
3. **Write comprehensive tests**: Cover success, failure, and edge cases
4. **Document thoroughly**: Update README with clear usage examples
5. **Validate early**: Run tests and validation after each major change
6. **Use meaningful names**: Choose descriptive names for fields and functions

## Common Mistakes

1. **Forgetting to delete the .onexignore file**: This is the most critical mistake! The template's .onexignore file hides validation errors and template placeholders. Always delete it first.
2. **Forgetting to update imports**: Make sure all imports match your renamed classes
3. **Leaving template placeholders**: Search for "TEMPLATE" to find missed replacements
4. **Not updating test assertions**: Tests should match your actual output structure
5. **Inconsistent naming**: Use the same naming pattern throughout all files
6. **Missing metadata updates**: Every file should have updated metadata blocks

## Automation Script (Future)

A script to automate this process would:

1. Prompt for node name and basic information
2. Copy template directory
3. Perform all text replacements
4. Generate new UUIDs
5. Run initial validation
6. Create initial commit

```bash
# Future script usage:
./scripts/create_node_from_template.sh \
  --name "data_processor" \
  --description "Processes data files and converts formats" \
  --author "John Doe" \
  --tags "data,processing,conversion"
```

## Registry Integration

After creating your node:

1. **Update .onextree**: Add your node to the registry manifest
2. **Register handlers**: If your node uses custom file handlers
3. **Update documentation**: Add to the main project documentation
4. **Create PR**: Follow the project's contribution guidelines
