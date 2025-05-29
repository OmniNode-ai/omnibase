# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-27T17:23:40.229368'
# description: Stamped by PythonHandler
# entrypoint: python://test_github_actions.py
# hash: 4acea4635f09485e428c307db4618799672337762d618ec49246adf293b4300d
# last_modified_at: '2025-05-29T13:51:22.994621+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_github_actions.py
# namespace: py://omnibase.test_github_actions_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4250964a-449a-4ff8-bbac-765bc2db2d2b
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3

import re

import yaml

from omnibase.model.model_github_actions import GitHubActionsWorkflow
from scripts.comprehensive_yaml_fixer import fix_github_actions_indentation


def test_github_actions() -> None:
    # Read the file
    with open(".github/workflows/ci.yml", "r") as f:
        content = f.read()

    print("=== ORIGINAL CONTENT (first 200 chars) ===")
    print(repr(content[:200]))

    # Apply preprocessing
    content = re.sub(r"^true:$", '"on":', content, flags=re.MULTILINE)
    print("\n=== AFTER true->on FIX ===")
    print(repr(content[:200]))

    # Apply GitHub Actions specific indentation fixing
    fixed_content = fix_github_actions_indentation(content)
    print("\n=== AFTER GITHUB ACTIONS INDENTATION FIX (first 500 chars) ===")
    print(repr(fixed_content[:500]))

    # Try to parse with YAML
    try:
        data = yaml.safe_load(fixed_content)
        print("\n=== YAML PARSING: SUCCESS ===")
        print("Keys:", list(data.keys()) if data else "None")

        # Try to create the model
        try:
            GitHubActionsWorkflow(**data)
            print("=== PYDANTIC MODEL: SUCCESS ===")
        except Exception as e:
            print("=== PYDANTIC MODEL: FAILED ===")
            print(f"Error: {e}")
            print(f"Error type: {type(e)}")

    except yaml.YAMLError as e:
        print("\n=== YAML PARSING: FAILED ===")
        print(f"Error: {e}")

        # Show the problematic lines around the error
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            lines = fixed_content.split("\n")
            start = max(0, mark.line - 3)
            end = min(len(lines), mark.line + 4)
            print(f"\nLines around error (line {mark.line + 1}):")
            for i in range(start, end):
                marker = " >>> " if i == mark.line else "     "
                print(f"{marker}{i+1:3}: {repr(lines[i])}")


if __name__ == "__main__":
    test_github_actions()
