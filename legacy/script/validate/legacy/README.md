# Legacy Directory Tree Validator

This directory contains the legacy implementation of the directory tree validator, preserved for reference during the migration to the new `.tree` + `.treerules` system.

## Contents

- `validate_directory_tree.py`: The original validator implementation using `DirectoryTreeTemplate` and rule-based validation

## Purpose

These files are kept for reference to:
1. Preserve the working code for pattern/rule-based validation
2. Enable incremental porting of validation logic to the new system
3. Support regression testing and comparison
4. Provide a fallback if needed during migration

## Status

These files are deprecated and should not be used in new code. They are maintained here for reference only.

## Migration Notes

The new implementation:
- Uses `.tree` files for structure validation
- Uses `.treerules` files for rule-based validation
- Separates concerns between structure and rules
- Provides a more maintainable and extensible architecture 