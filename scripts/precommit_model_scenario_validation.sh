#!/usr/bin/env bash
set -euo pipefail

# Find all nodes in the canonical nodes directory
NODES_DIR="src/omnibase/nodes"
EXIT_CODE=0

for node_path in "$NODES_DIR"/*/v1_0_0; do
  node_name=$(basename $(dirname "$node_path"))
  model_path="$node_path/models/state.py"
  contract_path="$node_path/contract.yaml"
  scenarios_dir="$node_path/scenarios"

  if [[ -f "$model_path" && -f "$contract_path" ]]; then
    echo "[CHECK] Model/contract drift for $node_name"
    if ! poetry run onex check-model-alignment "$node_name" "$contract_path" "$model_path"; then
      EXIT_CODE=1
    fi
  fi

  if [[ -d "$scenarios_dir" && -f "$model_path" ]]; then
    echo "[CHECK] Scenario validation for $node_name"
    if ! poetry run onex validate-scenarios "$node_name" "$model_path" "$scenarios_dir"; then
      EXIT_CODE=1
    fi
  fi

done

exit $EXIT_CODE 