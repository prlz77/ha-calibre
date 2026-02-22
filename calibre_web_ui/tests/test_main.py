import os
import io
import json
import pytest

# Set env vars for tests
os.environ["CALIBRE_LIBRARY_PATH"] = "/test/library"
os.environ["CALIBRE_SYNC_DIR"] = "/test/sync"
os.environ["LOG_LEVEL"] = "DEBUG"

# Need to import app after setting environ
from app.main import app, run_calibre_cmd

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_run_calibre(monkeypatch):
    """Mock the subprocess.run call inside run_calibre_cmd."""
    class MockResult:
        def __init__(self, stdout, returncode=0):
            self.stdout = stdout
            self.returncode = returncode

    def mock_run_cmd(*args, **kwargs):
        cmd = args[0]
        # Basic mock responses depending on command
        if "list" in cmd:
            return MockResult(json.dumps([
                {"id": 1, "title": "Test Book", "authors": "John Doe", "formats": ["/test/library/Test Book.epub", "/test/library/Test Book.mobi"]}
            ]))
        elif "add" in cmd and "--automerge" not in cmd:
             return MockResult("Added book id: 2")
        elif "add" in cmd and "--automerge" in cmd:
             return MockResult("Sync completed")
        elif "remove" in cmd:
             return MockResult("Deleted book")
        elif "ebook-convert" in cmd:
             # Create a dummy converted file to simulate success
             target_file = cmd[-1]
             with open(target_file, "w") as f:
                 f.write("dummy content")
             return MockResult("Conversion success")
        elif "add_format" in cmd:
             return MockResult("Added format")
        return MockResult("")

    import subprocess
    monkeypatch.setattr(subprocess, "run", mock_run_cmd)

def test_index_page(client, mock_run_calibre):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Test Book" in response.data

def test_upload_book(client, mock_run_calibre):
    data = {"file": (io.BytesIO(b"dummy ebook content"), "test_book.epub")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 302 # Redirect after success

def test_convert_book(client, mock_run_calibre, monkeypatch):
    data = {"format": "azw3"}
    response = client.post("/convert/1", data=data)
    assert response.status_code == 302 # Redirect on success

def test_delete_book(client, mock_run_calibre):
    response = client.post("/delete/1")
    assert response.status_code == 302 # Redirect after delete

def test_sync_directory(client, mock_run_calibre, monkeypatch):
    # Mock os.path.isdir to pass sync validation
    import os
    monkeypatch.setattr(os.path, "isdir", lambda path: True)
    response = client.post("/sync")
    assert response.status_code == 302 # Redirect after sync
