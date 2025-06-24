# Changelog

## [Unreleased]

## [0.0.2] - 2025-06-24

### Added

- Added support for additional comic archive formats (CBT, CB7)
- Integrated comicapi library for improved metadata extraction
- Added proper RAR archive support using unrar and rarfile
- Enhanced error handling for archive processing
- Added comprehensive logging for debugging

### Changed

- Replaced direct archive handling with comicapi for better format support
- Updated requirements.txt with new dependencies
- Improved metadata extraction accuracy
- Enhanced error messages and user feedback

### Fixed

- Fixed issues with RAR/CBR file handling
- Resolved metadata extraction errors
- Fixed cover image extraction for various archive formats
- Improved handling of corrupted or invalid archives

## [0.0.1] - 2025-06-24

### Added

- Initial release of ComicDB
- Support for CBZ, CBR, and PDF comic book formats
- Basic comic metadata extraction
- Cover image extraction
- Simple GUI interface
- Logging system for debugging

### Changed

- Replaced rarfile with py7zr for better archive handling
- Improved error handling for corrupted archives
- Enhanced file type detection
- Updated project documentation

### Fixed

- Fixed issues with archive validation
- Improved handling of invalid or corrupted files
- Fixed file path handling for Windows systems

---

This project is licensed under the GNU General Public License v3.0 (GPLv3). See [LICENSE](LICENSE) for details.
