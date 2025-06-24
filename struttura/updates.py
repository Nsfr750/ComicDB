"""
Update checking functionality for the ComicDB application.
"""
import logging
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Tuple, Dict, Any
import requests
import json
from pathlib import Path
import os
from datetime import datetime, timedelta

# Get the application directory
APP_DIR = Path(__file__).parent.parent
UPDATES_FILE = APP_DIR / 'updates.json'
DEFAULT_UPDATE_URL = "https://api.github.com/repos/Nsfr750/ComicDB/releases/latest"

# Configure logger
logger = logging.getLogger(__name__)

# Set a user agent to prevent rate limiting
DEFAULT_HEADERS = {
    'User-Agent': 'ComicDB-Update-Checker/1.0',
    'Accept': 'application/vnd.github.v3+json'
}

class UpdateError(Exception):
    """Custom exception for update-related errors."""
    pass

class UpdateChecker:
    """Handles checking for application updates."""
    
    def __init__(self, current_version: str, config_path: Optional[Path] = None, 
                 update_url: Optional[str] = None):
        """Initialize the update checker.
        
        Args:
            current_version: The current version of the application.
            config_path: Path to the configuration file (optional).
            update_url: Custom URL to check for updates (optional).
        """
        self.current_version = current_version
        self.config_path = config_path or UPDATES_FILE
        self.update_url = update_url or os.getenv('COMICDB_UPDATE_URL') or DEFAULT_UPDATE_URL
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the update configuration.
        
        Returns:
            Dictionary containing the configuration.
        """
        default_config = {
            'last_checked': None,
            'last_version': None,
            'dont_ask_until': None,
            'update_url': self.update_url
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config.update(config)
                    return default_config
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error loading update config: {e}")
        
        return default_config
    
    def _save_config(self) -> None:
        """Save the update configuration."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except (OSError, TypeError) as e:
            logger.error(f"Error saving update config: {e}")
            # Try to save a minimal config if full save fails
            try:
                minimal_config = {
                    'last_checked': self.config.get('last_checked'),
                    'last_version': self.config.get('last_version'),
                    'dont_ask_until': self.config.get('dont_ask_until')
                }
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(minimal_config, f, indent=2, ensure_ascii=False)
            except Exception as e2:
                logger.error(f"Failed to save minimal config: {e2}")
    
    def _should_check_for_updates(self) -> bool:
        """Determine if we should check for updates based on last check time."""
        if not self.config.get('last_checked'):
            return True
            
        try:
            last_checked = datetime.fromisoformat(self.config['last_checked'].replace('Z', '+00:00'))
            # Check at most once every 6 hours
            return datetime.utcnow() - last_checked > timedelta(hours=6)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid last_checked timestamp: {e}")
            return True
    
    def check_for_updates(self, parent: Optional[tk.Tk] = None, 
                         force_check: bool = False) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check for available updates.
        
        Args:
            parent: Parent window for dialogs.
            force_check: If True, skip the cache and force a check.
            
        Returns:
            Tuple of (update_available, update_info)
        """
        # Skip if we've checked recently and this isn't a forced check
        if not force_check and not self._should_check_for_updates():
            logger.debug("Skipping update check - checked recently")
            return False, None
            
        try:
            logger.info(f"Checking for updates from {self.update_url}")
            
            # Add timeout and headers to prevent hanging requests
            response = requests.get(
                self.update_url,
                headers=DEFAULT_HEADERS,
                timeout=10
            )
            
            # Handle rate limiting
            if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                if int(response.headers['X-RateLimit-Remaining']) == 0:
                    reset_time = datetime.fromtimestamp(int(response.headers.get('X-RateLimit-Reset', 0)))
                    logger.warning(f"GitHub API rate limit reached. Resets at {reset_time}")
                    if force_check and parent:
                        messagebox.showwarning(
                            'Rate Limit Reached',
                            'GitHub API rate limit reached. Please try again later.',
                            parent=parent
                        )
                    return False, None
            
            # Handle 404 - repository or release not found
            if response.status_code == 404:
                logger.warning(f"Update check failed: Repository or release not found at {self.update_url}")
                if force_check and parent:
                    messagebox.showwarning(
                        'Update Check Failed',
                        'Could not find the update repository. The URL may be incorrect or the repository may be private.',
                        parent=parent
                    )
                return False, None
                
            # Handle other HTTP errors
            response.raise_for_status()
            
            try:
                release = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {e}")
                if force_check and parent:
                    messagebox.showerror(
                        'Update Error',
                        'Received invalid response from the update server.',
                        parent=parent
                    )
                return False, None
                
            if not isinstance(release, dict) or 'tag_name' not in release:
                logger.error(f"Invalid release data received: {release}")
                return False, None
                
            # Update last checked time
            self.config['last_checked'] = datetime.utcnow().isoformat() + 'Z'
            self.config['last_version'] = release['tag_name'].lstrip('v')
            self._save_config()
            
            latest_version = self.config['last_version']
            
            if self._version_compare(latest_version, self.current_version) > 0:
                logger.info(f"Update available: {latest_version}")
                return True, {
                    'version': latest_version,
                    'url': release.get('html_url', ''),
                    'notes': release.get('body', ''),
                    'published_at': release.get('published_at', ''),
                    'is_prerelease': release.get('prerelease', False),
                    'assets': release.get('assets', [])
                }
            else:
                logger.info(f"No updates available (current: {self.current_version}, latest: {latest_version})")
                if force_check and parent:
                    messagebox.showinfo(
                        'No Updates',
                        f'You are using the latest version ({self.current_version}).',
                        parent=parent
                    )
                return False, None
                
        except requests.RequestException as e:
            logger.error(f"Error checking for updates: {e}", exc_info=True)
            if force_check and parent:
                messagebox.showerror(
                    'Update Error',
                    f'Failed to check for updates: {str(e)}\n\nURL: {self.update_url}',
                    parent=parent
                )
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error during update check: {e}", exc_info=True)
            if force_check and parent:
                messagebox.showerror(
                    'Update Error',
                    f'An unexpected error occurred while checking for updates: {str(e)}',
                    parent=parent
                )
            return False, None
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """Compare two version strings.
        
        Returns:
            1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        def parse_version(v: str) -> list:
            return [int(x) for x in v.split('.')]
            
        try:
            v1_parts = parse_version(v1)
            v2_parts = parse_version(v2)
            
            # Pad with zeros if versions have different lengths
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
            
        except (ValueError, AttributeError):
            # Fallback to string comparison if version format is invalid
            return (v1 > v2) - (v1 < v2)
    
    def show_update_dialog(self, parent: tk.Tk, update_info: dict) -> None:
        """Show a dialog with update information."""
        from tkinter import ttk
        
        dialog = tk.Toplevel(parent)
        dialog.title("Update Available")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = 500
        height = 300
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update info
        ttk.Label(
            main_frame,
            text=f"Version {update_info['version']} is available!",
            font=('TkDefaultFont', 12, 'bold')
        ).pack(pady=(0, 10))
        
        # Release notes
        notes_frame = ttk.LabelFrame(main_frame, text="Release Notes", padding=5)
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        text = tk.Text(
            notes_frame,
            wrap=tk.WORD,
            width=60,
            height=10,
            font=('TkDefaultFont', 9)
        )
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text.insert('1.0', update_info['notes'])
        text.config(state='disabled')
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        ttk.Button(
            btn_frame,
            text="Download Now",
            command=lambda: self._open_download(update_info['url'])
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Remind Me Later",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Make the dialog modal
        dialog.wait_window()
    
    def _open_download(self, url: str) -> None:
        """Open the download URL in the default browser."""
        import webbrowser
        webbrowser.open(url)
        self.dialog.destroy()


def check_for_updates(parent: Optional[tk.Tk] = None, current_version: str = "__version__", force_check: bool = False) -> None:
    """Check for application updates and show a dialog if an update is available.
    
    Args:
        parent: Parent window for dialogs.
        current_version: Current application version.
        force_check: If True, skip the cache and force a check.
    """
    checker = UpdateChecker(current_version)
    update_available, update_info = checker.check_for_updates(parent, force_check=force_check)
    
    if update_available and update_info:
        checker.show_update_dialog(parent, update_info)
