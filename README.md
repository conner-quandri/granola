# Granola Meeting Notes Extractor

A Python script to extract and organize meeting notes from [Granola](https://granola.ai)'s cache file into individual markdown files organized by date.

## Features

- 📝 **Rich Content Extraction**: Pulls actual meeting content from Granola's internal cache
- 📁 **Date Organization**: Organizes meetings into `~/granola-notes/YYYY-MM-DD/` directories
- 📄 **Individual Files**: Each meeting becomes its own markdown file
- 🔄 **Multiple Formats**: Support for JSON and Markdown output
- ⏰ **Cron Job Ready**: Easy automation with included setup script
- 🛡️ **Safe Filenames**: Automatically sanitizes meeting titles for filesystem compatibility
- 🔍 **Duplicate Handling**: Handles meetings with identical titles by adding timestamps
- 👥 **Multi-User Support**: Works for any Mac user with automatic path detection

## Installation

### Prerequisites

- macOS with Granola app installed
- Python 3.6+ (pre-installed on macOS)
- Meeting data in Granola (at least one meeting recorded)

### Setup

1. **Clone or download this repository:**
   ```bash
   git clone https://github.com/becevior/granola.git
   cd granola
   ```

2. **Make the script executable:**
   ```bash
   chmod +x extract_meeting_notes.py setup_cron.sh
   ```

3. **Test the extraction:**
   ```bash
   python3 extract_meeting_notes.py
   ```
   This will create a `~/granola-notes/` directory with your meetings organized by date.

## Quick Start

### Basic Usage

```bash
# Extract all meetings to ~/granola-notes/ directory
python3 extract_meeting_notes.py

# Custom output directory
python3 extract_meeting_notes.py --output-dir ~/my-meetings

# Legacy mode (single file output)
python3 extract_meeting_notes.py --legacy-mode --format markdown --output all_meetings.md
```

### Set Up Automated Extraction

```bash
# Set up cron job to run every 5 minutes
./setup_cron.sh
```

## Directory Structure

The script creates the following structure in your home directory:

```
~/granola-notes/
├── 2025-08-15/
│   └── AI Sports broadcaster concept development.md
├── 2025-07-09/
│   ├── Drug policy pipeline update with Sanket and Ben.md
│   └── Another meeting from same day.md
└── 2025-06-23/
    ├── Meta startup program interview with Azadeh.md
    ├── PyTorch Q&A system design planning.md
    └── Weekly engineering roadmap review.md
```

## Command Line Options

```bash
python3 extract_meeting_notes.py [OPTIONS]

Options:
  --cache-path PATH     Path to Granola cache file 
                       (default: ~/Library/Application Support/Granola/cache-v3.json)
  --output-dir DIR      Base directory for organized meeting files 
                       (default: ~/granola-notes)
  --legacy-mode        Use legacy output format (single file or stdout)
  --format FORMAT      Output format for legacy mode: json|markdown 
                       (default: markdown)
  --output FILE        Output file for legacy mode (prints to stdout if not specified)
```

## Meeting File Format

Each meeting file contains:

- **Meeting metadata**: Title, creation date, update date, ID
- **Meeting content**: All structured notes from Granola panels
- **Participants**: Creator and attendees
- **Rich formatting**: Headings, bullet points, and other markdown elements

Example:

```markdown
# AI Sports broadcaster concept development

**Created:** 2025-08-15 21:13:10
**Updated:** 2025-08-19 19:44:29
**ID:** 5dcb42d3-07dc-490f-abd7-068888bd3b9c

## Meeting Content

### Summary

- Developing YC application for AI-powered personalized sports commentary platform
- Core value proposition: compete with Instagram/TikTok-style sports content

### Current Sports Media Pain Points

- ESPN/SportsCenter viewing experience widely disliked
- Consumption fragmented across platforms (TikTok, reels, YouTube, Twitter, Reddit)

## Participants

- Conner (creator)
```

## Automation

### Cron Job Setup

The included `setup_cron.sh` script sets up automatic extraction every 5 minutes:

```bash
./setup_cron.sh
```

### Manual Cron Configuration

To set up manually or customize timing:

```bash
# Edit cron jobs
crontab -e

# Add this line for every 5 minutes (replace /path/to/script with actual path):
*/5 * * * * /usr/bin/python3 "/path/to/extract_meeting_notes.py" --output-dir "$HOME/granola-notes" >> "/path/to/cron.log" 2>&1

# Other timing examples:
# Every hour:     0 * * * *
# Every 30 min:   */30 * * * *
# Daily at 9 AM:  0 9 * * *
```

**Note**: The setup script automatically handles path detection, so it's recommended to use `./setup_cron.sh` instead of manual configuration.

### Managing Cron Jobs

```bash
# View current cron jobs
crontab -l

# Check extraction logs
tail -f cron.log

# Remove the cron job
crontab -l | grep -v 'extract_meeting_notes.py' | crontab -
```

## Requirements

- Python 3.6+
- Granola app installed with meetings in cache
- Standard library only (no additional dependencies)

## How It Works

1. **Cache Reading**: Reads Granola's `cache-v3.json` file containing meeting data
2. **Content Parsing**: Extracts rich content from `documentPanels` structure
3. **Format Conversion**: Converts Granola's internal format to readable markdown
4. **File Organization**: Creates date-based directory structure
5. **Safe Writing**: Handles filename conflicts and special characters

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