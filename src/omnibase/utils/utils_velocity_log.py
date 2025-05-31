import argparse
import re
import subprocess
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from pydantic import BaseModel as PydanticBaseModel
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.model.model_log_entry import LogContextModel
_COMPONENT_NAME = Path(__file__).stem


def load_template(path: (str | Path)) ->str:
    return Path(path).read_text()


WEEKLY_TMPL_PATH = 'src/omnibase/templates/dev_logs/velocity_log_weekly.tmpl'
ENTRY_TMPL_PATH = 'src/omnibase/templates/dev_logs/velocity_log_entry.tmpl'
weekly_template = load_template(WEEKLY_TMPL_PATH)
entry_template = load_template(ENTRY_TMPL_PATH)


class VelocityLogEntry(PydanticBaseModel):
    date: str
    summary: str = "- <add summary of this day's progress>"
    velocity_log_id: str = '<uuid>'
    parent_log_id: str = '<uuid or null>'
    score: str = '<add here>'
    lines_changed: str = '<+X / -Y>'
    files_modified: int = 0
    time_spent: str = '<duration>'
    velocity_metric: str = '<add here>'
    key_achievements: str = '- <add here>'
    prompts_actions: str = '- <add here>'
    major_milestones: str = '- <add here>'
    blockers_next_steps: str = '- <add here>'
    related_issues: str = 'None'
    breaking_changes: str = 'None'
    migration_notes: str = 'None'
    documentation_impact: str = 'None'
    test_coverage: str = 'None'
    security_notes: str = 'None'
    reviewers: str = 'None'
    velocity_log_reference: str = "<PR description reference or 'None'>"
    raw_report: str = ''


class WeeklyVelocityLog(PydanticBaseModel):
    week_start: str
    week_end: str
    entries: List[str]


def week_bounds(dt: datetime) ->tuple[datetime, datetime]:
    weekday = dt.weekday()
    monday = dt - timedelta(days=weekday)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_user() ->str:
    return subprocess.run(['git', 'config', 'user.name'], capture_output=
        True, text=True).stdout.strip().lower().replace(' ', '_')


def get_git_stats() ->tuple[str, int]:
    shortstat = subprocess.run(['git', 'diff', '--shortstat',
        'origin/main...HEAD'], capture_output=True, text=True).stdout.strip()
    lines_changed = '<+X / -Y>'
    files_modified = 0
    if shortstat:
        m = re.search('(\\d+) files? changed', shortstat)
        if m:
            files_modified = int(m.group(1))
        ins = re.search('(\\d+) insertions?\\(\\+\\)', shortstat)
        dels = re.search('(\\d+) deletions?\\(-\\)', shortstat)
        plus = int(ins.group(1)) if ins else 0
        minus = int(dels.group(1)) if dels else 0
        lines_changed = f'+{plus} / -{minus}'
    return lines_changed, files_modified


def get_commit_info() ->tuple[str, list[str]]:
    commit_times = subprocess.run(['git', 'log', '--reverse',
        '--format=%cI', 'origin/main..HEAD'], capture_output=True, text=True
        ).stdout.strip().split('\n')
    commit_times = [t for t in commit_times if t]
    start_time = commit_times[0] if commit_times else '<duration>'
    end_time = commit_times[-1] if commit_times else '<duration>'
    try:
        if commit_times:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            time_spent = str(end_dt - start_dt)
        else:
            time_spent = '<duration>'
    except Exception:
        time_spent = '<duration>'
    commit_actions = subprocess.run(['git', 'log', '--reverse',
        '--format=[%cI] :rocket: %s (id: %h, agent: "%an")',
        'origin/main..HEAD'], capture_output=True, text=True).stdout.strip(
        ).split('\n')
    commit_actions = [a for a in commit_actions if a]
    return time_spent, commit_actions


def parse_args() ->list[str]:
    parser = argparse.ArgumentParser(description=
        'Generate or update velocity log entries.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--date', type=str, help='Single date (YYYY-MM-DD)')
    group.add_argument('--range', nargs=2, type=str, metavar=('START',
        'END'), help='Date range (inclusive, YYYY-MM-DD YYYY-MM-DD)')
    group.add_argument('--dates', nargs='+', type=str, help=
        'List of dates (YYYY-MM-DD ...)')
    args = parser.parse_args()
    if args.date:
        dates = [args.date]
    elif args.range:
        start = datetime.strptime(args.range[0], '%Y-%m-%d')
        end = datetime.strptime(args.range[1], '%Y-%m-%d')
        dates = [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in
            range((end - start).days + 1)]
    elif args.dates:
        dates = args.dates
    else:
        dates = [datetime.now().strftime('%Y-%m-%d')]
    return dates


def is_valid_date(date_str: str) ->bool:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except Exception:
        return False


def render_entry(entry: VelocityLogEntry) ->str:
    if not is_valid_date(entry.date):
        return ''
    s = entry_template
    for k, v in entry.__dict__.items():
        s = s.replace(f'<{k}>', str(v) if v else f'<{k}>')
    s = re.sub('<[^>]+>', '', s)
    if not entry.date or entry.date.strip() == '':
        return ''
    return s


