# ComicDB Documentation

This directory contains the source files for the ComicDB documentation.

## Building the Documentation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository** (if you haven't already):

   ```bash
   git clone https://github.com/Nsfr750/ComicDB.git
   cd ComicDB
   ```

2. **Set up a virtual environment** (recommended):

   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   # source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r docs/requirements-docs.txt
   ```

### Building the Documentation

#### Build HTML (English)

```bash
cd docs
make html
```

The HTML output will be in `_build/html/`.

#### Build All Languages

```bash
cd docs
make multilang
```

#### Live Preview with Auto-reload

```bash
cd docs
make livehtml
```

Then open http://localhost:8000 in your browser.

## Translation

### Extracting Strings for Translation

1. Extract translatable strings:

   ```bash
   cd docs
   make gettext
   ```

2. Update translation files:

   ```bash
   make updatepo
   ```

3. Edit the `.po` files in `locale/it/LC_MESSAGES/`

4. Compile translations:

   ```bash
   make compilepo
   ```

### Adding a New Language

1. Add the language code to `LANGUAGES` in the `Makefile`
2. Create the language directory structure:

   ```bash
   mkdir -p locale/xx/LC_MESSAGES
   ```

3. Initialize the translation files:

   ```bash
   sphinx-intl update -p _build/locale -l xx -d locale/
   ```

4. Translate the `.po` files in `locale/xx/LC_MESSAGES/`

## Documentation Structure

```
docs/
├── _static/                # Static files (CSS, JS, images)
├── _templates/             # Custom templates
├── additional/             # Additional documentation (changelog, license, etc.)
├── developer/              # Developer documentation
├── locale/                 # Translation files
├── user/                   # User documentation
├── conf.py                 # Sphinx configuration
├── index.rst              # Main documentation page
├── Makefile               # Build commands
└── requirements-docs.txt  # Documentation dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

The documentation is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).
