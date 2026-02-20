import json
import logging
import os
import secrets
import subprocess

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configure logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# Middleware to handle Home Assistant Ingress path
class IngressMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        ingress_path = environ.get("HTTP_X_INGRESS_PATH", "")
        if ingress_path:
            environ["SCRIPT_NAME"] = ingress_path
            path_info = environ.get("PATH_INFO", "")
            if path_info.startswith(ingress_path):
                environ["PATH_INFO"] = path_info[len(ingress_path):]
        return self.wsgi_app(environ, start_response)


app.wsgi_app = IngressMiddleware(app.wsgi_app)

CALIBRE_LIBRARY_PATH = os.environ.get("CALIBRE_LIBRARY_PATH", "/share/calibre")
CALIBRE_SYNC_DIR = os.environ.get("CALIBRE_SYNC_DIR", "")
CALIBRE_SYNC_INTERVAL = int(os.environ.get("CALIBRE_SYNC_INTERVAL", "0"))
UPLOAD_FOLDER = "/tmp/calibre_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logger.info("Flask App starting with LIBRARY_PATH: %s", CALIBRE_LIBRARY_PATH)
if CALIBRE_SYNC_DIR:
    logger.info("Sync Directory enabled: %s", CALIBRE_SYNC_DIR)
logger.info("Log Level set to: %s", LOG_LEVEL)


