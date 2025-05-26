#!/bin/bash

# ONEX Node Validation Script
# Discovers and validates each ONEX node individually using their CLI interfaces
# This provides smoke testing for node CLIs beyond what the automated test suite covers

set -e

echo "🔍 ONEX Node Validation"
echo "======================="
echo ""

# Discover all nodes in the nodes directory
NODES_DIR="src/omnibase/nodes"
if [ ! -d "$NODES_DIR" ]; then
    echo "❌ Error: Nodes directory not found at $NODES_DIR"
    exit 1
fi

echo "📂 Discovering nodes in $NODES_DIR..."
DISCOVERED_NODES=()
for node_dir in "$NODES_DIR"/*; do
    if [ -d "$node_dir" ] && [ "$(basename "$node_dir")" != "__pycache__" ]; then
        node_name=$(basename "$node_dir")
        DISCOVERED_NODES+=("$node_name")
        echo "   Found: $node_name"
    fi
done

echo ""
echo "🧪 Testing each node individually..."
echo "===================================="

PASSED_NODES=()
FAILED_NODES=()

for node in "${DISCOVERED_NODES[@]}"; do
    echo ""
    echo "🔍 Testing $node..."
    
    # Find the node's main module
    node_module="omnibase.nodes.$node.v1_0_0.node"
    
    # Test if the node module exists and can be imported
    if poetry run python -c "import $node_module" 2>/dev/null; then
        echo "   ✓ Module import successful"
        
        # Test CLI help (basic smoke test)
        if poetry run python -m "$node_module" --help >/dev/null 2>&1; then
            echo "   ✓ CLI help accessible"
            PASSED_NODES+=("$node")
        else
            echo "   ❌ CLI help failed"
            FAILED_NODES+=("$node")
        fi
    else
        echo "   ❌ Module import failed"
        FAILED_NODES+=("$node")
    fi
done

echo ""
echo "📊 Individual Node Validation Results:"
echo "======================================"

if [ ${#PASSED_NODES[@]} -gt 0 ]; then
    echo "✅ Passed Nodes (${#PASSED_NODES[@]}):"
    for node in "${PASSED_NODES[@]}"; do
        echo "   ✓ $node"
    done
fi

if [ ${#FAILED_NODES[@]} -gt 0 ]; then
    echo ""
    echo "❌ Failed Nodes (${#FAILED_NODES[@]}):"
    for node in "${FAILED_NODES[@]}"; do
        echo "   ✗ $node"
    done
fi

echo ""
echo "📈 Summary:"
echo "- ${#DISCOVERED_NODES[@]} total nodes discovered"
echo "- ${#PASSED_NODES[@]} nodes passed individual validation"
echo "- ${#FAILED_NODES[@]} nodes failed individual validation"

if [ ${#FAILED_NODES[@]} -gt 0 ]; then
    echo ""
    echo "❌ Some nodes failed individual validation. Check the output above for details."
    exit 1
else
    echo ""
    echo "✅ All discovered nodes passed individual validation!"
fi 