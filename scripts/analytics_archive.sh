#!/bin/bash
# The GA4 archive job (scripts/analytics_archive.py), as launchd runs it: twice a day, FROM A COPY in
# ~/Library/Application Support/stharrold-analytics/, because a launchd job cannot read ~/Documents, where the repo
# lives (the same macOS privacy rule as aerzeit's analytics pull). scripts/install_analytics_launchd.sh makes the copy.
#
# Each run archives whatever is due, so a Mac that was off catches up at the next run; most runs archive nothing
# and stay quiet. With no network it skips quietly until the last success is ALERT_DAYS old: BigQuery still holds
# the data, so being offline loses nothing until the export itself is lost. The Python script posts its own
# notifications (archived, check needed, failed, exit 1); any other non-zero exit is a crash before it started
# (uv could not install the dependencies, say) and is reported here, never treated as "nothing to do".
set -uo pipefail

HOME_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$HOME_DIR/last-success"
ALERT_DAYS="${ALERT_DAYS:-7}"
LOG_HINT="$HOME/Library/Logs/stharrold-analytics.log"

notify() {
  osascript -e "display notification \"$2\" with title \"$1\"" >/dev/null 2>&1 || true
}

# Any HTTP answer means the network is up (-I headers only; no -f, BigQuery's root answers 404).
if ! curl -sI -o /dev/null -m 20 https://bigquery.googleapis.com/; then
  last=$(cat "$STATE" 2>/dev/null || echo 0)
  if (($(date +%s) - last > ALERT_DAYS * 86400)); then
    echo "[FAIL] $(date -u +%FT%TZ) no network, and the last successful run is $ALERT_DAYS+ days old"
    notify "Site analytics archive failed" "No network, and no successful run for $ALERT_DAYS+ days. See $LOG_HINT"
    exit 1
  fi
  echo "[INFO] $(date -u +%FT%TZ) no network; the next run retries"
  exit 0
fi

echo "[INFO] $(date -u +%FT%TZ) run starting (version $(cat "$HOME_DIR/VERSION" 2>/dev/null || echo unknown))"
uv run --script "$HOME_DIR/scripts/analytics_archive.py"
rc=$?
case "$rc" in
  0) date +%s > "$STATE" ;;
  1) ;; # the script reported the failure itself
  *)
    echo "[FAIL] $(date -u +%FT%TZ) analytics_archive.py exited $rc before it could report"
    notify "Site analytics archive failed" "The job exited $rc. See $LOG_HINT"
    ;;
esac
exit "$rc"
