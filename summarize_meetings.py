#!/usr/bin/python3
"""
Script to generate summaries of meeting notes using LLM.
Supports daily, weekly, and monthly summaries with state tracking to avoid reprocessing.

Usage:
    python summarize_meetings.py --type daily
    python summarize_meetings.py --type weekly
    python summarize_meetings.py --type monthly
    python summarize_meetings.py --type all
    python summarize_meetings.py --type daily --force --date 2025-10-14
"""

import json
import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file (override existing variables)
load_dotenv(override=True)

# Configuration
DEFAULT_NOTES_DIR = Path(__file__).parent / "daily_outputs"
DEFAULT_SUMMARIES_DIR = Path(__file__).parent / "summaries"
DEFAULT_STATE_FILE = Path(__file__).parent / ".summarization_state.json"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

class StateManager:
    """Manages tracking of processed dates/periods."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from file or create new state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse state file, creating new one")
                return {"daily": [], "weekly": [], "monthly": []}
        return {"daily": [], "weekly": [], "monthly": []}

    def _save_state(self):
        """Save state to file."""
        self.state_file.parent.mkdir(exist_ok=True, parents=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def is_processed(self, identifier: str, summary_type: str) -> bool:
        """Check if identifier has been processed."""
        return identifier in self.state.get(summary_type, [])

    def mark_processed(self, identifier: str, summary_type: str):
        """Mark identifier as processed."""
        if summary_type not in self.state:
            self.state[summary_type] = []
        if identifier not in self.state[summary_type]:
            self.state[summary_type].append(identifier)
            self.state[summary_type].sort()
            self._save_state()

class MeetingSummarizer:
    """Generates summaries of meeting notes using Anthropic Claude."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def _call_claude(self, prompt: str, max_tokens: int = 4000) -> str:
        """Make API call to Claude."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise

    def summarize_daily(self, date: str, meetings: List[Dict]) -> str:
        """Generate daily summary from meeting notes."""
        # Aggregate meeting content
        meeting_texts = []
        for meeting in meetings:
            meeting_texts.append(f"## {meeting['title']}\n\n{meeting['content']}\n")

        aggregated = "\n---\n\n".join(meeting_texts)

        prompt = f"""Analyze the following meeting notes from {date} and create a comprehensive daily summary.

Meeting Notes:
{aggregated}

Please provide:

1. **Executive Summary** (2-3 sentences capturing the essence of the day)

2. **Key Themes** (3-5 main topics that emerged across meetings)

3. **Action Items** (extract specific action items with owners if identifiable)

4. **Important Decisions** (list any decisions made)

5. **People Involved** (key participants across all meetings)

6. **Topics & Projects Discussed** (categorize by area/project with brief notes)

7. **Meeting Investment** (estimate total time spent in meetings: {len(meetings)} meetings)

Format the output as clear, well-structured markdown. Be concise but comprehensive."""

        return self._call_claude(prompt)

    def summarize_weekly(self, week_id: str, date_range: str, daily_summaries: List[str]) -> str:
        """Generate weekly summary from daily summaries."""
        aggregated = "\n\n---\n\n".join(daily_summaries)

        prompt = f"""Analyze the following daily summaries from week {week_id} ({date_range})
and create a comprehensive weekly summary.

Daily Summaries:
{aggregated}

Please provide:

