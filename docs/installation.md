# Installation Guide

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: 3.8 or higher
- **Disk Space**: 100MB minimum (plus space for your comic library)
- **RAM**: 4GB minimum, 8GB recommended

## Installation Methods

### Method 1: Standalone Installer (Recommended for End Users)

1. Download the latest installer for your operating system from the [Releases](https://github.com/Nsfr750/ComicDB/releases) page
2. Run the installer and follow the on-screen instructions
3. Launch ComicDB from your applications menu or desktop shortcut

### Method 2: Using pip (For Developers)


1. Ensure Python 3.8+ is installed
2. Open a terminal/command prompt and run:
   ```bash
   pip install comicdb
   ```
3. Launch ComicDB by running:
   ```bash
   comicdb
   ```

### Method 3: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/Nsfr750/ComicDB.git
   cd ComicDB
   ```
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install in development mode:
   ```bash
   pip install -e .
   ```
5. Run the application:
   ```bash
   python -m comicdb
   ```

## Post-Installation

After installation, you may want to:

1. Configure your [comic library location](configuration.md#library-settings)
2. Set up [preferences](configuration.md#preferences)
3. Import your existing comic collection

## Troubleshooting

### Common Issues

#### Missing Dependencies
If you encounter missing dependency errors, try:
```bash
pip install -r requirements.txt
```

#### Permission Issues
On Linux/macOS, you might need to use `sudo` for system-wide installation.

#### Application Won't Start
- Check that all dependencies are installed
- Try running from the command line to see error messages
- Check the log file at `~/.comicdb/logs/comicdb.log`

## Updating ComicDB

### Standalone Installer
Download and run the latest installer from the [Releases](https://github.com/Nsfr750/ComicDB/releases) page.

### Using pip
```bash
pip install --upgrade comicdb
```

## Uninstallation

### Windows
1. Go to Settings > Apps > Apps & features
2. Find "ComicDB" in the list
3. Click Uninstall

### macOS
1. Open Finder
2. Go to Applications
3. Drag ComicDB to the Trash

### Linux
```bash
# For system-wide installation
sudo pip uninstall comicdb

# For user installation
pip uninstall comicdb
```
