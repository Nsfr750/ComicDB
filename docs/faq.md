# Frequently Asked Questions

## General

### What is ComicDB?
ComicDB is a powerful, open-source comic book collection manager that helps you organize, catalog, and read your digital comic book collection.

### Is ComicDB free?
Yes, ComicDB is completely free and open-source software released under the GPL3 License.

### What platforms does ComicDB support?
ComicDB is available for Windows, macOS, and Linux. A web version is also in development.

## Installation

### What are the system requirements?
- Windows 10/11, macOS 10.15+, or Linux (64-bit)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Internet connection (for metadata fetching)

### How do I install ComicDB on Windows?
1. Download the latest installer from our [GitHub releases](https://github.com/Nsfr750/ComicDB/releases)
2. Run the installer and follow the on-screen instructions
3. Launch ComicDB from the Start menu

## Features

### What file formats does ComicDB support?
- CBZ, CBR, PDF, and more
- Images: JPG, PNG, GIF, WEBP
- Archives: ZIP, RAR, 7Z

### Can I import my existing library?
Yes, ComicDB can import from:
- ComicRack
- ComicBookLover
- Comic Vine
- CSV/JSON exports

### Is there a mobile app?
A mobile app is currently in development. In the meantime, you can use the web interface on your mobile device.

## Troubleshooting

### ComicDB won't start
1. Make sure you have the latest version of .NET installed
2. Try running as administrator
3. Check the logs in `%APPDATA%\ComicDB\logs`

### My comics aren't importing
1. Check that the files are in a supported format
2. Make sure the files aren't corrupted
3. Verify that you have read permissions for the files

### Metadata isn't downloading
1. Check your internet connection
2. Verify that the comic has a valid ISBN or issue number
3. Try manually refreshing the metadata

## Data & Privacy

### Where is my data stored?
All data is stored locally on your computer by default. The database is located at:
- Windows: `%APPDATA%\ComicDB`
- macOS: `~/Library/Application Support/ComicDB`
- Linux: `~/.config/ComicDB`

### Is my data backed up?
ComicDB automatically creates backups in the `backups` folder within the data directory. You can also set up automatic cloud backups in the settings.

### Is my collection shared online?
No, your collection is stored locally by default. You can choose to enable cloud sync if desired.

## Contributing

### How can I contribute to ComicDB?
We welcome contributions! You can help by:
1. Reporting bugs
2. Suggesting new features
3. Submitting pull requests
4. Improving documentation
5. Translating the interface

### Where can I report bugs?
Please report bugs on our [GitHub Issues](https://github.com/Nsfr750/ComicDB/issues) page.

### How can I request a new feature?
You can request new features by creating an issue on our [GitHub repository](https://github.com/Nsfr750/ComicDB/issues).

## Support

### Where can I get help?
- Check out our [documentation](index.md)
- Join our [Discord server](https://discord.gg/...)
- Post in our [community forum](https://github.com/Nsfr750/ComicDB/discussions)
- Open an issue on [GitHub](https://github.com/Nsfr750/ComicDB/issues)

### Is there a user guide?
Yes, check out our [Getting Started](getting-started.md) guide and [User Manual](user-manual.md).

### How do I update ComicDB?
ComicDB will notify you when updates are available. You can also check for updates manually in the Help menu.

## Advanced

### Can I use my own metadata sources?
Yes, you can add custom metadata sources in the settings.

### Is there an API?
Yes, check out our [API documentation](api.md) for more information.

### Can I run ComicDB on a server?
A server version is planned for a future release.
