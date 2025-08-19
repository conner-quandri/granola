#!/bin/bash

# Setup script for Granola meeting notes cron job
# This will extract meeting notes every hour

echo "Setting up cron job for Granola meeting notes extraction..."

# Define paths
SCRIPT_PATH="/Users/beckwith/workplace/granola/extract_meeting_notes.py"
OUTPUT_DIR="/Users/beckwith/workplace/granola/daily_outputs"
LOG_FILE="/Users/beckwith/workplace/granola/cron.log"

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