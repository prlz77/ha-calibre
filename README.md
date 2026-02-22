# Home Assistant Add-on: Calibre Web UI

[![Build Status](https://github.com/prlz77/ha-calibre/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/prlz77/ha-calibre/actions/workflows/ci.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**TL;DR**: Convert your e-books to any format and download them on your e-reader through a clean web interface.

[![Add to Home Assistant](https://img.shields.io/badge/Add%20to-Home%20Assistant-41BDF5?style=for-the-badge&logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/repository_add/?repository_url=https%3A%2F%2Fgithub.com%2Fprlz77%2Fha-calibre)

If this add-on saves you time, makes your ebook setup easier, or helps you bridge the gap between Calibre and your family's e-readers, I would be very grateful for your support!

[![Buy me a coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/prlz77)

---

![Calibre Web UI](https://raw.githubusercontent.com/prlz77/ha-calibre/main/screenshots/ui.png)

Calibre Web UI is a lightweight Home Assistant add-on designed to bridge the gap between Calibre's powerful command-line tools and your local network devices. It provides a clean, responsive web interface that allows you to manage your book library, convert formats on the fly, and download books directly to your devices—including e-readers with minimalist browsers.

Whether you're looking to centralize your ebook collection on your Home Assistant instance or need a simple way to beam books to your devices without a USB cable, this add-on provides a seamless, resource-efficient solution.

## Why this add-on? (Philosophy)

There are excellent, full-featured tools like [janeczku/calibre-web](https://github.com/janeczku/calibre-web) available. This add-on is designed for a different use case:

-   **Resource Efficient**: Minimal RAM and CPU footprint, making it ideal for standard Home Assistant hardware (Pi 4, Blue/Yellow/Green, etc.).
-   **Zero Configuration**: Directly interacts with the Calibre CLI. No complex database shims or multi-user registration needed.
-   **E-reader First**: The UI is built with Bulma, specifically tuned to be fast and responsive on the minimalist web browsers found on e-ink devices.

> [!TIP]
> If you need multi-user management, refined administrative controls, public registration, or OPDS support, [calibre-web](https://github.com/janeczku/calibre-web) is likely the better choice for you.

## Features

- **Autosync** — Automatically sync your books at a configurable interval
- **Directory Sync** — Bulk add books from a local directory
- **Book Library** — Browse your Calibre library from any device on your LAN
- **Upload Books** — Add EPUB, MOBI, PDF, and other e-book formats via the web UI
- **Format Conversion** — Convert books between EPUB, MOBI, AZW3, and PDF using Calibre's `ebook-convert`
- **Download Books** — Download books directly from the library to your device
- **Delete Books** — Remove books from your library
- **E-reader Support** — Access your library from almost any e-reader or mobile web browser
- **Offline UI** — All CSS/fonts are bundled locally; no internet required

## Installation

1. Add this repository to your Home Assistant instance:
   - Go to **Settings → Add-ons → Add-on Store → ⋮ → Repositories**
   - Add: `https://github.com/prlz77/ha-calibre`
2. Find **Calibre Web UI** in the add-on store and click **Install**
3. Configure the add-on (see below) and click **Start**
4. Open the Web UI via the **Ingress** panel or navigate to `http://<your-ha-ip>:8080`

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `library_path` | `/share/calibre` | Path to the Calibre library on the HA host |
| `sync_dir` | (empty) | Optional path to a folder to sync books from |
| `sync_interval` | `0` (disabled) | Periodic sync interval in minutes |
| `log_level` | `info` | Logging verbosity: `debug`, `info`, `warning`, `error` |

## Accessing from E-readers & Mobile

1. Connect your device to the same Wi-Fi network as your Home Assistant
2. Open your device's web browser
3. Navigate to `http://<your-ha-ip>:8080`
4. Browse and download books directly to your device

## Development

```bash
cd calibre_web_ui
docker build -t calibre-web-ui .
docker run -p 8080:8080 -v /path/to/your/library:/share/calibre calibre-web-ui
```

## Support

Got questions, discovered a bug, or have a feature request? Please create an issue on [GitHub](https://github.com/prlz77/ha-calibre).
