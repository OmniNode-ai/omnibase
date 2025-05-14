# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: cli_args
# namespace: omninode.tools.cli_args
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:56+00:00
# last_modified_at: 2025-04-27T18:12:56+00:00
# entrypoint: cli_args.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run code and configuration validators."
    )
    parser.add_argument(
        "--validators",
        type=str,
        help="Comma-separated list of validator names to run (default: all)",
    )
    parser.add_argument(
        "--group",
        type=str,
        help="Validator group/profile to run (e.g., quality, security, ci)",
    )
    parser.add_argument(
        "--target",
        type=str,
        help="Target path or container to validate (default: project root)",
    )
    parser.add_argument(
        "--config", type=str, help="Path to config override JSON/YAML file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="text",
        choices=["text", "json", "html", "sarif"],
        help="Output format",
    )
    parser.add_argument(
        "--auto-fix", action="store_true", help="Enable auto-fix mode (where supported)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed, but make no changes",
    )
    parser.add_argument(
        "--max-workers", type=int, default=4, help="Max parallel validator executions"
    )
    parser.add_argument(
        "--describe", action="store_true", help="Describe available validators and exit"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all available validators and exit"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show validator orchestrator version and exit",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Only validate staged files (for pre-commit)",
    )
    return parser.parse_args()