def run_calibre_cmd(cmd_list):
    """Run a calibre CLI command with xvfb for headless display support."""
    full_cmd = ["xvfb-run", "-a"] + cmd_list
    logger.debug("Running command: %s", " ".join(full_cmd))
    try:
        result = subprocess.run(
            full_cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error("Command timed out: %s", " ".join(full_cmd))
        return None
    except subprocess.CalledProcessError as e:
        logger.error("Calibre error (cmd: %s): %s", " ".join(full_cmd), e.stderr)
        return None


def get_books():
    """Fetch the full book list with format paths from the library."""
    stdout = run_calibre_cmd([
        "calibredb", "list",
        "--library-path", CALIBRE_LIBRARY_PATH,
        "--for-machine",
        "--fields", "title,authors,formats",
    ])
    if not stdout:
        return []
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        logger.error("Failed to parse calibredb list output")
        return []


def get_book_formats(book_id):
    """Get the format file paths for a single book."""
    stdout = run_calibre_cmd([
        "calibredb", "list",
        "--library-path", CALIBRE_LIBRARY_PATH,
        "--for-machine",
        "--fields", "formats",
        "--search", f"id:{book_id}",
    ])
    if not stdout:
        return []
    try:
        books = json.loads(stdout)
        if books:
            return books[0].get("formats", [])
    except (json.JSONDecodeError, IndexError):
        pass
    return []


def is_safe_library_path(filepath):
    """Verify a file path is within the Calibre library (no traversal)."""
    real_path = os.path.realpath(filepath)
    real_library = os.path.realpath(CALIBRE_LIBRARY_PATH)
    return real_path.startswith(real_library + os.sep) and os.path.isfile(real_path)


@app.route("/")
def index():
    books = get_books()
    return render_template(
        "index.html",
        books=books,
        sync_enabled=bool(CALIBRE_SYNC_DIR),
        sync_interval=CALIBRE_SYNC_INTERVAL,
    )


@app.route("/upload", methods=["POST"])
def upload_book():
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    if not filename:
        flash("Invalid filename", "error")
        return redirect(url_for("index"))

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        result = run_calibre_cmd([
            "calibredb", "add",
            "--library-path", CALIBRE_LIBRARY_PATH,
            filepath,
        ])

        if result is not None:
            flash(f"Successfully added {filename}", "success")
        else:
            flash(f"Failed to add {filename}", "error")
    finally:
        # Always cleanup the uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

    return redirect(url_for("index"))


@app.route("/convert/<int:book_id>", methods=["POST"])
def convert_book(book_id):
    target_format = request.form.get("format", "mobi").lower()

    allowed_formats = {"mobi", "azw3", "epub", "pdf"}
    if target_format not in allowed_formats:
        flash("Invalid target format", "error")
        return redirect(url_for("index"))

    # Get available format paths for this book
    formats = get_book_formats(book_id)
    if not formats:
        flash("No formats available to convert from", "error")
        return redirect(url_for("index"))

    # Prefer EPUB as source, otherwise use the first available format
    source_file = next(
        (f for f in formats if f.lower().endswith(".epub")),
        formats[0],
    )

    # Don't convert to the same format
    source_ext = os.path.splitext(source_file)[1].lstrip(".").lower()
    if source_ext == target_format:
        flash(f"Book is already in {target_format.upper()} format", "warning")
        return redirect(url_for("index"))

    base_name = os.path.splitext(os.path.basename(source_file))[0]
    converted_file = os.path.join(UPLOAD_FOLDER, f"{base_name}.{target_format}")

    try:
        convert_result = run_calibre_cmd([
            "ebook-convert",
            source_file,
            converted_file,
        ])

        if convert_result is not None and os.path.exists(converted_file):
            # Add the converted format back to the library
            add_result = run_calibre_cmd([
                "calibredb", "add_format",
                "--library-path", CALIBRE_LIBRARY_PATH,
                str(book_id),
                converted_file,
            ])
            if add_result is not None:
                flash(f"Successfully converted to {target_format.upper()}", "success")
            else:
                flash("Conversion succeeded but failed to add to library", "error")
        else:
            flash("Conversion failed", "error")
    except Exception as e:
        logger.exception("Error during conversion of book %d", book_id)
        flash(f"Error during conversion: {e}", "error")
    finally:
        if os.path.exists(converted_file):
            os.remove(converted_file)

    return redirect(url_for("index"))


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    result = run_calibre_cmd([
        "calibredb", "remove",
        "--library-path", CALIBRE_LIBRARY_PATH,
        str(book_id),
    ])

    if result is not None:
        flash("Book deleted successfully", "success")
    else:
        flash("Failed to delete book", "error")

    return redirect(url_for("index"))


@app.route("/sync", methods=["POST"])
def sync_directory():
    if not CALIBRE_SYNC_DIR:
        flash("Sync directory not configured", "error")
        return redirect(url_for("index"))

    if not os.path.isdir(CALIBRE_SYNC_DIR):
        flash(f"Sync directory does not exist: {CALIBRE_SYNC_DIR}", "error")
        return redirect(url_for("index"))

    logger.info("Starting sync from directory: %s", CALIBRE_SYNC_DIR)
    
    # Using calibredb add -r --automerge ignore to avoid duplicates
    result = run_calibre_cmd([
        "calibredb", "add",
        "-r", CALIBRE_SYNC_DIR,
        "--library-path", CALIBRE_LIBRARY_PATH,
        "--automerge", "ignore",
    ])

    if result is not None:
        flash("Sync completed successfully", "success")
    else:
        flash("Sync failed or encountered errors", "error")

    return redirect(url_for("index"))


@app.route("/download/<path:filepath>")
def download_book(filepath):
    # filepath comes URL-decoded from Flask; prepend / for absolute path
    abs_path = "/" + filepath

    if not is_safe_library_path(abs_path):
        logger.warning("Blocked download attempt for: %s", abs_path)
        return "Forbidden", 403

    directory = os.path.dirname(abs_path)
    filename = os.path.basename(abs_path)

    # Kindle compatibility: The Kindle browser only allows downloading specific extensions (.mobi, .azw, .prc, .txt).
    # If the file is .azw3 and the requester is a Kindle, we serve it as .azw so it can be downloaded.
    user_agent = request.headers.get("User-Agent", "")
    download_name = None
    if "Kindle" in user_agent and filename.lower().endswith(".azw3"):
        download_name = filename[:-1]  # Change .azw3 to .azw
        logger.info("Renaming %s to %s for Kindle download", filename, download_name)

    return send_from_directory(
        directory, 
        filename, 
        as_attachment=True, 
        download_name=download_name
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
