# Granola Meeting Notes Extraction & Summarization

Automated system to extract meeting notes from Granola and generate AI-powered summaries at daily, weekly, and monthly intervals. Includes integration with Linear for generating project updates.

## Features

### Extraction
- 📝 **Rich Content Extraction**: Pulls meeting content, metadata, and raw transcripts from Granola's cache
- 📁 **Date Organization**: Organizes meetings into `daily_outputs/YYYY-MM-DD/` directories
- 📄 **Individual Files**: Each meeting becomes its own markdown file
- 🔄 **Multiple Formats**: Support for JSON and Markdown output
- 🛡️ **Safe Filenames**: Automatically sanitizes meeting titles for filesystem compatibility
- 👥 **Multi-User Support**: Works for any Mac user with automatic path detection

### Summarization
- 🤖 **AI-Powered Summaries**: Uses Claude API to generate intelligent summaries
- 📊 **Daily Summaries**: Key themes, action items, and decisions from each day
- 📈 **Weekly Summaries**: Aggregated insights and patterns across the week
- 📅 **Monthly Summaries**: Strategic overview and trends for the month
- 💾 **Smart State Tracking**: Only processes new data, avoiding unnecessary reprocessing
- ⏰ **Automated Scheduling**: Optional setup for hands-free daily execution

### Project Updates (with Linear Integration)
- 🎯 **Linear Integration**: Automatically pulls project and ticket data from Linear
- 📈 **Accurate Progress Tracking**: Calculates completion percentages from actual ticket status
- 📝 **Meeting Notes Integration**: Incorporates strategic context from extracted meeting notes
- 🔄 **Initiative-Level Updates**: Generates both project-level and initiative-level updates
- 📋 **Template-Based Generation**: Uses customizable templates for consistent formatting
- ✅ **Validation & Quality Checks**: Built-in quality checklist ensures accurate reporting

## Installation

### Prerequisites

- macOS with Granola app installed
- Python 3.6+ (pre-installed on macOS)
- Meeting data in Granola (at least one meeting recorded)
- Anthropic API key (for summarization features)

### Setup

1. **Clone or download this repository:**
   ```bash
   git clone https://github.com/becevior/granola.git
   cd granola
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key (for summarization):**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   # Add to shell profile for persistence
   echo "export ANTHROPIC_API_KEY='your-api-key-here'" >> ~/.zshrc
   ```

4. **Test the extraction:**
   ```bash
   python3 extract_meeting_notes.py
   ```
   This will create a `daily_outputs/` directory with your meetings organized by date.

## Quick Start

### Step 1: Extract Meeting Notes

```bash
# Extract all meetings to daily_outputs/ directory
python3 extract_meeting_notes.py

# Custom output directory
python3 extract_meeting_notes.py --output-dir ~/my-meetings

# Legacy mode (single file output)
python3 extract_meeting_notes.py --legacy-mode --format markdown --output all_meetings.md
```

### Step 2: Generate Summaries

```bash
# Generate all summaries (daily, weekly, monthly)
python3 summarize_meetings.py --type all

# Or generate specific types
python3 summarize_meetings.py --type daily
python3 summarize_meetings.py --type weekly
python3 summarize_meetings.py --type monthly
```

### Step 3: Set Up Automated Execution (Optional)

```bash
# Set up automated daily summarization
./setup_scheduling.sh
```

### Step 4: Generate Project Updates (Optional, requires Linear MCP)

Use Claude Code with the Linear MCP server to generate project updates:

1. See `prompts/generate_project_updates.md` for detailed instructions
2. The prompt integrates Linear project/ticket data with extracted meeting notes
3. Outputs go to `project_updates/` directory
4. Supports both project-level and initiative-level updates

## Directory Structure

The system creates the following structure:

```
granola/
├── daily_outputs/                     # Extracted meeting notes
│   ├── 2025-10-14/
│   │   ├── Meeting1.md
│   │   └── Meeting2.md
│   └── 2025-10-15/
│       └── Meeting3.md
├── summaries/                         # Generated summaries
│   ├── daily/
│   │   ├── 2025-10-14_summary.md
│   │   └── 2025-10-15_summary.md
│   ├── weekly/
│   │   └── 2025-W42_summary.md
│   └── monthly/
│       └── 2025-10_summary.md
├── project_updates/                   # Generated project updates
│   ├── initiative_update_*.md
│   └── *_update_YYYY-MM-DD.md
├── prompts/                           # Reusable prompts and templates
│   └── generate_project_updates.md
├── templates/                         # Output templates
│   └── project_update.md
├── .summarization_state.json          # Tracks processed dates
├── extract_meeting_notes.py
├── summarize_meetings.py
├── setup_scheduling.sh
└── requirements.txt
```

