# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: utils_velocity_log.py
# version: 1.0.0
# uuid: 4304b690-34b9-4ded-8ee0-10f8f521ea60
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.169827
# last_modified_at: 2025-05-21T16:42:46.098868
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 826b1f2aa28fe167123e9538ddd924141c5cda51ea77f029108edf2a533ac56a
# entrypoint: python@utils_velocity_log.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.utils_velocity_log
# meta_type: tool
# === /OmniNode:Metadata ===


import argparse
import re
import subprocess
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

# Fix import to avoid type confusion between pydantic.BaseModel and any local BaseModel
from pydantic import BaseModel as PydanticBaseModel

# Use only the aliased PydanticBaseModel for all model definitions to avoid type confusion


# Template loading helpers
def load_template(path: str | Path) -> str:
    return Path(path).read_text()


WEEKLY_TMPL_PATH = "src/omnibase/templates/dev_logs/velocity_log_weekly.tmpl"
ENTRY_TMPL_PATH = "src/omnibase/templates/dev_logs/velocity_log_entry.tmpl"
weekly_template = load_template(WEEKLY_TMPL_PATH)
entry_template = load_template(ENTRY_TMPL_PATH)


# Pydantic models
class VelocityLogEntry(PydanticBaseModel):
    date: str
    summary: str = "- <add summary of this day's progress>"
    velocity_log_id: str = "<uuid>"
    parent_log_id: str = "<uuid or null>"
    score: str = "<add here>"
    lines_changed: str = "<+X / -Y>"
    files_modified: int = 0
    time_spent: str = "<duration>"
    velocity_metric: str = "<add here>"
    key_achievements: str = "- <add here>"
    prompts_actions: str = "- <add here>"
    major_milestones: str = "- <add here>"
    blockers_next_steps: str = "- <add here>"
    related_issues: str = "None"
    breaking_changes: str = "None"
    migration_notes: str = "None"
    documentation_impact: str = "None"
    test_coverage: str = "None"
    security_notes: str = "None"
    reviewers: str = "None"
    velocity_log_reference: str = "<PR description reference or 'None'>"
    # For preserving manual edits
    raw_report: str = ""


class WeeklyVelocityLog(PydanticBaseModel):
    week_start: str
    week_end: str
    entries: List[str]


# Helper to get week start (Monday) and end (Sunday) for a given date
def week_bounds(dt: datetime) -> tuple[datetime, datetime]:
    weekday = dt.weekday()
    monday = dt - timedelta(days=weekday)
    sunday = monday + timedelta(days=6)
    return monday, sunday


# Helper to get git user.name and normalize for directory
def get_user() -> str:
    return (
        subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
        .stdout.strip()
        .lower()
        .replace(" ", "_")
    )


