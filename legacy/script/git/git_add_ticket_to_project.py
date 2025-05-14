#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: add_ticket_to_project
# namespace: omninode.tools.add_ticket_to_project
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:54+00:00
# last_modified_at: 2025-04-27T18:12:54+00:00
# entrypoint: add_ticket_to_project.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

import argparse
import re
import shutil
import subprocess
import sys

from foundation.script.git.omninode_issue_model import OmniNodeIssue
from pydantic import ValidationError


def check_gh_cli():
    if not shutil.which("gh"):
        print("Error: GitHub CLI (gh) is not installed or not in PATH.")
        sys.exit(1)


def render_issue_body(issue: OmniNodeIssue) -> str:
    req_md = "\n".join(f"  - [ ] {r}" for r in issue.requirements)
    acc_md = "\n".join(f"  - [ ] {a}" for a in issue.acceptance_criteria)
    return f"""# Title\n  {issue.title}\n\n# Status\n  {issue.status}\n\n# Priority\n  {issue.priority}\n\n# Notes\n  {issue.notes or ''}\n\n# Context\n  {issue.context}\n\n# Requirements\n{req_md}\n\n# Acceptance Criteria\n{acc_md}\n\n# Additional Notes\n  {issue.additional_notes or ''}\n"""


def create_issue(repo, issue: OmniNodeIssue, dry_run=False, verbose=False):
    body = render_issue_body(issue)
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        issue.title,
        "--body",
        body,
    ]
    print("[INFO] Command:", " ".join(cmd))
    if dry_run:
        print("[DRY RUN] Would execute:", " ".join(cmd))
        print("[DRY RUN] Issue body:\n", body)
        return f"https://github.com/{repo}/issues/FAKE"
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if verbose or result.returncode != 0:
            print("[STDOUT]", result.stdout.strip())
            print("[STDERR]", result.stderr.strip())
        if result.returncode == 0:
            print("Successfully created issue.")
            url_match = re.search(r"https://github.com/\S+/issues/\d+", result.stdout)
            if url_match:
                return url_match.group(0)
            lines = result.stdout.strip().splitlines()
            if lines:
                return lines[-1]
            else:
                print("Could not parse issue URL from output.")
                return None
        else:
            print("Error creating issue:")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def add_ticket(org, project_number, issue_url, dry_run=False, verbose=False):
    cmd = [
        "gh",
        "project",
        "item-add",
        str(project_number),
        "--owner",
        org,
        "--url",
        issue_url,
    ]
    print("[INFO] Command:", " ".join(cmd))
    if dry_run:
        print("[DRY RUN] Would execute:", " ".join(cmd))
        return 0
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if verbose or result.returncode != 0:
            print("[STDOUT]", result.stdout.strip())
            print("[STDERR]", result.stderr.strip())
        if result.returncode == 0:
            print("Successfully added issue to project board.")
        else:
            print("Error adding issue to project board:")
        return result.returncode
    except Exception as e:
        print(f"Exception: {e}")
        return 1


def remove_ticket(org, project_number, issue_url, dry_run=False, verbose=False):
    get_cmd = [
        "gh",
        "project",
        "item-list",
        str(project_number),
        "--owner",
        org,
        "--format",
        "json",
    ]
    print(f"[INFO] Command: {' '.join(get_cmd)}")
    if dry_run:
        print(f"[DRY RUN] Would execute: {' '.join(get_cmd)}")
        print(f"[DRY RUN] Would remove issue {issue_url} from project {project_number}")
        return 0
    try:
        result = subprocess.run(get_cmd, capture_output=True, text=True)
        if verbose or result.returncode != 0:
            print("[STDOUT]", result.stdout.strip())
            print("[STDERR]", result.stderr.strip())
        if result.returncode != 0:
            print("Error listing project items:")
            return 1
        import json

        items = json.loads(result.stdout)
        item_id = None
        for item in items:
            if item.get("content_url") == issue_url:
                item_id = item.get("id")
                break
        if not item_id:
            print(f"Issue {issue_url} not found in project {project_number}.")
            return 1
        rm_cmd = [
            "gh",
            "project",
            "item-remove",
            str(project_number),
            "--owner",
            org,
            "--id",
            str(item_id),
        ]
        print(f"[INFO] Command: {' '.join(rm_cmd)}")
        rm_result = subprocess.run(rm_cmd, capture_output=True, text=True)
        if verbose or rm_result.returncode != 0:
            print("[STDOUT]", rm_result.stdout.strip())
            print("[STDERR]", rm_result.stderr.strip())
        if rm_result.returncode == 0:
            print(f"Successfully removed issue from project {project_number}.")
        else:
            print(f"Error removing issue from project {project_number}:")
        return rm_result.returncode
    except Exception as e:
        print(f"Exception: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Add a GitHub issue to an org-level project board using gh CLI. Optionally create the issue first, and move it from another board."
    )
    parser.add_argument(
        "--org", required=True, help="GitHub organization name (e.g., OmniNode-ai)"
    )
    parser.add_argument(
        "--project", required=True, type=int, help="Project number (e.g., 1)"
    )
    parser.add_argument("--url", help="Full URL of the issue to add (if not creating)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the command(s) instead of executing them",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print extra output from CLI commands"
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create a new issue before adding to the project board",
    )
    parser.add_argument(
        "--repo", help="GitHub repo for issue creation (e.g., OmniNode-ai/ai-dev)"
    )
    parser.add_argument("--title", help="Title for new issue (required if --create)")
    parser.add_argument(
        "--context", help="Context for new issue (required if --create)"
    )
    parser.add_argument(
        "--requirements",
        nargs="*",
        help="Requirements for new issue (required if --create)",
    )
    parser.add_argument(
        "--acceptance-criteria",
        nargs="*",
        help="Acceptance criteria for new issue (required if --create)",
    )
    parser.add_argument(
        "--priority", default="Medium", help="Priority for new issue (default: Medium)"
    )
    parser.add_argument(
        "--status", default="Todo", help="Status for new issue (default: Todo)"
    )
    parser.add_argument("--notes", default="", help="Notes for new issue (optional)")
    parser.add_argument(
        "--additional-notes",
        default="",
        help="Additional notes for new issue (optional)",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Remove the issue from another project board after adding it here",
    )
    parser.add_argument(
        "--from-project",
        type=int,
        help="Project number to remove the issue from (used with --move)",
    )
    args = parser.parse_args()
    check_gh_cli()
    issue_url = args.url
    if args.create:
        # Validate and build the issue model
        try:
            issue = OmniNodeIssue(
                title=args.title,
                status=args.status,
                priority=args.priority,
                notes=args.notes,
                context=args.context,
                requirements=args.requirements,
                acceptance_criteria=args.acceptance_criteria,
                additional_notes=args.additional_notes,
            )
        except ValidationError as e:
            print("[ERROR] Issue validation failed:")
            print(e)
            sys.exit(1)
        issue_url = create_issue(
            args.repo, issue, dry_run=args.dry_run, verbose=args.verbose
        )
        if not issue_url:
            print("Failed to create issue. Aborting.")
            sys.exit(1)
    if not issue_url:
        print("Error: --url is required if not using --create.")
        sys.exit(1)
    rc = add_ticket(
        args.org, args.project, issue_url, args.dry_run, verbose=args.verbose
    )
    if rc == 0 and args.move and args.from_project:
        print(
            f"Moving issue: removing from project {args.from_project} after adding to {args.project}."
        )
        rc = remove_ticket(
            args.org, args.from_project, issue_url, args.dry_run, verbose=args.verbose
        )
    sys.exit(rc)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