1. **Executive Summary** (3-4 sentences capturing the week's highlights)

2. **Major Themes** (key themes that emerged throughout the week)

3. **Progress on Projects/Initiatives** (what moved forward, what stalled)

4. **Key Action Items** (consolidated and prioritized action items for the week)

5. **Meeting Load Analysis** (patterns in meeting frequency and types)

6. **Cross-Meeting Insights** (connections or patterns across different meetings)

7. **Week in Review** (notable wins, challenges, or observations)

Format as clear, well-structured markdown with an emphasis on strategic insights."""

        return self._call_claude(prompt)

    def summarize_monthly(self, month: str, weekly_summaries: List[str]) -> str:
        """Generate monthly summary from weekly summaries."""
        aggregated = "\n\n---\n\n".join(weekly_summaries)

        prompt = f"""Analyze the following weekly summaries from {month}
and create a comprehensive monthly summary.

Weekly Summaries:
{aggregated}

Please provide:

1. **Executive Summary** (4-5 sentences capturing the month's narrative)

2. **Strategic Themes** (overarching themes for the month)

3. **Major Milestones & Decisions** (key achievements and strategic decisions)

4. **Time Allocation Analysis** (how time was distributed across topics/projects)

5. **Recurring Patterns** (what consistently came up throughout the month)

6. **Month-over-Month Trends** (if discernible from the data)

7. **Looking Ahead** (implied priorities or focus areas for next month based on patterns)

Format as executive-level markdown summary focused on strategic insights and patterns."""

        return self._call_claude(prompt)

def get_meeting_files(date_dir: Path) -> List[Dict]:
    """Read all meeting files from a date directory."""
    meetings = []

    if not date_dir.exists():
        return meetings

    for file_path in sorted(date_dir.glob("*.md")):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Extract title from first line
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines else file_path.stem

                meetings.append({
                    'title': title,
                    'content': content,
                    'file': file_path.name
                })
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")

    return meetings

def get_available_dates(notes_dir: Path) -> List[str]:
    """Get all available date directories."""
    dates = []
    if not notes_dir.exists():
        return dates

    for item in notes_dir.iterdir():
        if item.is_dir() and re.match(r'\d{4}-\d{2}-\d{2}$', item.name):
            dates.append(item.name)

    return sorted(dates)

def get_week_id(date_str: str) -> str:
    """Convert date to ISO week format (YYYY-Wxx)."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%Y-W%U")

def get_week_dates(week_id: str, available_dates: List[str]) -> List[str]:
    """Get all dates that belong to a given week."""
    dates_in_week = []
    for date_str in available_dates:
        if get_week_id(date_str) == week_id:
            dates_in_week.append(date_str)
    return dates_in_week

def get_month_id(date_str: str) -> str:
    """Convert date to month format (YYYY-MM)."""
    return date_str[:7]

def process_daily_summaries(
    notes_dir: Path,
    summaries_dir: Path,
    state_manager: StateManager,
    summarizer: MeetingSummarizer,
    force: bool = False,
    specific_date: Optional[str] = None
):
    """Process daily summaries for unprocessed dates."""
    daily_dir = summaries_dir / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)

    available_dates = get_available_dates(notes_dir)

    if specific_date:
        dates_to_process = [specific_date] if specific_date in available_dates else []
        if not dates_to_process:
            print(f"Error: Date {specific_date} not found in {notes_dir}")
            return
    else:
        dates_to_process = [
            d for d in available_dates
            if force or not state_manager.is_processed(d, 'daily')
        ]

    if not dates_to_process:
        print("No new dates to process for daily summaries")
        return

    print(f"Processing {len(dates_to_process)} daily summaries...")

    for date in dates_to_process:
        print(f"  Processing {date}...", end=' ')

        date_dir = notes_dir / date
        meetings = get_meeting_files(date_dir)

        if not meetings:
            print("No meetings found, skipping")
            continue

        try:
            summary = summarizer.summarize_daily(date, meetings)

            # Write summary
            output_file = daily_dir / f"{date}_summary.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Daily Summary: {date}\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Meetings:** {len(meetings)}\n\n")
                f.write("---\n\n")
                f.write(summary)

            state_manager.mark_processed(date, 'daily')
            print(f"✓ ({len(meetings)} meetings)")

        except Exception as e:
            print(f"✗ Error: {e}")

