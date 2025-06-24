# ComicDB

[![GitHub release](https://img.shields.io/badge/release-v0.0.3-green)](https://github.com/Nsfr750/ComicDB/releases/tag/v0.0.3)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/Nsfr750/ComicDB/graphs/commit-activity)
[![Last Commit](https://img.shields.io/github/last-commit/Nsfr750/ComicDB?style=for-the-badge)](https://github.com/Nsfr750/ComicDB/commits/main)

A modern comic book collection manager and viewer with support for CBZ, CBR, CBT, CB7, and PDF formats.

**License:** This project is licensed under the GNU General Public License v3.0 (GPLv3). See [LICENSE](LICENSE) for details.

## Features

- Support for CBZ, CBR, CBT, CB7, and PDF comic book formats
- Advanced metadata extraction using comicapi
- Automatic cover image extraction
- Quick search and filter capabilities
- Modern, themeable interface
- Comprehensive logging system
- Cross-platform compatibility

## 📋 Requirements

- Python 3.8 or higher
- Tkinter (included with standard Python)
- Additional dependencies listed in `requirements.txt`

## 🚀 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Nsfr750/ComicDB.git
   cd ComicDB
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Platform-Specific Dependencies

#### Windows

```powershell
pip install python-magic-bin
```

#### Linux (Debian/Ubuntu)

```bash
sudo apt-get install libmagic1
```

#### macOS (using Homebrew)

```bash
brew install libmagic
```

## 🖥️ Usage

Run the application:

```bash
python main.py
```

## Centralized Logging System

All log entries (info, warning, error, and uncaught exceptions) are written to `traceback.log` in your project root. The logging system is thread-safe and timestamps all entries.

### How to Use

```python
from struttura.logger import log_info, log_warning, log_error

log_info("A message for info level")
log_warning("A message for warning level")
log_error("A message for error level")
```

To automatically log uncaught exceptions, call:

```python
from struttura.logger import setup_global_exception_logging
setup_global_exception_logging()
```

### Log Viewer

Access the Log Viewer from the menu bar to filter logs in real time by ALL, INFO, WARNING, or ERROR.

### Automated Tests

Automated tests for the logging system are provided in `tests/test_logger.py`. These tests verify info, warning, error, and exception logging, as well as global exception hook functionality.

Run tests with:

```bash
.venv\Scripts\pytest tests/test_logger.py
```

## Project Structure

- `main.py` — Main entry point
- `gui/` — GUI components (windows, widgets)
- `struttura/` — Core logic, dialogs, and utilities

## Troubleshooting

- If you see `ModuleNotFoundError` for a module in `struttura`, make sure you are running from the root and not from inside a subfolder.
- All sibling imports in `struttura` use relative imports (e.g., `from .about import About`).

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the LICENSE file for full terms.
