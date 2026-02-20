#!/usr/bin/with-contenv bashio
set -euo pipefail

# HA Add-ons store user configuration in /data/options.json
CONFIG_PATH="/data/options.json"

# Read options using jq
LIBRARY_PATH=$(jq --raw-output '.library_path' "$CONFIG_PATH")
SYNC_DIR=$(jq --raw-output '.sync_dir // ""' "$CONFIG_PATH")
LOG_LEVEL=$(jq --raw-output '.log_level' "$CONFIG_PATH")

# Use defaults if not provided
CALIBRE_LIBRARY_DIR="${LIBRARY_PATH:-/share/calibre}"
LOG_LEVEL="${LOG_LEVEL:-info}"

echo "Starting Calibre Web UI Add-on..."
echo "Configuration: Library Path = $CALIBRE_LIBRARY_DIR, Sync Dir = $SYNC_DIR, Log Level = $LOG_LEVEL"

# Create library directory if it doesn't exist
if [ ! -d "$CALIBRE_LIBRARY_DIR" ]; then
    echo "Creating Calibre library directory at $CALIBRE_LIBRARY_DIR..."
    mkdir -p "$CALIBRE_LIBRARY_DIR"
fi

# Initialize the Calibre library database if not present
echo "Initializing Calibre library database if not present..."
calibredb list --library-path="$CALIBRE_LIBRARY_DIR" > /dev/null 2>&1 || true

export CALIBRE_LIBRARY_PATH="$CALIBRE_LIBRARY_DIR"
export CALIBRE_SYNC_DIR="$SYNC_DIR"
export LOG_LEVEL="$LOG_LEVEL"

echo "Starting Web Server..."
# Run Flask via gunicorn (2 workers suitable for embedded/HA hardware)
exec gunicorn --workers 2 --bind 0.0.0.0:8080 --timeout 120 main:app
