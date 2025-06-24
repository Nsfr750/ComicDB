"""
Utility functions for handling UnRAR setup and RAR file operations.
"""
import os
import sys
import ctypes
import logging
from typing import Optional, Tuple, List

# Set up logging
logger = logging.getLogger(__name__)

# Global flag to track if we've already set up the UnRAR library
_UNRAR_INITIALIZED = False

# Known UnRAR executable locations for different platforms
if sys.platform == 'win32':
    # Prioritize 64-bit UnRAR on Windows
    UNRAR_PATHS = [
        # 64-bit paths first
        r"C:\Program Files\WinRAR\UnRAR.exe",
        # 32-bit paths
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        # Avoid using UnrarDLL as it might be 32-bit
    ]
    
    # Only add DLL path if it's explicitly requested
    if os.environ.get('USE_UNRAR_DLL', '').lower() == 'true':
        UNRAR_PATHS.extend([
            r"C:\Windows\System32\UnRAR.dll",
            r"C:\Windows\SysWOW64\UnRAR.dll"
        ])
else:
    # Unix-like systems
    UNRAR_PATHS = [
        "/usr/bin/unrar",
        "/usr/local/bin/unrar",
        "/usr/bin/unrar-free",
        "/usr/local/bin/unrar-free"
    ]

def setup_unrar() -> Tuple[bool, str]:
    """
    Set up the UnRAR library for RAR file support.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    global _UNRAR_INITIALIZED
    
    if _UNRAR_INITIALIZED:
        return True, "UnRAR library already initialized"
    
    # Try to find UnRAR executable
    unrar_path = find_unrar_executable()
    if not unrar_path:
        return False, "Could not find UnRAR executable. Please install WinRAR or UnRAR."
    
    logger.info(f"Found UnRAR at: {unrar_path}")
    
    # Set up rarfile to use the found UnRAR executable
    try:
        import rarfile
        
        # Set the UNRAR_TOOL to the full path
        rarfile.UNRAR_TOOL = unrar_path
        
        # For DLLs, we need to set the PATH to include the directory containing the DLL
        if unrar_path.lower().endswith('.dll'):
            unrar_dir = os.path.dirname(unrar_path)
            os.environ['PATH'] = f"{unrar_dir};{os.environ.get('PATH', '')}"
            
            # Try to load the DLL directly to verify it's accessible
            try:
                ctypes.WinDLL(unrar_path)
            except Exception as dll_error:
                return False, f"Failed to load UnRAR DLL: {str(dll_error)}"
        
        # Test if rarfile can find the unrar tool
        try:
            if rarfile.tool_setup():
                _UNRAR_INITIALIZED = True
                return True, f"Successfully set up RAR file support using: {unrar_path}"
        except Exception as tool_error:
            logger.warning(f"rarfile.tool_setup() failed: {tool_error}")
            # Continue to try other methods
        
        # If we get here, tool_setup failed, but we can still try to use the DLL directly
        if unrar_path.lower().endswith('.dll'):
            try:
                # Try to use the DLL directly
                ctypes.WinDLL(unrar_path)
                _UNRAR_INITIALIZED = True
                return True, f"Using UnRAR DLL directly: {unrar_path}"
            except Exception as dll_error:
                return False, f"Failed to use UnRAR DLL directly: {str(dll_error)}"
        
        return False, "Found UnRAR but failed to initialize it properly"
        
    except Exception as e:
        return False, f"Error setting up RAR support: {str(e)}"

def find_unrar_executable() -> Optional[str]:
    """
    Try to find the UnRAR executable on the system.
    
    Returns:
        Optional[str]: Path to the UnRAR executable if found, None otherwise
    """
    # Check common installation paths
    for path in UNRAR_PATHS:
        if os.path.exists(path):
            return path
    
    # Check if unrar is in PATH
    if sys.platform == 'win32':
        import shutil
        if shutil.which('unrar'):
            return 'unrar'
    else:
        # On Unix-like systems, try 'which'
        for cmd in ['unrar', 'unrar-free']:
            path = shutil.which(cmd)
            if path:
                return path
    
    return None

def is_rar_supported() -> Tuple[bool, str]:
    """
    Check if RAR file support is available.
    
    Returns:
        Tuple[bool, str]: (is_supported, message)
    """
    try:
        # First try to use the unrar package directly
        try:
            from unrar import unrarlib
            return True, "RAR support is available via unrar package"
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Error loading unrar package: {e}")
        
        # Try to use rarfile with our setup
        try:
            import rarfile
            
            # Try to find the UnRAR executable (avoiding 32-bit DLLs)
            unrar_path = find_unrar_executable()
            if unrar_path:
                # On Windows, avoid using 32-bit DLLs
                if sys.platform == 'win32' and 'x86' in unrar_path and unrar_path.lower().endswith('.dll'):
                    return False, "Found 32-bit UnRAR DLL which is not compatible with 64-bit Python"
                
                rarfile.UNRAR_TOOL = unrar_path
                if rarfile.tool_setup():
                    return True, f"RAR support is available via rarfile using {unrar_path}"
                
                # If tool_setup failed, try to see if we can use the DLL directly (64-bit only)
                if sys.platform == 'win32' and unrar_path.lower().endswith('.dll'):
                    try:
                        # Only try to load the DLL if it's in a 64-bit location
                        if 'x86' not in unrar_path and 'SysWOW64' not in unrar_path:
                            ctypes.WinDLL(unrar_path)
                            return True, f"RAR support is available via direct DLL: {unrar_path}"
                    except Exception as dll_error:
                        logger.warning(f"Failed to load UnRAR DLL directly: {dll_error}")
            
            return False, "RAR support is not properly configured. Could not find or load UnRAR."
            
        except ImportError:
            return False, "The 'rarfile' package is required for RAR support. Install with: pip install rarfile"
        except Exception as e:
            logger.error(f"Error checking rarfile support: {e}")
            return False, f"Error checking RAR support: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error in is_rar_supported: {e}")
        return False, f"Unexpected error checking RAR support: {str(e)}"
    
    return False, ("No RAR support available. Please install one of the following:\n"
                  "1. WinRAR (64-bit): https://www.win-rar.com/\n"
                  "2. Python rarfile package: pip install rarfile")
