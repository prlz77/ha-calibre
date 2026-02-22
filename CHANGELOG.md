# Changelog

## 1.5.1

### Fixed
- **UI Layout** — Fixed overlap between book title and author on small screens.

### Added
- **Orientation-based Layout** — Automatically switches between List (vertical) and Grid (horizontal) views.

## 1.5.0

### Added
- **Quality Checks** — Integrated `ruff` for Rust-speed linting and formatting.
- **Automated Testing** — Added `pytest` suite for core web endpoints.
- **CI/CD Pipeline** — Added GitHub Actions workflow to run tests on every push.
- **Pre-commit Hooks** — Standardized local development with automated quality checks.
- **Compact Mobile View** — Optimized the UI for e-readers and small screens by reducing vertical spacing and switching to a list view.

### Changed
- Generalized UI and documentation to support all e-readers/mobile devices instead of focusing on Kindle specifically.
- Restructured README with a friendlier donation invite and quality badges.


## 1.4.2

### Added
- **Drag & Drop Upload** — You can now drag and drop book files directly onto the "Add New Book" box in the web UI.

## 1.4.1

### Fixed
- **Kindle Compatibility** — Automatically serve `.azw3` files as `.azw` to bypass Kindle browser download restrictions.
- **Kindle UI Layout** — Added legacy CSS fallback to ensure a 2-column grid on Kindle browsers (which lack Flexbox support).

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
- **Support** — Added "Buy Me a Coffee" link to the web interface and README.

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
