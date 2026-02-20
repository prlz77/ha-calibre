import json
import os
import subprocess
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_calibre_key_for_flash_messages"

# Middleware to handle Home Assistant Ingress path
class IngressMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Home Assistant adds X-Ingress-Path header
        ingress_path = environ.get('HTTP_X_INGRESS_PATH', '')
        if ingress_path:
            environ['SCRIPT_NAME'] = ingress_path
            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith(ingress_path):
                environ['PATH_INFO'] = path_info[len(ingress_path):]
        
        return self.app(environ, start_response)

app.wsgi_app = IngressMiddleware(app.wsgi_app)

CALIBRE_LIBRARY_PATH = os.environ.get("CALIBRE_LIBRARY_PATH", "/share/calibre")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
UPLOAD_FOLDER = "/tmp/calibre_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print(f"Flask App starting with LIBRARY_PATH: {CALIBRE_LIBRARY_PATH}")
print(f"Log Level set to: {LOG_LEVEL}")

def run_calibre_cmd(cmd_list):
    # Some calibre tools require a display server; xvfb-run provides a virtual one.
    full_cmd = ["xvfb-run"] + cmd_list
    try:
        result = subprocess.run(
            full_cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Calibre error (cmd: {' '.join(full_cmd)}): {e.stderr}")
        return None

@app.route("/")
def index():
    # Fetch list of books as JSON
    stdout = run_calibre_cmd([
        "calibredb", "list",
        "--library-path", CALIBRE_LIBRARY_PATH,
        "--for-machine"
    ])
    
    books = []
    if stdout:
        try:
            books = json.loads(stdout)
        except json.JSONDecodeError:
            books = []
            
    return render_template("index.html", books=books)

@app.route("/upload", methods=["POST"])
def upload_book():
    if 'file' not in request.files:
        flash("No file part", "error")
        return redirect(url_for("index"))
    
    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for("index"))
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Add to calibre
        result = run_calibre_cmd([
            "calibredb", "add",
            "--library-path", CALIBRE_LIBRARY_PATH,
            filepath
        ])
        
        # Cleanup
        os.remove(filepath)
        
        if result is not None:
            flash(f"Successfully added {filename}", "success")
        else:
            flash(f"Failed to add {filename}", "error")
            
    return redirect(url_for("index"))

@app.route("/convert/<int:book_id>", methods=["POST"])
def convert_book(book_id):
    target_format = request.form.get("format", "mobi").lower()
    
    if target_format not in ["mobi", "azw3", "epub", "pdf"]:
         return jsonify({"error": "Invalid format"}), 400
         
    # Calibre provides a way to convert formats by adding a new format
    # calibredb add_format id path_to_file
    # But first we need the existing file to convert. 
    # Actually, Calibre supports converting within the library via `calibredb add_format` ... wait, ebook-convert is separate.
    # calibredb doesn't have a direct "convert" command inside the library in CLI.
    # We must extract the format, convert it, and add it back.
    
    # Let's get the book metadata first
    stdout = run_calibre_cmd([
        "calibredb", "show_metadata",
        str(book_id),
        "--library-path", CALIBRE_LIBRARY_PATH,
        "--as-json"
    ])
    
    if not stdout:
        flash("Could not fetch book metadata", "error")
        return redirect(url_for("index"))
        
    try:
        metadata = json.loads(stdout)
        formats = metadata.get("formats", [])
        if not formats:
            flash("No formats to convert from", "error")
            return redirect(url_for("index"))
            
        # Prioritize epub if it exists, otherwise use the first format
        source_file = next((f for f in formats if f.lower().endswith("epub")), formats[0])
        
        # Prepare output path
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        converted_file = os.path.join(UPLOAD_FOLDER, f"{base_name}.{target_format}")
        
        # Run ebook-convert
        convert_result = run_calibre_cmd([
            "ebook-convert",
            source_file,
            converted_file
        ])
        
        if convert_result is not None and os.path.exists(converted_file):
            # Add back to library
            run_calibre_cmd([
                "calibredb", "add_format",
                str(book_id),
                converted_file,
                "--library-path", CALIBRE_LIBRARY_PATH
            ])
            os.remove(converted_file)
            flash(f"Successfully converted to {target_format.upper()}", "success")
        else:
            flash("Conversion failed", "error")
            
    except Exception as e:
        flash(f"Error during conversion: {str(e)}", "error")

    return redirect(url_for("index"))

@app.route("/download/<path:filepath>")
def download_book(filepath):
    # Calibredb list returns absolute paths to the library files
    # We can safely serve them since they are within the library path
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    
    # Additional security check to ensure it's from the allowed directory
    full_path = os.path.abspath(filepath)
    if not full_path.startswith(os.path.abspath(CALIBRE_LIBRARY_PATH)):
        return "Unauthorized", 403
        
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
