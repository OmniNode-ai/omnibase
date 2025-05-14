#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "git_template_orchestrate_git"
# namespace: "omninode.tools.git_template_orchestrate_git"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:32+00:00"
# last_modified_at: "2025-05-05T13:00:32+00:00"
# entrypoint: "git_template_orchestrate_git.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import argparse
import logging
import subprocess
import sys
from pathlib import Path

ACTIONS = ["add", "commit", "push", "add-ticket"]


def run_action(action, args, dry_run=False):
    if action == "add":
        cmd = ["git", "add", args.path or "."]
    elif action == "commit":
        cmd = ["git", "commit", "-m", args.message or "[orchestrate_git] commit"]
    elif action == "push":
        cmd = ["git", "push"]
    elif action == "add-ticket":
        ticket_args = [
            sys.executable,
            str(Path(__file__).parent / "add_ticket_to_project.py"),
            "--org",
            args.org,
            "--project",
            str(args.project),
            "--url",
            args.url,
        ]
        if dry_run:
            ticket_args.append("--dry-run")
        cmd = ticket_args
    else:
        print(f"Unknown action: {action}")
        return 1
    if dry_run:
        print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
        return 0
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout.strip())
        if result.returncode != 0:
            print(result.stderr.strip())
        return result.returncode
    except Exception as e:
        print(f"Exception: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate git and project actions (dry-run supported)"
    )
    parser.add_argument(
        "actions", nargs="*", choices=ACTIONS, help="Actions to perform in order"
    )
    parser.add_argument("--path", help="Path for git add (default: .)")
    parser.add_argument("--message", help="Commit message")
    parser.add_argument("--org", help="GitHub org for add-ticket")
    parser.add_argument("--project", type=int, help="Project number for add-ticket")
    parser.add_argument("--url", help="Issue URL for add-ticket")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions instead of executing them"
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    if not args.actions:
        logger.error("No actions specified. Choose from: %s", ", ".join(ACTIONS))
        sys.exit(1)
    results = []
    for action in args.actions:
        logger.info(f"Running action: {action}")
        rc = run_action(action, args, dry_run=args.dry_run)
        results.append((action, rc))
    logger.info("Summary:")
    for action, rc in results:
        logger.info(f"  {action}: {'OK' if rc == 0 else 'FAIL'}")
    sys.exit(max(rc for _, rc in results))


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()