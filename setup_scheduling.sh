#!/bin/bash
# Setup script for scheduling meeting summarization
# This creates a launchd configuration for macOS to run summarization automatically

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCHD_DIR/com.granola.summarize.plist"

echo "🔧 Granola Meeting Summarization Scheduler Setup"
echo "================================================"
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY environment variable is not set"
    echo "   The scheduler will need this to work properly."
    echo ""
    read -p "Enter your Anthropic API key (or press Enter to skip): " api_key
    if [ -n "$api_key" ]; then
        echo "export ANTHROPIC_API_KEY='$api_key'" >> ~/.zshrc
        echo "✓ API key added to ~/.zshrc"
        export ANTHROPIC_API_KEY="$api_key"
    fi
    echo ""
fi

# Create launchd directory if it doesn't exist
mkdir -p "$LAUNCHD_DIR"

# Create plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.granola.summarize</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_DIR/summarize_meetings.py</string>
        <string>--type</string>
        <string>all</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>ANTHROPIC_API_KEY</key>
        <string>$ANTHROPIC_API_KEY</string>
    </dict>

    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/summarization.log</string>

    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/summarization_error.log</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>23</integer>
        <key>Minute</key>
        <integer>59</integer>
    </dict>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

echo "✓ Created launchd plist file at:"
echo "  $PLIST_FILE"
echo ""

# Load the agent
echo "Loading launchd agent..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Launchd agent loaded successfully"
else
    echo "✗ Failed to load launchd agent"
    exit 1
fi

echo ""
echo "📅 Scheduling Configuration:"
echo "  - Runs daily at 11:59 PM"
echo "  - Processes all new daily/weekly/monthly summaries"
echo "  - Logs to: $SCRIPT_DIR/summarization.log"
echo ""
echo "Management commands:"
echo "  • Unload (disable): launchctl unload \"$PLIST_FILE\""
echo "  • Load (enable):    launchctl load \"$PLIST_FILE\""
echo "  • Run now:          launchctl start com.granola.summarize"
echo "  • Check status:     launchctl list | grep granola"
echo ""
echo "Manual execution:"
echo "  • Daily:   python3 $SCRIPT_DIR/summarize_meetings.py --type daily"
echo "  • Weekly:  python3 $SCRIPT_DIR/summarize_meetings.py --type weekly"
echo "  • Monthly: python3 $SCRIPT_DIR/summarize_meetings.py --type monthly"
echo "  • All:     python3 $SCRIPT_DIR/summarize_meetings.py --type all"
echo ""
echo "✅ Setup complete!"
