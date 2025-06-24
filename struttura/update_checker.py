"""Simple update checker for ComicDB."""

import logging
import webbrowser
from tkinter import messagebox
from typing import Optional, Tuple, Dict, Any
import json
import urllib.request
import urllib.error
from packaging import version

# Constants
GITHUB_RELEASES_URL = "https://api.github.com/repos/Nsfr750/ComicDB/releases/latest"

def check_for_updates(parent, current_version: str) -> None:
    """
    Check for updates in the background and notify the user if a new version is available.
    
    Args:
        parent: The parent window for dialogs
        current_version: Current version string (e.g., '1.0.0')
    """
    try:
        latest_version, release_url = _get_latest_release_info()
        
        if latest_version and version.parse(latest_version) > version.parse(current_version):
            # New version available
            if _ask_update_confirmation(parent, current_version, latest_version):
                webbrowser.open(release_url)
    except Exception as e:
        logging.error(f"Error checking for updates: {e}")

def _get_latest_release_info() -> Tuple[Optional[str], Optional[str]]:
    """
    Get the latest release version and URL from GitHub.
    
    Returns:
        Tuple of (version_string, release_url) or (None, None) if not found
    """
    try:
        with urllib.request.urlopen(GITHUB_RELEASES_URL) as response:
            data = json.loads(response.read().decode())
            return data.get('tag_name', '').lstrip('v'), data.get('html_url', '')
    except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        logging.warning(f"Could not check for updates: {e}")
        return None, None

def _ask_update_confirmation(parent, current_version: str, new_version: str) -> bool:
    """
    Ask the user if they want to download the new version.
    
    Returns:
        bool: True if user wants to download the update
    """
    message = (
        f"A new version of ComicDB is available!\n\n"
        f"Current version: {current_version}\n"
        f"New version: {new_version}\n\n"
        "Would you like to download it now?"
    )
    
    return messagebox.askyesno(
        title="Update Available",
        message=message,
        parent=parent
    )