def main() ->None:
    user = get_user()
    dates = parse_args()
    updated = set()
    for iso_date in dates:
        if not is_valid_date(iso_date):
            emit_log_event(LogLevelEnum.WARNING,
                f'Skipping invalid date: {iso_date}',
                context=LogContextModel(calling_module=__name__, calling_function='main', calling_line=__import__('inspect').currentframe().f_lineno, timestamp='auto', node_id=_COMPONENT_NAME),
                node_id=_COMPONENT_NAME, event_bus=self._event_bus)
            continue
        dt = datetime.strptime(iso_date, '%Y-%m-%d')
        monday, sunday = week_bounds(dt)
        week_start = monday.strftime('%Y_%m_%d')
        week_end = sunday.strftime('%Y_%m_%d')
        iso_week_start = monday.strftime('%Y-%m-%d')
        iso_week_end = sunday.strftime('%Y-%m-%d')
        log_dir = Path(f'docs/dev_logs/{user}')
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f'velocity_log_{week_start}-{week_end}.md'
        existing_content = log_path.read_text() if log_path.exists() else ''
        daily_entries = {}
        for m in re.finditer(
            '### (\\d{4}-\\d{2}-\\d{2})\\n(- .+?)(?=\\n###|\\n# Velocity Report:|\\Z)'
            , existing_content, re.DOTALL):
            date, summary = m.group(1), m.group(2).strip()
            if is_valid_date(date):
                daily_entries[date] = VelocityLogEntry(date=date, summary=
                    summary)
        for m in re.finditer(
            '# Velocity Report: .+?\\((\\d{4}-\\d{2}-\\d{2})\\)\\n(.*?)(?=\\n# Velocity Report:|\\Z)'
            , existing_content, re.DOTALL):
            date, raw_report = m.group(1), m.group(2).strip()
            if is_valid_date(date) and date in daily_entries:
                daily_entries[date].raw_report = raw_report
        week_dates = [(monday + timedelta(days=i)).strftime('%Y-%m-%d') for
            i in range(7)]
        for d in week_dates:
            if is_valid_date(d) and d not in daily_entries:
                daily_entries[d] = VelocityLogEntry(date=d)
        for d in dates:
            if not is_valid_date(d):
                continue
            entry = daily_entries[d]
            if not entry.raw_report:
                entry.velocity_log_id = str(uuid.uuid4())
                prev_dates = [date for date in week_dates if date < d and
                    daily_entries[date].raw_report]
                if prev_dates:
                    last_report = daily_entries[prev_dates[-1]]
                    entry.parent_log_id = last_report.velocity_log_id
                lines_changed, files_modified = get_git_stats()
                entry.lines_changed = lines_changed
                entry.files_modified = files_modified
                time_spent, commit_actions = get_commit_info()
                entry.time_spent = time_spent
                entry.prompts_actions = '\n'.join(commit_actions
                    ) if commit_actions else '- <add here>'
                entry.raw_report = ''
                updated.add((log_path, d))
        entries_rendered = []
        for d in week_dates:
            if not is_valid_date(d):
                continue
            entry = daily_entries[d]
            entry_block = f'### {entry.date}\n{entry.summary}\n'
            if d in dates:
                rendered = render_entry(entry)
                if rendered.strip():
                    entry_block += rendered
            elif entry.raw_report:
                entry_block += f"""# Velocity Report: <Short Title> ({entry.date})
{entry.raw_report}
"""
            entries_rendered.append(entry_block)
        log = weekly_template.replace('<YYYY-MM-DD>', iso_week_start, 1
            ).replace('<YYYY-MM-DD>', iso_week_end, 1)
        log = log.replace('<!-- Entries go here -->', '\n'.join(
            entries_rendered))
        log_path.write_text(log)
    if updated:
        emit_log_event(LogLevelEnum.INFO,
            'Updated the following velocity log entries:',
            context=LogContextModel(calling_module=__name__, calling_function='main', calling_line=__import__('inspect').currentframe().f_lineno, timestamp='auto', node_id=_COMPONENT_NAME),
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        for log_path, iso_date in sorted(updated):
            emit_log_event(LogLevelEnum.INFO,
                f'  {log_path} for {iso_date}',
                context=LogContextModel(calling_module=__name__, calling_function='main', calling_line=__import__('inspect').currentframe().f_lineno, timestamp='auto', node_id=_COMPONENT_NAME),
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus)
        emit_log_event(LogLevelEnum.INFO,
            'Please review and fill in all manual fields (e.g., Score, Key Achievements, Milestones, etc.).',
            context=LogContextModel(calling_module=__name__, calling_function='main', calling_line=__import__('inspect').currentframe().f_lineno, timestamp='auto', node_id=_COMPONENT_NAME),
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
    else:
        emit_log_event(LogLevelEnum.INFO,
            'No updates were made. All specified entries already exist.',
            context=LogContextModel(calling_module=__name__, calling_function='main', calling_line=__import__('inspect').currentframe().f_lineno, timestamp='auto', node_id=_COMPONENT_NAME),
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)


if __name__ == '__main__':
    main()
