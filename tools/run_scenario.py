#!/usr/bin/env python3
"""
Minimal ONEX scenario runner for tree generator node.
Loads a scenario chain YAML, loads the referenced config, invokes the node via CLI, and checks outputs.
Supports both ONEX and non-ONEX scenarios.
"""
import subprocess
import sys
from pathlib import Path
import json

from omnibase.model.model_scenario import ScenarioChainModel, ScenarioConfigModel, SingleScenarioModel
from omnibase.utils.yaml_extractor import load_and_validate_yaml_model


def run_node(node, input_args):
    # For CLI, always serialize as dict
    cli_args = input_args.model_dump() if hasattr(input_args, 'model_dump') else input_args
    cmd = [
        "poetry", "run", "onex", "run", node,
        "--args=" + json.dumps(cli_args)
    ]
    print(f"[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: run_scenario.py <scenario_chain.yaml | scenario.yaml>")
        sys.exit(1)
    chain_path = Path(sys.argv[1])
    chain = None
    single = None
    # Try to load as ScenarioChainModel
    try:
        chain = load_and_validate_yaml_model(chain_path, ScenarioChainModel)
    except Exception:
        pass
    if chain is None:
        # Try to load as SingleScenarioModel
        try:
            single = load_and_validate_yaml_model(chain_path, SingleScenarioModel)
        except Exception:
            pass
        if single is not None:
            # Wrap as a one-step chain
            class _AdHocChain:
                def __init__(self, single):
                    self.chain = [single]
                    self.config = None
            chain = _AdHocChain(single)
        else:
            print(f"[ERROR] File is neither a valid scenario chain nor a single scenario: {chain_path}")
            sys.exit(3)
    config_path = getattr(chain, 'config', None)
    if config_path:
        config_path = (chain_path.parent / config_path).resolve()
        try:
            config = load_and_validate_yaml_model(config_path, ScenarioConfigModel)
        except Exception as e:
            print(f"[ERROR] Scenario config validation failed: {e}")
            sys.exit(4)
    else:
        config = None
    for step in chain.chain:
        node = step.node
        input_args = step.input or {}
        expect = step.expect or {}
        result = run_node(node, input_args)
        # Only check output_path if present as attribute
        output_path = getattr(input_args, "output_path", None)
        if output_path and hasattr(expect, "manifest_path"):
            manifest_path = expect.manifest_path
            if not Path(manifest_path).exists():
                print(f"[FAIL] Expected manifest {manifest_path} not found.")
                sys.exit(2)
            else:
                print(f"[PASS] Manifest {manifest_path} generated.")
        if hasattr(expect, "status"):
            print(f"[INFO] Scenario step completed. (Status check not implemented)")
    print("[DONE] Scenario completed.")


if __name__ == "__main__":
    main()
