# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: yaml_issues_tracker.py
# version: 1.0.0
# uuid: dc2c513d-eccf-49df-b6d3-19526840541a
# author: OmniNode Team
# created_at: 2025-05-27T18:04:26.862010
# last_modified_at: 2025-05-27T22:20:27.572387
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3e97204e7acf2a14e9e178fb8d6d91ccc81d80dbf0f83e699b313cf3be10e902
# entrypoint: python@yaml_issues_tracker.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.yaml_issues_tracker
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
YAML Issues Tracker and Systematic Fixer

This script tracks YAML formatting issues across the codebase and provides
systematic fixes to prevent recurring problems.

Key Features:
- Tracks which files have recurring issues
- Identifies root causes (stamper, manual edits, etc.)
- Provides targeted fixes for different issue types
- Maintains a database of known problematic files
- Generates reports for monitoring progress
"""

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class YAMLIssue:
    """Represents a specific YAML formatting issue."""

    file_path: str
    line_number: int
    issue_type: str  # 'indentation', 'line-length', 'syntax', 'key-duplicates'
    description: str
    severity: str  # 'error', 'warning'
    first_seen: str
    last_seen: str
    occurrence_count: int
    root_cause: Optional[str] = None  # 'stamper', 'manual_edit', 'template', 'unknown'


@dataclass
class FileIssueHistory:
    """Tracks issue history for a specific file."""

    file_path: str
    total_issues: int
    recurring_issues: int
    last_clean: Optional[str]
    fix_attempts: int
    root_causes: Set[str]
    issues: List[YAMLIssue]


class YAMLIssuesTracker:
    """Tracks and manages YAML formatting issues across the codebase."""

    def __init__(self, db_path: str = ".yaml_issues_db.json"):
        self.db_path = Path(db_path)
        self.issues_db: Dict[str, FileIssueHistory] = {}
        self.load_database()

    def load_database(self) -> None:
        """Load existing issues database."""
        if self.db_path.exists():
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                    for file_path, file_data in data.items():
                        issues = [YAMLIssue(**issue) for issue in file_data["issues"]]
                        file_data["issues"] = issues
                        file_data["root_causes"] = set(file_data["root_causes"])
                        self.issues_db[file_path] = FileIssueHistory(**file_data)
            except Exception as e:
                print(f"Warning: Could not load issues database: {e}")
                self.issues_db = {}

    def save_database(self) -> None:
        """Save issues database to disk."""
        data = {}
        for file_path, file_history in self.issues_db.items():
            file_dict = asdict(file_history)
            file_dict["root_causes"] = list(file_history.root_causes)
            data[file_path] = file_dict

        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def run_yamllint(self) -> List[YAMLIssue]:
        """Run yamllint and parse the output into YAMLIssue objects."""
        try:
            result = subprocess.run(
                ["yamllint", ".", "--format", "parsable"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            issues = []
            current_time = datetime.now().isoformat()

            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                # Parse yamllint output: file:line:column: [level] message (rule)
                try:
                    parts = line.split(":", 3)
                    if len(parts) >= 4:
                        file_path = parts[0]
                        line_number = int(parts[1])
                        # Skip column for now
                        rest = parts[3].strip()

                        # Extract severity and message
                        if rest.startswith("[error]"):
                            severity = "error"
                            message = rest[7:].strip()
                        elif rest.startswith("[warning]"):
                            severity = "warning"
                            message = rest[9:].strip()
                        else:
                            severity = "error"
                            message = rest

                        # Determine issue type from message
                        issue_type = self._classify_issue_type(message)

                        issue = YAMLIssue(
                            file_path=file_path,
                            line_number=line_number,
                            issue_type=issue_type,
                            description=message,
                            severity=severity,
                            first_seen=current_time,
                            last_seen=current_time,
                            occurrence_count=1,
                        )
                        issues.append(issue)

                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse yamllint line: {line} ({e})")
                    continue

            return issues

        except subprocess.CalledProcessError as e:
            print(f"Error running yamllint: {e}")
            return []
        except FileNotFoundError:
            print("Error: yamllint not found. Please install yamllint.")
            return []

    def _classify_issue_type(self, message: str) -> str:
        """Classify the type of YAML issue based on the message."""
        message_lower = message.lower()

        if "indentation" in message_lower:
            return "indentation"
        elif "line too long" in message_lower:
            return "line-length"
        elif "syntax error" in message_lower:
            return "syntax"
        elif "duplication" in message_lower:
            return "key-duplicates"
        elif "document start" in message_lower:
            return "document-format"
        else:
            return "other"

    def _determine_root_cause(self, file_path: str) -> str:
        """Determine the likely root cause of issues in a file."""
        path = Path(file_path)

        # Check if it's a stamper-generated file
        if self._is_stamper_generated(path):
            return "stamper"

        # Check if it's a template file
        if "template" in file_path.lower() or "example" in file_path.lower():
            return "template"

        # Check if it's a CI/workflow file
        if ".github" in file_path:
            return "ci_workflow"

        # Check if it's a schema file
        if "schema" in file_path.lower():
            return "schema"

        # Check if it's a contract file
        if "contract" in file_path.lower():
            return "contract"

        return "unknown"

    def _is_stamper_generated(self, file_path: Path) -> bool:
        """Check if a file is generated by the stamper."""
        try:
            if file_path.suffix in [".py", ".md"]:
                with open(file_path, "r") as f:
                    content = f.read(1000)  # Read first 1000 chars
                    return "=== OmniNode:Metadata ===" in content
            return False
        except Exception:
            return False

    def update_issues(self, new_issues: List[YAMLIssue]) -> None:
        """Update the issues database with new issues."""
        current_time = datetime.now().isoformat()

        # Group issues by file
        issues_by_file: Dict[str, List[YAMLIssue]] = {}
        for issue in new_issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)

        # Update database
        for file_path, file_issues in issues_by_file.items():
            if file_path not in self.issues_db:
                self.issues_db[file_path] = FileIssueHistory(
                    file_path=file_path,
                    total_issues=0,
                    recurring_issues=0,
                    last_clean=None,
                    fix_attempts=0,
                    root_causes=set(),
                    issues=[],
                )

            file_history = self.issues_db[file_path]
            root_cause = self._determine_root_cause(file_path)
            file_history.root_causes.add(root_cause)

            # Update or add issues
            existing_issues = {
                (issue.line_number, issue.issue_type, issue.description): issue
                for issue in file_history.issues
            }

            for new_issue in file_issues:
                key = (
                    new_issue.line_number,
                    new_issue.issue_type,
                    new_issue.description,
                )
                if key in existing_issues:
                    # Update existing issue
                    existing_issue = existing_issues[key]
                    existing_issue.last_seen = current_time
                    existing_issue.occurrence_count += 1
                    if existing_issue.occurrence_count > 1:
                        file_history.recurring_issues += 1
                else:
                    # Add new issue
                    new_issue.root_cause = root_cause
                    file_history.issues.append(new_issue)
                    file_history.total_issues += 1

    def get_recurring_files(self) -> List[str]:
        """Get files with recurring issues."""
        return [
            file_path
            for file_path, history in self.issues_db.items()
            if history.recurring_issues > 0
        ]

    def get_files_by_root_cause(self, root_cause: str) -> List[str]:
        """Get files with issues caused by a specific root cause."""
        return [
            file_path
            for file_path, history in self.issues_db.items()
            if root_cause in history.root_causes
        ]

    def generate_report(self) -> str:
        """Generate a comprehensive report of YAML issues."""
        report = []
        report.append("# YAML Issues Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        # Summary statistics
        total_files = len(self.issues_db)
        recurring_files = len(self.get_recurring_files())
        total_issues = sum(history.total_issues for history in self.issues_db.values())
        total_recurring = sum(
            history.recurring_issues for history in self.issues_db.values()
        )

        report.append("## Summary")
        report.append(f"- Total files with issues: {total_files}")
        report.append(f"- Files with recurring issues: {recurring_files}")
        report.append(f"- Total issues: {total_issues}")
        report.append(f"- Recurring issues: {total_recurring}")
        report.append("")

        # Issues by root cause
        root_causes = set()
        for history in self.issues_db.values():
            root_causes.update(history.root_causes)

        report.append("## Issues by Root Cause")
        for cause in sorted(root_causes):
            files = self.get_files_by_root_cause(cause)
            report.append(f"- {cause}: {len(files)} files")
            for file_path in files[:5]:  # Show first 5
                report.append(f"  - {file_path}")
            if len(files) > 5:
                report.append(f"  - ... and {len(files) - 5} more")
        report.append("")

        # Most problematic files
        report.append("## Most Problematic Files")
        sorted_files = sorted(
            self.issues_db.items(),
            key=lambda x: (x[1].recurring_issues, x[1].total_issues),
            reverse=True,
        )

        for file_path, history in sorted_files[:10]:
            report.append(f"- {file_path}")
            report.append(f"  - Total issues: {history.total_issues}")
            report.append(f"  - Recurring issues: {history.recurring_issues}")
            report.append(f"  - Root causes: {', '.join(history.root_causes)}")
            report.append(f"  - Fix attempts: {history.fix_attempts}")

        return "\n".join(report)

    def mark_file_fixed(self, file_path: str) -> None:
        """Mark a file as fixed (remove from tracking)."""
        if file_path in self.issues_db:
            self.issues_db[file_path].last_clean = datetime.now().isoformat()
            self.issues_db[file_path].issues = []
            self.issues_db[file_path].total_issues = 0
            self.issues_db[file_path].recurring_issues = 0

    def increment_fix_attempts(self, file_path: str) -> None:
        """Increment fix attempts counter for a file."""
        if file_path in self.issues_db:
            self.issues_db[file_path].fix_attempts += 1


def main() -> None:
    """Main entry point for the YAML issues tracker."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Track and manage YAML formatting issues"
    )
    parser.add_argument("--scan", action="store_true", help="Scan for current issues")
    parser.add_argument("--report", action="store_true", help="Generate issues report")
    parser.add_argument("--mark-fixed", help="Mark a file as fixed")
    parser.add_argument(
        "--recurring", action="store_true", help="Show files with recurring issues"
    )
    parser.add_argument("--by-cause", help="Show files by root cause")

    args = parser.parse_args()

    tracker = YAMLIssuesTracker()

    if args.scan:
        print("Scanning for YAML issues...")
        issues = tracker.run_yamllint()
        tracker.update_issues(issues)
        tracker.save_database()
        print(
            f"Found {len(issues)} issues across {len(set(issue.file_path for issue in issues))} files"
        )

    if args.report:
        print(tracker.generate_report())

    if args.mark_fixed:
        tracker.mark_file_fixed(args.mark_fixed)
        tracker.save_database()
        print(f"Marked {args.mark_fixed} as fixed")

    if args.recurring:
        recurring = tracker.get_recurring_files()
        print("Files with recurring issues:")
        for file_path in recurring:
            history = tracker.issues_db[file_path]
            print(
                f"  {file_path} ({history.recurring_issues} recurring, {history.fix_attempts} fix attempts)"
            )

    if args.by_cause:
        files = tracker.get_files_by_root_cause(args.by_cause)
        print(f"Files with issues caused by '{args.by_cause}':")
        for file_path in files:
            print(f"  {file_path}")


if __name__ == "__main__":
    main()