def process_weekly_summaries(
    summaries_dir: Path,
    notes_dir: Path,
    state_manager: StateManager,
    summarizer: MeetingSummarizer,
    force: bool = False
):
    """Process weekly summaries for unprocessed weeks."""
    weekly_dir = summaries_dir / "weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)

    daily_dir = summaries_dir / "daily"

    # Get all available daily summaries
    available_dates = get_available_dates(notes_dir)

    # Group by week
    weeks = {}
    for date in available_dates:
        week_id = get_week_id(date)
        if week_id not in weeks:
            weeks[week_id] = []
        weeks[week_id].append(date)

    # Find weeks to process
    weeks_to_process = []
    for week_id, dates in sorted(weeks.items()):
        # Check if all daily summaries exist for this week
        all_daily_exist = all(
            (daily_dir / f"{date}_summary.md").exists()
            for date in dates
        )

        if not all_daily_exist:
            continue

        if force or not state_manager.is_processed(week_id, 'weekly'):
            weeks_to_process.append((week_id, dates))

    if not weeks_to_process:
        print("No new weeks to process for weekly summaries")
        return

    print(f"Processing {len(weeks_to_process)} weekly summaries...")

    for week_id, dates in weeks_to_process:
        date_range = f"{dates[0]} to {dates[-1]}"
        print(f"  Processing {week_id} ({date_range})...", end=' ')

        # Read daily summaries
        daily_summaries = []
        for date in dates:
            summary_file = daily_dir / f"{date}_summary.md"
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    daily_summaries.append(f.read())
            except Exception as e:
                print(f"✗ Error reading {summary_file}: {e}")
                continue

        if not daily_summaries:
            print("No daily summaries found, skipping")
            continue

        try:
            summary = summarizer.summarize_weekly(week_id, date_range, daily_summaries)

            # Write summary
            output_file = weekly_dir / f"{week_id}_summary.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Weekly Summary: {week_id}\n\n")
                f.write(f"**Date Range:** {date_range}\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(summary)

            state_manager.mark_processed(week_id, 'weekly')
            print(f"✓ ({len(daily_summaries)} days)")

        except Exception as e:
            print(f"✗ Error: {e}")

def process_monthly_summaries(
    summaries_dir: Path,
    notes_dir: Path,
    state_manager: StateManager,
    summarizer: MeetingSummarizer,
    force: bool = False
):
    """Process monthly summaries for unprocessed months."""
    monthly_dir = summaries_dir / "monthly"
    monthly_dir.mkdir(parents=True, exist_ok=True)

    weekly_dir = summaries_dir / "weekly"

    # Get all available dates and group by month
    available_dates = get_available_dates(notes_dir)

    months = {}
    for date in available_dates:
        month_id = get_month_id(date)
        week_id = get_week_id(date)

        if month_id not in months:
            months[month_id] = set()
        months[month_id].add(week_id)

    # Find months to process
    months_to_process = []
    for month_id, week_ids in sorted(months.items()):
        # Check if all weekly summaries exist for this month
        all_weekly_exist = all(
            (weekly_dir / f"{week_id}_summary.md").exists()
            for week_id in week_ids
        )

        if not all_weekly_exist:
            continue

        if force or not state_manager.is_processed(month_id, 'monthly'):
            months_to_process.append((month_id, sorted(week_ids)))

    if not months_to_process:
        print("No new months to process for monthly summaries")
        return

    print(f"Processing {len(months_to_process)} monthly summaries...")

    for month_id, week_ids in months_to_process:
        print(f"  Processing {month_id}...", end=' ')

        # Read weekly summaries
        weekly_summaries = []
        for week_id in week_ids:
            summary_file = weekly_dir / f"{week_id}_summary.md"
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    weekly_summaries.append(f.read())
            except Exception as e:
                print(f"✗ Error reading {summary_file}: {e}")
                continue

        if not weekly_summaries:
            print("No weekly summaries found, skipping")
            continue

        try:
            summary = summarizer.summarize_monthly(month_id, weekly_summaries)

            # Write summary
            output_file = monthly_dir / f"{month_id}_summary.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Monthly Summary: {month_id}\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(summary)

            state_manager.mark_processed(month_id, 'monthly')
            print(f"✓ ({len(weekly_summaries)} weeks)")

        except Exception as e:
            print(f"✗ Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='Generate summaries of meeting notes using LLM'
    )
    parser.add_argument(
        '--type',
        choices=['daily', 'weekly', 'monthly', 'all'],
        default='daily',
        help='Type of summary to generate (default: daily)'
    )
    parser.add_argument(
        '--notes-dir',
        type=Path,
        default=DEFAULT_NOTES_DIR,
        help='Directory containing meeting notes'
    )
    parser.add_argument(
        '--summaries-dir',
        type=Path,
        default=DEFAULT_SUMMARIES_DIR,
        help='Directory to write summaries'
    )
    parser.add_argument(
        '--state-file',
        type=Path,
        default=DEFAULT_STATE_FILE,
        help='State file for tracking processed dates'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reprocessing of already processed dates'
    )
    parser.add_argument(
        '--date',
        help='Specific date to process (YYYY-MM-DD, only for daily summaries)'
    )
    parser.add_argument(
        '--model',
        default=DEFAULT_MODEL,
        help='Anthropic model to use'
    )

    args = parser.parse_args()

    # Initialize components
    try:
        state_manager = StateManager(args.state_file)
        summarizer = MeetingSummarizer(model=args.model)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set ANTHROPIC_API_KEY environment variable:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Process based on type
    if args.type in ['daily', 'all']:
        process_daily_summaries(
            args.notes_dir,
            args.summaries_dir,
            state_manager,
            summarizer,
            args.force,
            args.date
        )

    if args.type in ['weekly', 'all']:
        process_weekly_summaries(
            args.summaries_dir,
            args.notes_dir,
            state_manager,
            summarizer,
            args.force
        )

    if args.type in ['monthly', 'all']:
        process_monthly_summaries(
            args.summaries_dir,
            args.notes_dir,
            state_manager,
            summarizer,
            args.force
        )

    print("\nSummarization complete!")

if __name__ == '__main__':
    main()
