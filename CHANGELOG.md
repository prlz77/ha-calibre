# Changelog

## 1.4.0

### Added
- **Autosync** — New feature to periodically sync books from a local directory.
- **Improved Resource Efficiency** — Background sync loop runs in bash to minimize RAM/CPU usage.

### Changed
- Added `sync_interval` configuration option.
- Updated UI to display autosync status.

## 1.3.0

### Added
- **Directory Sync** — New feature to bulk add books from a configured local directory.
- **Sync Library UI** — Added a "Sync Now" button in the web interface.
- **Plugin Icon** — Replaced default icon with a custom book-themed icon.

### Changed
- Updated configuration options to include `sync_dir`.

## 1.2.2

### Security
- Fixed path traversal vulnerability in download endpoint
- Replaced hardcoded Flask secret key with random generation at startup

### Fixed
- Fixed convert endpoint — was using invalid `calibredb show_metadata --as-json` flag
- Fixed book listing — `calibredb list` now requests `--fields title,authors,formats` to include format paths
- Fixed download URL construction — paths are now properly stripped of leading `/`
- Fixed typo: "mangement" → "management"

### Added
- **Delete books** — new delete button per book card
- **Offline UI** — Bulma CSS and Font Awesome are now bundled locally (no CDN dependency)
- **Book count** shown in library header
- **File type filter** on upload input
- Proper Python `logging` module instead of `print()` statements
- Command timeouts (120s) to prevent hung calibre processes
- `.dockerignore` to reduce Docker image size
- Home Assistant labels in Dockerfile
- `README.md` and `CHANGELOG.md` documentation

### Changed
- Reduced gunicorn workers from 4 to 2 (better for embedded HA hardware)
- Added `--timeout 120` to gunicorn for long conversions
- Added bash shebang and `set -euo pipefail` to `run.sh`
- Improved UI visual design and empty state messaging
- Kindle-compatible JavaScript (no ES6 arrow functions)

## 1.1.1

- Initial release with book listing, upload, conversion, and download
