import os
import logging
import tempfile
import shutil
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List, BinaryIO, Union
import zipfile
import io
import magic
import pikepdf
from PIL import Image
from io import BytesIO
import base64
import re
from dataclasses import dataclass, field
import contextlib

# Set up unrar path
if sys.platform == 'win32':
    # Common UnRAR installation paths on Windows
    unrar_paths = [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        r"C:\Program Files\UnrarDLL\UnRAR.exe",
        r"C:\Program Files (x86)\UnrarDLL\UnRAR.exe"
    ]
    
    for path in unrar_paths:
        if os.path.exists(path):
            os.environ['UNRAR_LIB_PATH'] = os.path.dirname(path)
            break

import comicapi.comicarchive
from comicapi import utils
from comicapi.issuestring import *
from comicapi.comicarchive import *
from comicapi.archivers import Archiver
from comicapi.genericmetadata import GenericMetadata
from comicapi.comicarchive import MetaDataStyle
import rarfile

# Configure rarfile to use unrar if available
try:
    from unrar import rarfile as unrar_rarfile
    rarfile.UNRAR_TOOL = 'unrar'  # Use the Python unrar package
    rarfile.UNRAR_TOOL_AVAILABLE = True
except ImportError:
    # Fall back to default rarfile behavior
    pass
logger = logging.getLogger(__name__)