# Helper to get lines changed and files modified
def get_git_stats() -> tuple[str, int]:
    shortstat = subprocess.run(
        ["git", "diff", "--shortstat", "origin/main...HEAD"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    lines_changed = "<+X / -Y>"
    files_modified = 0
    if shortstat:
        m = re.search(r"(\d+) files? changed", shortstat)
        if m:
            files_modified = int(m.group(1))
        ins = re.search(r"(\d+) insertions?\(\+\)", shortstat)
        dels = re.search(r"(\d+) deletions?\(-\)", shortstat)
        plus = int(ins.group(1)) if ins else 0
        minus = int(dels.group(1)) if dels else 0
        lines_changed = f"+{plus} / -{minus}"
    return lines_changed, files_modified


# Helper to get commit times and actions
def get_commit_info() -> tuple[str, list[str]]:
    commit_times = (
        subprocess.run(
            ["git", "log", "--reverse", "--format=%cI", "origin/main..HEAD"],
            capture_output=True,
            text=True,
        )
        .stdout.strip()
        .split("\n")
    )
    commit_times = [t for t in commit_times if t]
    start_time = commit_times[0] if commit_times else "<duration>"
    end_time = commit_times[-1] if commit_times else "<duration>"
    try:
        if commit_times:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            time_spent = str(end_dt - start_dt)
        else:
            time_spent = "<duration>"
    except Exception:
        time_spent = "<duration>"
    commit_actions = (
        subprocess.run(
            [
                "git",
                "log",
                "--reverse",
                '--format=[%cI] :rocket: %s (id: %h, agent: "%an")',
                "origin/main..HEAD",
            ],
            capture_output=True,
            text=True,
        )
        .stdout.strip()
        .split("\n")
    )
    commit_actions = [a for a in commit_actions if a]
    return time_spent, commit_actions


# CLI argument parsing
def parse_args() -> list[str]:
    parser = argparse.ArgumentParser(
        description="Generate or update velocity log entries."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--date", type=str, help="Single date (YYYY-MM-DD)")
    group.add_argument(
        "--range",
        nargs=2,
        type=str,
        metavar=("START", "END"),
        help="Date range (inclusive, YYYY-MM-DD YYYY-MM-DD)",
    )
    group.add_argument(
        "--dates", nargs="+", type=str, help="List of dates (YYYY-MM-DD ...)"
    )
    args = parser.parse_args()
    if args.date:
        dates = [args.date]
    elif args.range:
        start = datetime.strptime(args.range[0], "%Y-%m-%d")
        end = datetime.strptime(args.range[1], "%Y-%m-%d")
        dates = [
            (start + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range((end - start).days + 1)
        ]
    elif args.dates:
        dates = args.dates
    else:
        dates = [datetime.now().strftime("%Y-%m-%d")]
    return dates


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except Exception:
        return False


# Render entry from template and model
def render_entry(entry: VelocityLogEntry) -> str:
    if not is_valid_date(entry.date):
        return ""
    s = entry_template
    for k, v in entry.__dict__.items():
        s = s.replace(f"<{k}>", str(v) if v else f"<{k}>")
    # Remove any remaining placeholders
    s = re.sub(r"<[^>]+>", "", s)
    # Remove empty Velocity Report blocks (no date)
    if not entry.date or entry.date.strip() == "":
        return ""
    return s


# Main logic
def main() -> None:
    user = get_user()
    dates = parse_args()
    updated = set()
    for iso_date in dates:
        if not is_valid_date(iso_date):
            print(f"Skipping invalid date: {iso_date}")
            continue
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
        monday, sunday = week_bounds(dt)
        week_start = monday.strftime("%Y_%m_%d")
        week_end = sunday.strftime("%Y_%m_%d")
        iso_week_start = monday.strftime("%Y-%m-%d")
        iso_week_end = sunday.strftime("%Y-%m-%d")
        log_dir = Path(f"docs/dev_logs/{user}")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"velocity_log_{week_start}-{week_end}.md"
        # Read existing log if present
        existing_content = log_path.read_text() if log_path.exists() else ""
        # Parse existing daily summaries and reports
        daily_entries = {}
        for m in re.finditer(
            r"### (\d{4}-\d{2}-\d{2})\n(- .+?)(?=\n###|\n# Velocity Report:|\Z)",
            existing_content,
            re.DOTALL,
        ):
            date, summary = m.group(1), m.group(2).strip()
            if is_valid_date(date):
                daily_entries[date] = VelocityLogEntry(date=date, summary=summary)
        # Parse existing velocity reports
        for m in re.finditer(
            r"# Velocity Report: .+?\((\d{4}-\d{2}-\d{2})\)\n(.*?)(?=\n# Velocity Report:|\Z)",
            existing_content,
            re.DOTALL,
        ):
            date, raw_report = m.group(1), m.group(2).strip()
            if is_valid_date(date) and date in daily_entries:
                daily_entries[date].raw_report = raw_report
        # Build all days in this week
        week_dates = [
            (monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)
        ]
        # Update or create entries for specified dates
        for d in week_dates:
            if is_valid_date(d) and d not in daily_entries:
                daily_entries[d] = VelocityLogEntry(date=d)
        # For each date in the CLI list, update the entry with new details
        for d in dates:
            if not is_valid_date(d):
                continue
            entry = daily_entries[d]
            # Only update if not already detailed
            if not entry.raw_report:
                entry.velocity_log_id = str(uuid.uuid4())
                # Find parent_log_id from previous reports
                prev_dates = [
                    date
                    for date in week_dates
                    if date < d and daily_entries[date].raw_report
                ]
                if prev_dates:
                    last_report = daily_entries[prev_dates[-1]]
                    entry.parent_log_id = last_report.velocity_log_id
                lines_changed, files_modified = get_git_stats()
                entry.lines_changed = lines_changed
                entry.files_modified = files_modified
                time_spent, commit_actions = get_commit_info()
                entry.time_spent = time_spent
                entry.prompts_actions = (
                    "\n".join(commit_actions) if commit_actions else "- <add here>"
                )
                # All other fields remain as placeholders
                entry.raw_report = ""  # Will be rendered fresh
                updated.add((log_path, d))
        # Render the log
        entries_rendered = []
        for d in week_dates:
            if not is_valid_date(d):
                continue
            entry = daily_entries[d]
            # Always render the summary
            entry_block = f"### {entry.date}\n{entry.summary}\n"
            # If this date is in the CLI list, render the detailed report
            if d in dates:
                rendered = render_entry(entry)
                if rendered.strip():
                    entry_block += rendered
            elif entry.raw_report:
                # Preserve any existing detailed report
                entry_block += f"# Velocity Report: <Short Title> ({entry.date})\n{entry.raw_report}\n"
            entries_rendered.append(entry_block)
        # Assemble the full log
        log = weekly_template.replace("<YYYY-MM-DD>", iso_week_start, 1).replace(
            "<YYYY-MM-DD>", iso_week_end, 1
        )
        log = log.replace("<!-- Entries go here -->", "\n".join(entries_rendered))
        log_path.write_text(log)
    # Print summary
    if updated:
        print("Updated the following velocity log entries:")
        for log_path, iso_date in sorted(updated):
            print(f"  {log_path} for {iso_date}")
        print(
            "Please review and fill in all manual fields (e.g., Score, Key Achievements, Milestones, etc.).\n"
        )
    else:
        print("No updates were made. All specified entries already exist.")


if __name__ == "__main__":
    main()
