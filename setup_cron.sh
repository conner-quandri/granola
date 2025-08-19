#!/bin/bash

# Setup script for Granola meeting notes cron job
# This will extract meeting notes every 5 minutes

echo "Setting up cron job for Granola meeting notes extraction..."

# Get current user and script directory
CURRENT_USER=$(whoami)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/extract_meeting_notes.py"

# Define user-specific paths
HOME_DIR="$HOME"
OUTPUT_DIR="$SCRIPT_DIR/daily_outputs"
LOG_FILE="$SCRIPT_DIR/cron.log"

echo "User: $CURRENT_USER"
echo "Script location: $SCRIPT_PATH"
echo "Output directory: $OUTPUT_DIR"
echo "Log file: $LOG_FILE"
echo ""

# Validate script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    echo "Please ensure you're running this from the correct directory."
    exit 1
fi

# Check if Granola cache exists
GRANOLA_CACHE="$HOME_DIR/Library/Application Support/Granola/cache-v3.json"
if [ ! -f "$GRANOLA_CACHE" ]; then
    echo "Warning: Granola cache file not found at:"
    echo "  $GRANOLA_CACHE"
    echo "Please ensure Granola is installed and has meeting data."
    echo ""
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Create the cron job entry
CRON_JOB="*/5 * * * * /usr/bin/python3 \"$SCRIPT_PATH\" --output-dir \"$OUTPUT_DIR\" >> \"$LOG_FILE\" 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "extract_meeting_notes.py"; then
    echo "Cron job already exists. Current crontab:"
    crontab -l | grep "extract_meeting_notes.py"
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added successfully!"
    echo "Schedule: Every 5 minutes"
    echo "Script: $SCRIPT_PATH"
    echo "Output: $OUTPUT_DIR"
    echo "Logs: $LOG_FILE"
fi

echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To edit cron jobs:"
echo "  crontab -e"
echo ""
echo "To remove this cron job:"
echo "  crontab -l | grep -v 'extract_meeting_notes.py' | crontab -"