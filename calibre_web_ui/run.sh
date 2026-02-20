#!/usr/bin/env bash

# HA Add-ons usually map data to /share or /data
# Let's use /share/calibre for the library so it's accessible across the network and survives add-on updates.
CALIBRE_LIBRARY_DIR="/share/calibre"

echo "Starting Calibre Web UI Add-on..."

# Check if library directory exists, create if not
if [ ! -d "$CALIBRE_LIBRARY_DIR" ]; then
    echo "Creating Calibre library directory at $CALIBRE_LIBRARY_DIR..."
    mkdir -p "$CALIBRE_LIBRARY_DIR"
fi

# Ensure the library has a metadata.db, or create an empty one by running a dummy list command
echo "Initializing Calibre library database if not present..."
# Note: we run calibredb list to trigger database creation if it's completely empty/new
# The command might fail if empty or no db, but it's safe to run
calibredb list --library-path="$CALIBRE_LIBRARY_DIR" > /dev/null 2>&1

export CALIBRE_LIBRARY_PATH="$CALIBRE_LIBRARY_DIR"

echo "Starting Web Server..."
# Run the Flask application via gunicorn
exec gunicorn -w 4 -b 0.0.0.0:8080 main:app
