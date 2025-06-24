import sys
import os
import traceback

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tkinter as tk
from tkinter import ttk, messagebox
import os
import configparser
import logging
import locale
import gettext

# Local imports
from struttura.database import ComicDatabase
from struttura.logger import setup_global_exception_logging, log_info, log_error, log_warning
from struttura.config import load_config, save_config, get_config_path, get_database_path
from struttura.version import get_version
from gui.main_window import MainWindow
from gui.splash import SplashScreen
from struttura.comic_scanner import ComicScanner
from struttura.lang import set_language, get_language, tr
from struttura.update_checker import check_for_updates
from struttura.unrar_utils import find_unrar_executable, setup_unrar, is_rar_supported

def verify_unrar_setup() -> bool:
    """Verify that UnRAR is properly set up for handling CBR files."""
    print("\n=== Checking RAR Support ===")
    
    # First check if we can find the UnRAR executable
    unrar_path = find_unrar_executable()
    if unrar_path:
        print(f"✓ Found UnRAR at: {unrar_path}")
    else:
        print("⚠️  Could not find UnRAR executable in standard locations")
    
    # Check if RAR is supported
    rar_supported, message = is_rar_supported()
    print(f"RAR support status: {message}")
    
    # Set up RAR support
    success, setup_msg = setup_unrar()
    print(f"Setup result: {setup_msg}")
    
    if success:
        print("✓ RAR support is properly configured")
    
    return success and rar_supported and unrar_path is not None

def init_database() -> bool:
    """Initialize the database and create tables if they don't exist."""
    db = None
    try:
        from struttura.database import ComicDatabase
        
        # Initialize SQLite database (will be created if it doesn't exist)
        db_path = os.path.join(os.path.dirname(__file__), 'comicdb.sqlite')
        print(f"Initializing database at: {db_path}")
        
        # Create database instance and connect
        db = ComicDatabase(database=db_path, db_type='sqlite')
        
        if not db.is_connected():
            print("Error: Failed to connect to the database.")
            return False
            
        # Force recreation of all tables with the new schema
        print("Creating database tables...")
        if not db.create_tables(force_recreate=True):
            print("Error: Failed to create database tables.")
            return False
            
        print("Database tables created successfully with the latest schema.")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        traceback.print_exc()
        return False
    finally:
        if db:
            db.close()

def show_main_application(root, config):
    """Show the main application window."""
    # Configure the root window
    root.title(f"ComicDB {get_version()}")
    
    # Set application icon
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
        else:
            log_warning(f"Icon file not found at: {icon_path}")
    except Exception as e:
        log_error(f"Error setting application icon: {e}")
    
    # Create the main application
    app = MainWindow(root, config)
    
    # Set up the UI - this is now done in MainWindow.__init__
    
    # Center the window
    window_width = 1200
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Check for updates in the background
    if config.get('check_updates', True):
        check_for_updates(root, get_version())

def main():
    """Main entry point for the application."""
    # Initialize logging first
    setup_global_exception_logging()
    log_info(f"Starting ComicDB {get_version()}")
    
    # Verify unrar is set up
    if not verify_unrar_setup():
        log_error("unrar is not properly set up. Please install it and try again.")
        messagebox.showerror(
            "Error",
            "unrar is required but not found. Please install it and try again."
        )
        return
    
    # Load configuration
    config = load_config()
    
    # Set up language - use 'language' key from config, default to 'en' if not found
    set_language(config.get('language', 'en'))
    log_info(f"Language set to: {get_language()}")
    # Save the language to config if not already set
    if 'language' not in config:
        config['language'] = get_language()
        save_config(config)
    
    # Create the main application window
    root = tk.Tk()
    root.title(f"ComicDB {get_version()}")
    
    # Set application icon if it exists
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        log_error(f"Error setting application icon: {e}")
    
    # Hide the root window initially
    root.withdraw()
    
    # Show splash screen
    splash = SplashScreen(root, duration=5000)  # Show for 5 seconds
    
    # Schedule the main application to start after splash screen
    def show_main():
        # Show the main window
        root.deiconify()
        show_main_application(root, config)
        
    root.after(2000, show_main)  # Show main window after splash duration
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    print("Starting ComicDB...")
    try:
        main()
    except Exception as e:
        print(f"Error in main: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        input("Press Enter to exit...")
        
    finally:
        # Clean up database connections
        if 'db' in locals() and db is not None:
            print("Cleaning up database connections...")
            try:
                # Commit any pending transactions
                if hasattr(db, 'connection') and db.connection:
                    try:
                        db.connection.commit()
                        print("Committed pending transactions")
                    except Exception as commit_error:
                        print(f"Error committing transactions: {commit_error}")
                
                # Close all connections
                if hasattr(db, 'close_all_connections'):
                    print("Closing all database connections...")
                    db.close_all_connections()
                elif hasattr(db, 'close'):
                    print("Closing database connection...")
                    db.close()
                print("Database connections closed successfully")
                
            except Exception as e:
                print(f"Error during database cleanup: {e}")
                traceback.print_exc()
            finally:
                db = None
    main()
    print("ComicDB has exited.")