## Command Line Options

### Extraction (`extract_meeting_notes.py`)

```bash
python3 extract_meeting_notes.py [OPTIONS]

Options:
  --cache-path PATH     Path to Granola cache file
                       (default: ~/Library/Application Support/Granola/cache-v3.json)
  --output-dir DIR      Base directory for organized meeting files
                       (default: ./daily_outputs)
  --legacy-mode        Use legacy output format (single file or stdout)
  --format FORMAT      Output format for legacy mode: json|markdown
                       (default: markdown)
  --output FILE        Output file for legacy mode (prints to stdout if not specified)
```

### Summarization (`summarize_meetings.py`)

```bash
python3 summarize_meetings.py [OPTIONS]

Options:
  --type TYPE          Type of summary: daily|weekly|monthly|all (default: daily)
  --notes-dir DIR      Directory containing meeting notes (default: ./daily_outputs)
  --summaries-dir DIR  Directory to write summaries (default: ./summaries)
  --state-file FILE    State file for tracking (default: ./.summarization_state.json)
  --force              Force reprocessing of already processed dates
  --date DATE          Specific date to process (YYYY-MM-DD, daily only)
  --model MODEL        Anthropic model to use (default: claude-3-5-sonnet-20241022)
```

## File Formats

### Meeting Notes Format

Each extracted meeting file contains:

- **Meeting metadata**: Title, creation date, update date, ID
- **Meeting content**: All structured notes from Granola panels
- **Participants**: Creator and attendees
- **Raw transcript**: Timestamped conversation with speaker labels
- **Rich formatting**: Headings, bullet points, and other markdown elements

Example:

```markdown
# Meeting Title

**Created:** 2025-10-14 19:00:22
**Updated:** 2025-10-15 16:39:41
**ID:** abc123def-4567-8901-2345-678901234567

## Meeting Content

### Summary
[AI-generated summary from Granola]

## Participants
- John Doe (creator)
- Jane Smith

## Raw Transcript

**[19:00:33] You:** Hello everyone
**[19:00:35] Other:** Hi there
```

### Summary Format

Generated summaries include:

- **Daily**: Executive summary, key themes, action items, decisions, participants, topics
- **Weekly**: Major themes, project progress, consolidated action items, meeting patterns
- **Monthly**: Strategic overview, milestones, time allocation, recurring patterns, trends

## Automation

### Automated Summarization Setup (macOS)

The included `setup_scheduling.sh` script configures automatic daily execution:

```bash
./setup_scheduling.sh
```

This sets up a launchd agent that runs daily at 11:59 PM and processes:
- New daily summaries
- Complete weeks (weekly summaries)
- Complete months (monthly summaries)

**Management commands:**
```bash
# Run summarization now (test)
launchctl start com.granola.summarize

# Stop/disable automatic execution
launchctl unload ~/Library/LaunchAgents/com.granola.summarize.plist

# Re-enable automatic execution
launchctl load ~/Library/LaunchAgents/com.granola.summarize.plist

# Check status
launchctl list | grep granola

# View logs
tail -f summarization.log
tail -f summarization_error.log
```

### Manual Execution

Run extraction and summarization whenever you want:

```bash
# Step 1: Extract latest meetings
python3 extract_meeting_notes.py

# Step 2: Generate summaries
python3 summarize_meetings.py --type all
```

## Requirements

### Extraction
- Python 3.6+
- Granola app installed with meetings in cache
- Standard library only (no additional dependencies)

### Summarization
- Python 3.6+
- `anthropic` package (see requirements.txt)
- Anthropic API key
- Estimated cost: ~$6/month for daily use

## Project Updates Generation

The project updates feature integrates Linear project management data with meeting notes to generate comprehensive status updates.

### Overview