@dataclass
class ComicMetadata:
    """Data class for storing comic book metadata."""
    title: str = ""
    series: Optional[str] = None
    subseries: Optional[str] = None  # Added subseries field
    issue_number: Optional[str] = None
    volume: Optional[int] = None
    year: Optional[int] = None
    publisher: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    notes: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    web: Optional[str] = None
    page_count: Optional[int] = None
    format: Optional[str] = None
    black_and_white: bool = False
    manga: bool = False
    characters: List[str] = field(default_factory=list)
    teams: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    scan_info: Optional[str] = None
    story_arc: Optional[str] = None
    story_arc_number: Optional[str] = None
    series_group: Optional[str] = None
    alternate_series: Optional[str] = None
    alternate_number: Optional[str] = None
    alternate_count: Optional[int] = None
    count: Optional[int] = None
    age_rating: Optional[str] = None
    community_rating: Optional[float] = None
    main_character_or_team: Optional[str] = None
    review: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_modified: Optional[float] = None
    cover_image: Optional[bytes] = None
    cover_image_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary."""
        return {
            'title': self.title,
            'series': self.series,
            'subseries': self.subseries,
            'issue_number': self.issue_number,
            'volume': self.volume,
            'year': self.year,
            'publisher': self.publisher,
            'authors': self.authors,
            'summary': self.summary,
            'notes': self.notes,
            'genre': self.genre,
            'language': self.language,
            'web': self.web,
            'page_count': self.page_count,
            'format': self.format,
            'black_and_white': self.black_and_white,
            'manga': self.manga,
            'characters': self.characters,
            'teams': self.teams,
            'locations': self.locations,
            'scan_info': self.scan_info,
            'story_arc': self.story_arc,
            'story_arc_number': self.story_arc_number,
            'series_group': self.series_group,
            'alternate_series': self.alternate_series,
            'alternate_number': self.alternate_number,
            'alternate_count': self.alternate_count,
            'count': self.count,
            'age_rating': self.age_rating,
            'community_rating': self.community_rating,
            'main_character_or_team': self.main_character_or_team,
            'review': self.review,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_modified': self.file_modified,
            'cover_image_type': self.cover_image_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComicMetadata':
        """Create a ComicMetadata instance from a dictionary."""
        metadata = cls()
        for key, value in data.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        return metadata


class ComicScanner:
    """
    Class for scanning and processing comic book files (CBR, CBZ, PDF).
    Extracts metadata and cover images from comic book files.
    """
    
    def __init__(self):
        self.supported_formats = ['.cbr', '.cbz', '.cbt', '.cb7', '.pdf']
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        self.max_cover_size = (300, 450)  # Max dimensions for cover images
        self.comic_archive = None
        self.logger = logging.getLogger(__name__)
    
    def is_comic_file(self, file_path: str) -> bool:
        """Check if the file is a supported comic book format."""
        ext = os.path.splitext(file_path.lower())[1]
        return ext in self.supported_formats
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Scan a directory for comic book files.
        
        Args:
            directory: Path to the directory to scan
            recursive: If True, scan subdirectories recursively
            
        Returns:
            List of paths to comic book files
        """
        comic_files = []
        
        try:
            if recursive:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if self.is_comic_file(file):
                            comic_files.append(os.path.join(root, file))
            else:
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path) and self.is_comic_file(file):
                        comic_files.append(file_path)
            
            logger.info(f"Found {len(comic_files)} comic files in {directory}")
            return comic_files
            
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
            return []
                        
    def find_comic_files(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Alias for scan_directory to maintain backward compatibility.
        
        Args:
            directory: Path to the directory to scan
            recursive: If True, scan subdirectories recursively
            
        Returns:
            List of paths to comic book files
        """
        return self.scan_directory(directory, recursive)
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a comic book file.
        
        Args:
            file_path: Path to the comic book file
            
        Returns:
            Dictionary containing metadata
        """
        try:
            file_path = os.path.abspath(file_path)
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename.lower())[1]
            
            # Default metadata from filename
            metadata = {
                'title': os.path.splitext(filename)[0],
                'year': None,
                'issue_number': None,
                'series': None,
                'subseries': None,
                'publisher': None,
                'authors': [],
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_modified': os.path.getmtime(file_path)
            }
            
            # Parse filename for common patterns
            self._parse_filename(metadata)
            
            # Extract metadata from file based on format
            if ext == '.pdf':
                self._extract_pdf_metadata(file_path, metadata)
            elif ext in ['.cbr', '.cbz']:
                self._extract_comic_archive_metadata(file_path, metadata)
            
            # Extract cover image
            cover_image, cover_type = self.extract_cover_image(file_path)
            if cover_image:
                metadata['cover_image'] = cover_image
                metadata['cover_image_type'] = cover_type
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return {}
    
    def _parse_filename(self, metadata: Dict[str, Any]) -> None:
        """Parse common filename patterns to extract metadata."""
        filename = os.path.splitext(os.path.basename(metadata['file_path']))[0]
        
        # Common patterns:
        # - Series v01 (2010) 001.cbz
        # - Series - 001 - Title (2010).cbz
        # - Series 001 (2010).cbr
        
        # Try to extract year (4 digits in parentheses)
        year_match = re.search(r'\((\d{4})\)', filename)
        if year_match:
            try:
                metadata['year'] = int(year_match.group(1))
                # Remove the year from the title
                filename = filename.replace(year_match.group(0), '').strip()
            except (ValueError, IndexError):
                pass
        
        # Try to extract issue number (digits, possibly with a # or - prefix/suffix)
        issue_match = re.search(r'[#\s-](\d+)(?:[\s-]|$)', filename)
        if issue_match:
            metadata['issue_number'] = issue_match.group(1)
            # Remove the issue number from the title
            filename = filename.replace(issue_match.group(0), ' ').strip()
        
        # The remaining part is likely the series/title
        metadata['series'] = filename.strip()
        metadata['title'] = filename.strip()
    
    def _extract_pdf_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """Extract metadata from PDF files."""
        try:
            with pikepdf.Pdf.open(file_path) as pdf:
                doc_info = pdf.docinfo
                
                if '/Title' in doc_info and doc_info['/Title']:
                    metadata['title'] = str(doc_info['/Title'])
                if '/Author' in doc_info and doc_info['/Author']:
                    authors = str(doc_info['/Author']).split(';')
                    metadata['authors'] = [a.strip() for a in authors if a.strip()]
                if '/Producer' in doc_info and doc_info['/Producer']:
                    metadata['publisher'] = str(doc_info['/Producer'])
                if '/CreationDate' in doc_info and doc_info['/CreationDate']:
                    try:
                        # Try to extract year from PDF creation date (format: D:YYYYMMDD...)
                        date_str = str(doc_info['/CreationDate'])
                        if date_str.startswith('D:') and len(date_str) >= 6:
                            year = int(date_str[2:6])
                            if 1900 <= year <= 2100:  # Sanity check
                                metadata['year'] = year
                    except (ValueError, TypeError):
                        pass
                        
        except Exception as e:
            logger.warning(f"Could not extract PDF metadata from {file_path}: {e}")
    
    def _extract_comic_archive_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """Extract metadata from comic archive files (CBZ, CBR, CBT, CB7)."""
        try:
            # Initialize ComicArchive for the file
            self.comic_archive = comicapi.comicarchive.ComicArchive(file_path)
            
            # Check if it's a valid comic archive
            if not self.comic_archive.seems_to_be_a_comic_archive():
                self.logger.warning(f"File does not appear to be a valid comic archive: {file_path}")
                return None
                
            # Read metadata with default style
            md = self.comic_archive.read_metadata(MetaDataStyle.CIX)
            
            if md:
                # Map comicapi metadata to our metadata format
                if hasattr(md, 'series') and md.series:
                    metadata['series'] = md.series
                if hasattr(md, 'issue') and md.issue:
                    metadata['issue_number'] = str(md.issue)
                if hasattr(md, 'title') and md.title:
                    metadata['title'] = md.title
                if hasattr(md, 'publisher') and md.publisher:
                    metadata['publisher'] = md.publisher
                if hasattr(md, 'volume') and md.volume:
                    try:
                        metadata['volume'] = int(md.volume) if str(md.volume).isdigit() else None
                    except (ValueError, TypeError):
                        pass
                if hasattr(md, 'year') and md.year:
                    try:
                        metadata['year'] = int(md.year) if str(md.year).isdigit() else None
                    except (ValueError, TypeError):
                        pass
                # Handle writers/authors
                if hasattr(md, 'writers') and md.writers:
                    metadata['authors'] = [w.strip() for w in md.writers]
                elif hasattr(md, 'writer') and md.writer:
                    metadata['authors'] = [w.strip() for w in md.writer.split(',')]
                if hasattr(md, 'description') and md.description:
                    metadata['summary'] = md.description
                if hasattr(md, 'notes') and md.notes:
                    metadata['notes'] = md.notes
                if hasattr(md, 'genre') and md.genre:
                    metadata['genre'] = md.genre
                if hasattr(md, 'language') and md.language:
                    metadata['language'] = md.language
                if hasattr(md, 'web_link') and md.web_link:
                    metadata['web'] = md.web_link
                elif hasattr(md, 'webLink') and md.webLink:
                    metadata['web'] = md.webLink
                if hasattr(md, 'page_count') and md.page_count:
                    try:
                        metadata['page_count'] = int(md.page_count)
                    except (ValueError, TypeError):
                        pass
                if hasattr(md, 'black_and_white') and md.black_and_white is not None:
                    metadata['black_and_white'] = md.black_and_white
                elif hasattr(md, 'blackAndWhite') and md.blackAndWhite is not None:
                    metadata['black_and_white'] = md.blackAndWhite
                if hasattr(md, 'manga') and md.manga is not None:
                    metadata['manga'] = md.manga
                if hasattr(md, 'characters') and md.characters:
                    if isinstance(md.characters, str):
                        metadata['characters'] = [c.strip() for c in md.characters.split(',')]
                    else:
                        metadata['characters'] = md.characters
                if hasattr(md, 'teams') and md.teams:
                    if isinstance(md.teams, str):
                        metadata['teams'] = [t.strip() for t in md.teams.split(',')]
                    else:
                        metadata['teams'] = md.teams
                if hasattr(md, 'locations') and md.locations:
                    if isinstance(md.locations, str):
                        metadata['locations'] = [l.strip() for l in md.locations.split(',')]
                    else:
                        metadata['locations'] = md.locations
                if hasattr(md, 'scan_info') and md.scan_info:
                    metadata['scan_info'] = md.scan_info
                elif hasattr(md, 'scanInfo') and md.scanInfo:
                    metadata['scan_info'] = md.scanInfo
                if hasattr(md, 'story_arc') and md.story_arc:
                    metadata['story_arc'] = md.story_arc
                elif hasattr(md, 'storyArc') and md.storyArc:
                    metadata['story_arc'] = md.storyArc
                if hasattr(md, 'series_group') and md.series_group:
                    metadata['series_group'] = md.series_group
                elif hasattr(md, 'seriesGroup') and md.seriesGroup:
                    metadata['series_group'] = md.seriesGroup
                if hasattr(md, 'alternate_series') and md.alternate_series:
                    metadata['alternate_series'] = md.alternate_series
                elif hasattr(md, 'alternateSeries') and md.alternateSeries:
                    metadata['alternate_series'] = md.alternateSeries
                if hasattr(md, 'age_rating') and md.age_rating:
                    metadata['age_rating'] = md.age_rating
                elif hasattr(md, 'ageRating') and md.ageRating:
                    metadata['age_rating'] = md.ageRating
                if hasattr(md, 'community_rating') and md.community_rating is not None:
                    try:
                        metadata['community_rating'] = float(md.community_rating)
                    except (ValueError, TypeError):
                        pass
                elif hasattr(md, 'communityRating') and md.communityRating is not None:
                    try:
                        metadata['community_rating'] = float(md.communityRating)
                    except (ValueError, TypeError):
                        pass
                if hasattr(md, 'review') and md.review:
                    metadata['review'] = md.review
            
            # If no metadata was found, try to extract from filename
            if not any(metadata.values()):
                self._parse_filename(metadata)
                
        except Exception as e:
            self.logger.error(f"Error initializing ComicArchive for {file_path}: {str(e)}")
            return None
            
        finally:
            if hasattr(self, 'comic_archive') and self.comic_archive:
                self.comic_archive = None
            
    def _extract_zip_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """Extract metadata from ZIP/CBZ file."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Look for ComicInfo.xml
                comic_info_files = [f for f in zip_ref.namelist() 
                                  if os.path.basename(f).lower() == 'comicinfo.xml']
                
                if not comic_info_files:
                    logger.debug(f"No ComicInfo.xml found in {file_path}")
                    return
                    
                # Use the first ComicInfo.xml found
                with zip_ref.open(comic_info_files[0]) as xml_file:
                    xml_content = xml_file.read()
                    self._parse_comic_info_xml(xml_content, metadata)
                    
        except zipfile.BadZipFile as e:
            logger.warning(f"Bad ZIP file: {file_path} - {e}")
        except Exception as e:
            logger.warning(f"Error reading ZIP file {file_path}: {e}")
            
    def _extract_rar_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """Extract metadata from RAR/CBR file using py7zr."""
        try:
            with py7zr.SevenZipFile(file_path, 'r') as rar_ref:
                # Get all files in the archive
                all_files = rar_ref.getnames()
                
                # Look for ComicInfo.xml
                comic_info_files = [f for f in all_files 
                                  if os.path.basename(f).lower() == 'comicinfo.xml']
                
                if not comic_info_files:
                    logger.debug(f"No ComicInfo.xml found in {file_path}")
                    return
                    
                # Use the first ComicInfo.xml found
                comic_info_path = comic_info_files[0]
                
                # Extract to a temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Extract just the ComicInfo.xml
                    rar_ref.extract(targets=[comic_info_path], path=temp_dir)
                    temp_file = os.path.join(temp_dir, comic_info_path)
                    
                    # Read the XML content
                    with open(temp_file, 'rb') as f:
                        xml_content = f.read()
                        
                    # Parse the XML content
                    self._parse_comic_info_xml(xml_content, metadata)
                    
        except py7zr.Bad7zFile as e:
            logger.warning(f"Bad RAR file: {file_path} - {e}")
        except Exception as e:
            logger.warning(f"Error reading RAR file {file_path}: {e}")
    
    def _parse_comic_info_xml(self, xml_content: bytes, metadata: Dict[str, Any]) -> None:
        """Parse ComicInfo.xml content and update metadata."""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(xml_content)
            
            # Map XML tags to metadata fields
            tag_mapping = {
                'Title': 'title',
                'Series': 'series',
                'Number': 'issue_number',
                'Volume': 'volume',
                'Year': 'year',
                'Publisher': 'publisher',
                'Summary': 'summary',
                'Notes': 'notes',
                'Genre': 'genre',
                'LanguageISO': 'language',
                'Web': 'web',
                'PageCount': 'page_count',
                'Format': 'format',
                'BlackAndWhite': 'black_and_white',
                'Manga': 'manga',
                'Characters': 'characters',
                'Teams': 'teams',
                'Locations': 'locations',
                'ScanInformation': 'scan_info',
                'StoryArc': 'story_arc',
                'StoryArcNumber': 'story_arc_number',
                'SeriesGroup': 'series_group',
                'AlternateSeries': 'alternate_series',
                'AlternateNumber': 'alternate_number',
                'AlternateCount': 'alternate_count',
                'Count': 'count',
                'AgeRating': 'age_rating',
                'CommunityRating': 'community_rating',
                'MainCharacterOrTeam': 'main_character_or_team',
                'Review': 'review'
            }
            
            # Extract simple fields
            for tag, field in tag_mapping.items():
                elem = root.find(tag)
                if elem is not None and elem.text:
                    # Convert to appropriate type
                    if field == 'year':
                        try:
                            metadata[field] = int(elem.text)
                        except (ValueError, TypeError):
                            pass
                    elif field in ['page_count', 'alternate_number', 'alternate_count', 'count', 'community_rating']:
                        try:
                            metadata[field] = float(elem.text) if '.' in elem.text else int(elem.text)
                        except (ValueError, TypeError):
                            metadata[field] = elem.text
                    elif field == 'black_and_white':
                        metadata[field] = elem.text.lower() in ('yes', 'true', '1')
                    else:
                        metadata[field] = elem.text
            
            # Handle writers/artists/colorists/etc.
            creators = {}
            for writer in root.findall('Writer'):
                if writer.text:
                    creators[writer.text] = 'writer'
            for penciller in root.findall('Penciller'):
                if penciller.text:
                    creators[penciller.text] = 'penciller'
            for inker in root.findall('Inker'):
                if inker.text:
                    creators[inker.text] = 'inker'
            for colorist in root.findall('Colorist'):
                if colorist.text:
                    creators[colorist.text] = 'colorist'
            for letterer in root.findall('Letterer'):
                if letterer.text:
                    creators[letterer.text] = 'letterer'
            for cover_artist in root.findall('CoverArtist'):
                if cover_artist.text:
                    creators[cover_artist.text] = 'cover_artist'
            for editor in root.findall('Editor'):
                if editor.text:
                    creators[editor.text] = 'editor'
            
            # Add to authors list with their roles
            if creators:
                metadata['authors'] = [f"{name} ({role})" for name, role in creators.items()]
            
        except Exception as e:
            logger.warning(f"Error parsing ComicInfo.xml: {e}")
    
    def extract_cover_image(self, file_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Extract the cover image from a comic book file.
        
        Args:
            file_path: Path to the comic book file
            
        Returns:
            Tuple of (image_data, image_type) or (None, None) if no cover found
        """
        try:
            ext = os.path.splitext(file_path.lower())[1]
            
            if ext == '.pdf':
                return self._extract_pdf_cover(file_path)
            elif ext in ['.cbr', '.cbz']:
                return self._extract_archive_cover(file_path)
            else:
                return None, None
                
        except Exception as e:
            logger.warning(f"Error extracting cover from {file_path}: {e}")
            return None, None
    
    def _extract_pdf_cover(self, file_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Extract the first page of a PDF as a cover image."""
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert first page to image using pdftoppm
                temp_image = os.path.join(temp_dir, 'cover.jpg')
                cmd = f'pdftoppm -jpeg -f 1 -l 1 "{file_path}" "{os.path.splitext(temp_image)[0]}"'
                os.system(cmd)
                
                # Check if the image was created
                if os.path.exists(f"{os.path.splitext(temp_image)[0]}-1.jpg"):
                    # Open the image, resize it, and convert to bytes
                    img = Image.open(f"{os.path.splitext(temp_image)[0]}-1.jpg")
                    img.thumbnail(self.max_cover_size, Image.Resampling.LANCZOS)
                    
                    # Convert to bytes
                    img_byte_arr = BytesIO()
                    img.convert('RGB').save(img_byte_arr, format='JPEG', quality=85)
                    return img_byte_arr.getvalue(), 'image/jpeg'
                
        except Exception as e:
            logger.warning(f"Error extracting PDF cover: {e}")
            
        return None, None
    
    def _extract_archive_cover(self, file_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Extract the cover image from a comic archive file."""
        try:
            # Check if it's a RAR file and if we have the tools to handle it
            if file_path.lower().endswith(('.cbr', '.rar')):
                if not rarfile.UNRAR_TOOL_AVAILABLE:
                    self.logger.warning(f"RAR support not properly configured. Cannot extract cover from: {file_path}")
                    self.logger.info("Please install UnRAR or WinRAR and ensure it's in your PATH")
                    return None, None
            
            # Initialize ComicArchive for the file
            self.comic_archive = comicapi.comicarchive.ComicArchive(file_path)
            
            # Check if it's a valid comic archive
            if not hasattr(self.comic_archive, 'seems_to_be_a_comic_archive') or not self.comic_archive.seems_to_be_a_comic_archive():
                self.logger.warning(f"File does not appear to be a valid comic archive: {file_path}")
                return None, None
            
            # Get the first page as cover
            try:
                page_data = self.comic_archive.get_page(0)
                if not page_data:
                    self.logger.warning(f"No pages found in archive: {file_path}")
                    return None, None
                    
                # Process the image data
                return self._process_image_data(page_data, file_path)
                
            except Exception as e:
                self.logger.error(f"Error reading page 0 from {file_path}: {str(e)}")
                return None, None
            
        except Exception as e:
            self.logger.error(f"Error extracting cover from {file_path}: {str(e)}", exc_info=True)
            return None, None
            
        finally:
            if hasattr(self, 'comic_archive') and self.comic_archive:
                self.comic_archive = None
            
    def _extract_rar_cover(self, file_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Extract cover from RAR/CBR file using py7zr.
        
        Args:
            file_path: Path to the RAR/CBR file
            
        Returns:
            Tuple of (image_data, image_type) or (None, None) if extraction fails
        """
        try:
            # Verify file exists and is accessible
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return None, None
                
            if not os.path.isfile(file_path):
                logger.warning(f"Path is not a file: {file_path}")
                return None, None
                
            if os.path.getsize(file_path) == 0:
                logger.warning(f"File is empty: {file_path}")
                return None, None
                
            # Verify it's a RAR file
            if not self._is_rar_file(file_path):
                logger.warning(f"Not a valid RAR file: {file_path}")
                # Check if it's actually a ZIP file
                if zipfile.is_zipfile(file_path):
                    logger.warning(f"File {file_path} is actually a ZIP file, not a RAR")
                    return self._extract_zip_cover(file_path)
                return None, None
                
            # Try to open with py7zr
            try:
                with py7zr.SevenZipFile(file_path, 'r') as rar_ref:
                    # Get all files in the archive
                    all_files = rar_ref.getnames()
                
                # Filter for image files
                image_files = [
                    f for f in all_files 
                    if os.path.splitext(f.lower())[1] in self.image_extensions 
                    and not os.path.basename(f).startswith('.')
                ]
                
                if not image_files:
                    logger.debug(f"No image files found in RAR: {file_path}")
                    return None, None
                    
                # Sort to ensure consistent ordering
                image_files.sort()
                first_image = image_files[0]
                
                # Extract to a temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    rar_ref.extract(targets=[first_image], path=temp_dir)
                    temp_file = os.path.join(temp_dir, first_image)
                    
                    # Read the image data
                    with open(temp_file, 'rb') as f:
                        img_data = f.read()
                        
                    # Process the image
                    return self._process_image_data(img_data, first_image)
                    
            except py7zr.Bad7zFile as e:
                logger.warning(f"Bad RAR file: {file_path} - {e}")
                return None, None
            except Exception as e:
                logger.warning(f"Error reading RAR file {file_path}: {e}")
                return None, None
                
        except Exception as e:
            logger.warning(f"Unexpected error processing RAR file {file_path}: {e}", exc_info=True)
            return None, None
            
    def _extract_zip_cover(self, file_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Extract cover from ZIP/CBZ file.
        
        Args:
            file_path: Path to the ZIP/CBZ file
            
        Returns:
            Tuple of (image_data, image_type) or (None, None) if extraction fails
        """
        try:
            # Verify file exists and is accessible
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return None, None
                
            if not os.path.isfile(file_path):
                logger.warning(f"Path is not a file: {file_path}")
                return None, None
                
            if os.path.getsize(file_path) == 0:
                logger.warning(f"File is empty: {file_path}")
                return None, None
            
            # Check if it's actually a RAR file mislabeled as ZIP
            if self._is_rar_file(file_path):
                logger.warning(f"File {file_path} is actually a RAR file, not a ZIP")
                return self._extract_rar_cover(file_path)
                
            # Verify it's a valid ZIP file
            if not zipfile.is_zipfile(file_path):
                logger.warning(f"Not a valid ZIP file: {file_path}")
                return None, None
                
            # Check if the ZIP file is corrupted
            try:
                with zipfile.ZipFile(file_path, 'r') as test_zip:
                    test_zip.testzip()
            except (zipfile.BadZipFile, zipfile.LargeZipFile) as e:
                logger.warning(f"Corrupted or invalid ZIP file {file_path}: {e}")
                return None, None
                
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Get all image files
                try:
                    image_files = []
                    for f in zip_ref.namelist():
                        try:
                            # Skip directories and hidden files
                            if f.endswith('/') or os.path.basename(f).startswith('.'):
                                continue
                                
                            # Check if file is an image by extension
                            if os.path.splitext(f.lower())[1] in self.image_extensions:
                                # Verify the file can be opened
                                with zip_ref.open(f) as test_file:
                                    test_file.read(4)  # Try reading a small part
                                image_files.append(f)
                        except Exception as e:
                            logger.debug(f"Skipping invalid file {f} in {file_path}: {e}")
                            continue
                    
                    if not image_files:
                        logger.debug(f"No valid image files found in ZIP: {file_path}")
                        return None, None
                        
                    # Sort to ensure consistent ordering
                    image_files.sort()
                    first_image = image_files[0]
                    
                    # Read the image data
                    with zip_ref.open(first_image) as img_file:
                        img_data = img_file.read()
                        if not img_data:
                            logger.warning(f"Empty image file in ZIP: {first_image}")
                            return None, None
                            
                    # Process the image
                    return self._process_image_data(img_data, first_image)
                    
                except Exception as e:
                    logger.warning(f"Error processing files in ZIP {file_path}: {e}")
                    return None, None
                    
        except zipfile.BadZipFile as e:
            logger.warning(f"Bad ZIP file: {file_path} - {e}")
            return None, None
        except Exception as e:
            logger.warning(f"Error reading ZIP file {file_path}: {e}", exc_info=True)
            return None, None
            
    def _is_rar_file(self, file_path: str) -> bool:
        """
        Check if a file is likely a RAR file by its signature and structure.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if the file appears to be a valid RAR archive, False otherwise
        """
        try:
            # Basic file checks
            if not os.path.exists(file_path):
                logger.debug(f"File does not exist: {file_path}")
                return False
                
            if not os.path.isfile(file_path):
                logger.debug(f"Path is not a file: {file_path}")
                return False
                
            if os.path.getsize(file_path) < 7:  # Minimum size for RAR signature
                logger.debug(f"File too small to be a RAR: {file_path}")
                return False
            
            # Check RAR signature
            with open(file_path, 'rb') as f:
                header = f.read(7)
                
                # RAR 1.5 - 4.x signature: Rar!\x1A\x07\x00
                if header.startswith(b'Rar!\x1a\x07\x00'):
                    # Verify block type (must be 0x72 or 0x73 for archive header)
                    block_type = f.read(1)
                    return block_type in (b'\x72', b'\x73')
                
                # RAR 5.0+ signature: Rar!\x1A\x07\x01\x00
                if header.startswith(b'Rar!\x1a\x07\x01'):
                    # RAR 5.0+ has a different header structure
                    return True
                
                # Not a RAR file
                return False
                
        except Exception as e:
            logger.debug(f"Error checking RAR file {file_path}: {e}")
            return False
    
    def _process_image_data(self, img_data: bytes, filename: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Process image data and return as JPEG with MIME type."""
        try:
            # Determine image type from extension
            ext = os.path.splitext(filename.lower())[1]
            if ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            elif ext == '.gif':
                mime_type = 'image/gif'
            elif ext == '.webp':
                mime_type = 'image/webp'
            else:
                mime_type = 'application/octet-stream'
            
            # Process the image
            img = Image.open(BytesIO(img_data))
            img.thumbnail(self.max_cover_size, Image.Resampling.LANCZOS)
            
            # Convert to JPEG for consistency
            img_byte_arr = BytesIO()
            img = img.convert('RGB')  # Convert to RGB for JPEG
            img.save(img_byte_arr, format='JPEG', quality=85)
            return img_byte_arr.getvalue(), 'image/jpeg'
            
        except Exception as img_error:
            logger.warning(f"Error processing image {filename}: {img_error}")
            # Return original if processing fails
            return img_data, mime_type
    
    @staticmethod
    def get_file_mime_type(file_path: str) -> str:
        """Get the MIME type of a file."""
        try:
            mime = magic.Magic(mime=True)
            return mime.from_file(file_path)
        except Exception as e:
            logger.warning(f"Could not determine MIME type of {file_path}: {e}")
            return 'application/octet-stream'
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in megabytes."""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except Exception as e:
            logger.warning(f"Could not get file size for {file_path}: {e}")
            return 0.0
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """Check if a file is an image."""
        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            return file_type.startswith('image/')
        except Exception as e:
            logger.warning(f"Could not check if file is an image: {e}")
            return False
    
    @classmethod
    def is_archive_file(cls, file_path: str) -> bool:
        """Check if a file is a valid archive (ZIP, RAR, etc.)."""
        try:
            # Basic file checks
            if not os.path.exists(file_path):
                logger.warning(f"File does not exist: {file_path}")
                return False
                
            if not os.path.isfile(file_path):
                logger.warning(f"Path is not a file: {file_path}")
                return False
                
            if os.path.getsize(file_path) == 0:
                logger.warning(f"File is empty: {file_path}")
                return False
                
            ext = os.path.splitext(file_path.lower())[1]
            
            # Handle ZIP/CBZ files
            if ext in ['.cbz', '.zip']:
                try:
                    # First try with zipfile for better error messages
                    if zipfile.is_zipfile(file_path):
                        return True
                    
                    # If that fails, try reading the file header
                    with open(file_path, 'rb') as f:
                        header = f.read(4)
                        if header == b'PK\x03\x04':
                            return True
                    
                    logger.warning(f"File {file_path} is not a valid ZIP archive")
                    return False
                    
                except Exception as e:
                    logger.warning(f"Error checking ZIP file {file_path}: {e}")
                    return False
            
            # Handle RAR/CBR files
            elif ext in ['.cbr', '.rar']:
                try:
                    # Try with py7zr first
                    with py7zr.SevenZipFile(file_path, 'r') as _:
                        return True
                except (py7zr.Bad7zFile, py7zr.ArchiveError) as e:
                    logger.warning(f"Invalid RAR file {file_path}: {e}")
                    # Try checking the file signature as a fallback
                    try:
                        with open(file_path, 'rb') as f:
                            header = f.read(7)
                            # RAR 1.5 - 4.x signature: Rar!\x1A\x07\x00
                            if header.startswith(b'Rar!\x1a\x07\x00'):
                                return True
                            # RAR 5.0+ signature: Rar!\x1A\x07\x01\x00
                            if header.startswith(b'Rar!\x1a\x07\x01'):
                                return True
                    except Exception:
                        pass
                    return False
                except Exception as e:
                    logger.warning(f"Error checking RAR file {file_path}: {e}")
                    return False
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking archive file {file_path}: {e}", exc_info=True)
            return False
            
    @classmethod
    def _is_valid_zip_file(cls, file_path: str) -> bool:
        """
        This is now an alias for is_archive_file() for backward compatibility.
        """
        return cls.is_archive_file(file_path)
    
    @staticmethod
    def is_pdf_file(file_path: str) -> bool:
        """Check if a file is a PDF."""
        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            return file_type == 'application/pdf'
        except Exception as e:
            logger.warning(f"Could not check if file is a PDF: {e}")
            return False
            
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scan a single comic book file and extract its metadata.
        
        This is a convenience method that wraps around extract_metadata for backward compatibility.
        
        Args:
            file_path: Path to the comic book file
            
        Returns:
            Dictionary containing the extracted metadata. Returns an empty dict on error.
            The dict may contain an 'error' key with a detailed error message.
        """
        try:
            # Verify file exists and is accessible
            try:
                if not os.path.exists(file_path):
                    return {'error': f'File not found: {file_path}'}
                
                if not os.path.isfile(file_path):
                    return {'error': f'Path is not a file: {file_path}'}
                    
                # Check file size to avoid processing empty files
                if os.path.getsize(file_path) == 0:
                    return {'error': f'File is empty: {file_path}'}
                    
            except OSError as e:
                return {'error': f'Cannot access file {file_path}: {str(e)}'}
            
            # Verify it's a supported comic format
            if not self.is_comic_file(file_path):
                return {'error': f'Unsupported file format: {os.path.splitext(file_path)[1]}'}
            
            # Extract and return metadata
            metadata = self.extract_metadata(file_path)
            if not metadata:
                return {'error': 'Failed to extract metadata from file'}
                
            return metadata
            
        except Exception as e:
            error_msg = f'Error scanning file {file_path}: {str(e)}'
            logger.error(error_msg, exc_info=True)  # Log full traceback
            return {'error': error_msg}
