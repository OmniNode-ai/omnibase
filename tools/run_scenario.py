#!/usr/bin/env python3
"""
Minimal ONEX scenario runner for tree generator node.
Loads a scenario chain YAML, loads the referenced config, invokes the node via CLI, and checks outputs.
Supports both ONEX and non-ONEX scenarios.
"""
import sys
import subprocess
from pathlib import Path
from omnibase.utils.yaml_extractor import load_and_validate_yaml_model
from omnibase.model.model_scenario import ScenarioConfigModel, ScenarioChainModel

def run_treegen_node(input_args):
    import json
    cli_args = [
        '--args=' + json.dumps([
            '--root-directory', input_args.get('root_directory', 'src/omnibase'),
            '--output-format', input_args.get('output_format', 'yaml'),
            '--output-path', input_args.get('output_path', '.onextree'),
            '--include-metadata' if input_args.get('include_metadata', True) else ''
        ])
    ]
    cmd = [
        'poetry', 'run', 'onex', 'run', 'tree_generator_node',
    ] + cli_args
    print(f"[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: run_scenario.py <scenario_chain.yaml>")
        sys.exit(1)
    chain_path = Path(sys.argv[1])
    try:
        chain = load_and_validate_yaml_model(chain_path, ScenarioChainModel)
    except Exception as e:
        print(f"[ERROR] Scenario chain validation failed: {e}")
        sys.exit(3)
    config_path = chain.config
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
        if node != 'tree_generator_node':
            print(f"[SKIP] Node {node} not supported in this runner.")
            continue
        result = run_treegen_node(input_args)
        output_path = input_args.get('output_path', '.onextree')
        if 'manifest_path' in expect:
            manifest_path = expect['manifest_path']
            if not Path(manifest_path).exists():
                print(f"[FAIL] Expected manifest {manifest_path} not found.")
                sys.exit(2)
            else:
                print(f"[PASS] Manifest {manifest_path} generated.")
        if 'status' in expect:
            import yaml as yml
            with open(output_path, 'r') as f:
                tree = yml.safe_load(f)
            print(f"[INFO] Scenario step completed. (Status check not implemented)")
    print("[DONE] Scenario completed.")

if __name__ == "__main__":
    main() 