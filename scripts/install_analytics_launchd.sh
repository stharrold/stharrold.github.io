#!/bin/bash
# Install (or update) the GA4 archive job (scripts/analytics_archive.sh) as a launchd job, at 09:00 and 21:00.
#
#   bash scripts/install_analytics_launchd.sh               # copy the scripts, install the job
#   bash scripts/install_analytics_launchd.sh --print-plist # print the job file, change nothing
#   bash scripts/install_analytics_launchd.sh --run-now     # start the job now
#   bash scripts/install_analytics_launchd.sh --uninstall   # remove the job (the archive on Drive stays)
#
# WHY A COPY: a launchd job cannot read anything under ~/Documents, where the repo lives. So the job runs from
# ~/Library/Application Support/stharrold-analytics/, which this script fills. RE-RUN IT after changing either
# script, or the job keeps running the old copy (the copy's VERSION file records the commit it came from).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/Library/Application Support/stharrold-analytics"
LABEL="io.github.stharrold.analytics-archive"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/stharrold-analytics.log"
DOMAIN="gui/$(id -u)"
FILES=(scripts/analytics_archive.py scripts/analytics_archive.sh)

plist() {
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$DEST/scripts/analytics_archive.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
$(for h in 9 21; do printf '        <dict>\n            <key>Hour</key>\n            <integer>%s</integer>\n            <key>Minute</key>\n            <integer>0</integer>\n        </dict>\n' "$h"; done)
    </array>
    <key>StandardOutPath</key>
    <string>$LOG</string>
    <key>StandardErrorPath</key>
    <string>$LOG</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF
}

case "${1:-}" in
  --print-plist)
    plist
    exit 0
    ;;
  --run-now)
    launchctl kickstart "$DOMAIN/$LABEL"
    echo "started $LABEL; follow it with: tail -f \"$LOG\""
    exit 0
    ;;
  --uninstall)
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    echo "removed $LABEL (the archive on Google Drive stays)"
    exit 0
    ;;
  "") ;;
  *)
    sed -n '2,7p' "$0"
    exit 2
    ;;
esac

mkdir -p "$DEST/scripts" "$(dirname "$PLIST")" "$(dirname "$LOG")"
for f in "${FILES[@]}"; do
  cp "$REPO/$f" "$DEST/$f"
done
git -C "$REPO" rev-parse HEAD > "$DEST/VERSION"

plist > "$PLIST"
plutil -lint "$PLIST" >/dev/null
launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST"
echo "installed $LABEL from $(cut -c1-7 "$DEST/VERSION"): runs at 09:00 and 21:00, archives every settled day not yet on Drive"
echo "  copy: $DEST"
echo "  log:  $LOG"