This feature uses Claude Code with the Linear MCP server to:
- Query Linear for projects and tickets in specific initiatives
- Calculate accurate completion percentages based on ticket status
- Incorporate strategic context from meeting notes
- Generate formatted project updates and initiative-level summaries

### Requirements

- Claude Code CLI installed
- Linear MCP server configured
- Meeting notes extracted in `daily_outputs/` directory
- Template file in `templates/project_update.md`

### Usage

1. Open the prompt file:
   ```bash
   cat prompts/generate_project_updates.md
   ```

2. In Claude Code, provide the initiative name:
   ```
   Generate updates for initiative: "Intelligence Q4 2025 - Accuracy Explainability"
   ```

3. Claude Code will:
   - Query Linear for all projects in the initiative
   - Pull relevant meeting notes from `daily_outputs/`
   - Calculate completion percentages from ticket status
   - Generate individual project update files
   - Create initiative-level summary

### Output Format

**Project Updates** (`project_updates/*_update_YYYY-MM-DD.md`):
- Overview with status and progress percentage
- What was done (completed tickets)
- What needs to be done (in progress/todo tickets)
- Blockers and risks
- Key metrics with ticket breakdown
- Learnings from meeting notes

**Initiative Updates** (`project_updates/initiative_update_*_YYYY-MM-DD.md`):
- Executive summary with overall health
- Project status table
- Key accomplishments
- Active blockers and risks
- Strategic context from meetings
- Decisions needed and help requested

### Key Features

- **Accurate Completion Tracking**: Calculates `(Released tickets / Total tickets) * 100`
- **Meeting Notes Integration**: Automatically finds and incorporates relevant meeting insights
- **Quality Validation**: Built-in checklist ensures accuracy and completeness
- **Template-Based**: Uses customizable templates for consistent formatting
- **Ticket References**: All work items include Linear ticket IDs for traceability

See `prompts/generate_project_updates.md` for detailed instructions and guidelines.

## How It Works

### Extraction Process

1. **Cache Reading**: Reads Granola's `cache-v3.json` file containing meeting data
2. **Content Parsing**: Extracts rich content from `documentPanels` and `transcripts`
3. **Format Conversion**: Converts Granola's internal format to readable markdown
4. **File Organization**: Creates date-based directory structure
5. **Safe Writing**: Handles filename conflicts and special characters

### Summarization Process

1. **State Check**: Reads `.summarization_state.json` to identify unprocessed dates
2. **Data Aggregation**: Collects meeting notes for the target period (day/week/month)
3. **LLM Processing**: Sends to Claude API with structured prompts
4. **Summary Generation**: Receives formatted markdown summaries with key insights
5. **State Update**: Marks period as processed to avoid reprocessing
6. **Hierarchical Flow**: Daily → Weekly → Monthly summaries build on each other

## Troubleshooting

### Common Issues

- **Cache file not found**: 
  - Ensure Granola is installed and has meeting data
  - Check if cache exists: `ls ~/Library/Application\ Support/Granola/cache-v3.json`
  - Try recording a test meeting in Granola first

- **Permission errors**: 
  - Make sure the script has write access to output directory
  - Check that `~/granola-notes` is writable: `ls -la ~/granola-notes`

- **Cron job not running**: 
  - Verify cron service is running: `sudo launchctl list | grep cron`
  - Check cron logs in the script directory
  - Ensure absolute paths are used in cron entries

- **Different user setup**:
  - Each user needs to run the setup on their own account
  - Cache paths are user-specific (`~/Library/Application Support/Granola/`)
  - Output goes to each user's home directory (`~/granola-notes/`)

### Debugging

```bash
# Test the script manually
python3 extract_meeting_notes.py

# Check if Granola cache exists
ls -la ~/Library/Application\ Support/Granola/

# Check cron logs (in script directory)
tail -f cron.log

# Verify cron job is scheduled
crontab -l

# Test with verbose output
python3 extract_meeting_notes.py --output-dir ~/test-granola
```

### For System Administrators

To deploy this for multiple users:

1. Each user should clone/download the repository to their own directory
2. Each user runs `./setup_cron.sh` from their copy
3. Outputs go to each user's `~/granola-notes/` directory
4. Cron jobs run under each user's account with their permissions

## License

MIT License - Feel free to modify and distribute as needed.