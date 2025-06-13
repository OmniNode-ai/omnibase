from enum import Enum


class EnumFixOperationType(Enum):
    """Enumeration of fix operation types for standards compliance."""
    
    # File and directory operations
    RENAME_FILE = "rename_file"
    MOVE_FILE = "move_file"
    CREATE_DIRECTORY = "create_directory"
    DELETE_FILE = "delete_file"
    
    # Content modifications
    UPDATE_IMPORTS = "update_imports"
    RENAME_CLASS = "rename_class"
    RENAME_VARIABLE = "rename_variable"
    RENAME_FUNCTION = "rename_function"
    
    # Template artifact removal
    REMOVE_TEMPLATE_REFERENCE = "remove_template_reference"
    REPLACE_TEMPLATE_TOKEN = "replace_template_token"
    
    # Metadata fixes
    UPDATE_NODE_METADATA = "update_node_metadata"
    FIX_CONTRACT_SCHEMA = "fix_contract_schema"
    UPDATE_DOCUMENTATION = "update_documentation"
    
    # Code organization
    MOVE_MODEL_TO_MODELS_DIR = "move_model_to_models_dir"
    MOVE_ENUM_TO_ENUMS_DIR = "move_enum_to_enums_dir"
    SPLIT_LARGE_FILE = "split_large_file"
    
    # Naming convention fixes
    FIX_SNAKE_CASE = "fix_snake_case"
    FIX_PASCAL_CASE = "fix_pascal_case"
    ADD_PREFIX = "add_prefix"
    REMOVE_PREFIX = "remove_prefix" 