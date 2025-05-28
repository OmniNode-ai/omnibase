#!/bin/bash

# Script to revert Python files that only have header changes

echo "Finding Python files with only header changes..."

files_to_revert=()

# Get all modified Python files
for file in $(git diff --name-only | grep "\.py$"); do
    # Skip files we know should not be reverted
    if [[ "$file" == "src/omnibase/model/model_node_metadata.py" ]] || \
       [[ "$file" == "src/omnibase/runtimes/onex_runtime/v1_0_0/handlers/handler_python.py" ]] || \
       [[ "$file" == "src/omnibase/nodes/node_manager_node/v1_0_0/helpers/helpers_cli_commands.py" ]] || \
       [[ "$file" == "src/omnibase/nodes/node_manager_node/v1_0_0/helpers/helpers_maintenance.py" ]] || \
       [[ "$file" == "revert_incorrect_stamps.py" ]] || \
       [[ "$file" == "revert_header_only_changes.sh" ]]; then
        echo "Skipping $file (intentional changes)"
        continue
    fi
    
    # Check if file only has header changes (no content changes)
    content_changes=$(git diff "$file" | grep -E "^[+-]" | grep -v "^[+-]#" | grep -v "^[+-]$" | grep -v "^---" | grep -v "^+++" | wc -l)
    
    if [ "$content_changes" -eq 0 ]; then
        echo "✓ $file - only header changes"
        files_to_revert+=("$file")
    else
        echo "✗ $file - has content changes ($content_changes lines)"
    fi
done

if [ ${#files_to_revert[@]} -eq 0 ]; then
    echo "No Python files found with only header changes."
    exit 0
fi

echo ""
echo "Found ${#files_to_revert[@]} Python files to revert:"
for file in "${files_to_revert[@]}"; do
    echo "  - $file"
done

echo ""
read -p "Revert these ${#files_to_revert[@]} files? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for file in "${files_to_revert[@]}"; do
        echo "Reverting $file..."
        git checkout HEAD -- "$file"
    done
    echo "Reverted ${#files_to_revert[@]} files."
else
    echo "Aborted."
fi 