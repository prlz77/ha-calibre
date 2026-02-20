# HA Add-ons store user configuration in /data/options.json
CONFIG_PATH="/data/options.json"

# Read options using jq
LIBRARY_PATH=$(jq --raw-output '.library_path' $CONFIG_PATH)
LOG_LEVEL=$(jq --raw-output '.log_level' $CONFIG_PATH)

# Use defaults if not provided
CALIBRE_LIBRARY_DIR="${LIBRARY_PATH:-/share/calibre}"

echo "Starting Calibre Web UI Add-on..."
echo "Configuration: Library Path = $CALIBRE_LIBRARY_DIR, Log Level = $LOG_LEVEL"

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
export LOG_LEVEL="$LOG_LEVEL"

echo "Starting Web Server..."
# Run the Flask application via gunicorn
exec gunicorn -w 4 -b 0.0.0.0:8080 main:app
