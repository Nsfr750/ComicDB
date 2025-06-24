import sys
import os
import traceback

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def verify_unrar_setup() -> bool:
    """Verify that UnRAR is properly set up for handling CBR files."""
    from struttura.unrar_utils import setup_unrar, is_rar_supported, find_unrar_executable
    
    print("\n=== Checking RAR Support ===")
    
    # First check if we can find the UnRAR executable
    unrar_path = find_unrar_executable()
    if unrar_path:
        print(f"✓ Found UnRAR at: {unrar_path}")
    else:
        print("⚠️  Could not find UnRAR executable in standard locations")
    
    # Try to set up RAR support
    success, message = setup_unrar()
    print(f"Setup result: {message}")
    
    if success:
        print("✓ RAR support is properly configured")
        return True
    
    # If setup failed, try to diagnose the issue
    print("\n⚠️  RAR Support Issues:")
    print(f"- {message}")
    
    # Check if rarfile is installed
    try:
        import rarfile
    except ImportError:
        print("\n❌ The 'rarfile' package is not installed.")
        print("   Install it with: pip install rarfile")
        print("   Then install either WinRAR or UnRAR as described below.")
    
    print("\nTo enable full RAR support, please install one of the following:")
    print("1. WinRAR (recommended): https://www.win-rar.com/")
    print("   - Make sure to install the 64-bit version if you're on 64-bit Windows")
    print("   - During installation, select 'Add to PATH' or add the installation directory to your system PATH")
    print("2. UnRAR (lightweight): https://www.rarlab.com/rar/UnRAR.exe")
    print("   - Download and extract to a directory in your PATH")
    print("\nAfter installation, restart the application.")
    print("Note: The application will continue to work, but some RAR files may not be accessible.")
    
    # Check if we can use RAR support in a limited way
    supported, support_msg = is_rar_supported()
    if supported:
        print(f"\nℹ️  Limited RAR support is available: {support_msg}")
        return True
    
    return False

def init_database() -> bool:
    """Initialize the database and create tables if they don't exist."""
    db = None
    try:
        from struttura.database import ComicDatabase
        
        # Initialize SQLite database (will be created if it doesn't exist)
        db_path = os.path.join(project_root, 'comicdb.sqlite')
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

def main():
    from struttura.database import ComicDatabase
    db = None
    
    try:
        print("Starting ComicDB...")
        
        # Verify UnRAR setup
        if not verify_unrar_setup():
            print("Warning: RAR file support may be limited. Continuing anyway...")
        
        print("Setting up logging...")
        from struttura.logger import setup_global_exception_logging
        setup_global_exception_logging()
        
        # Initialize database
        print("Initializing database...")
        db_path = os.path.join(project_root, 'comicdb.sqlite')
        db = ComicDatabase(database=db_path, db_type='sqlite')
        
        if not db.is_connected():
            print("Error: Failed to connect to the database. Exiting...")
            input("Premi Invio per uscire...")
            return
            
        # Create tables if they don't exist
        if not db.create_tables(force_recreate=False):
            print("Error: Failed to create database tables. Exiting...")
            input("Premi Invio per uscire...")
            return
        
        print("Importing MainWindow...")
        from gui.main_window import MainWindow
        
        print("Creating main window...")
        app = MainWindow(db_config={'database': db_path, 'db_type': 'sqlite'})
        
        # Check for updates on startup (non-blocking)
        try:
            from struttura.updates import UpdateChecker
            from struttura.version import get_version
            
            def do_update_check():
                try:
                    # Create and configure the update checker
                    checker = UpdateChecker(
                        current_version=get_version(),
                        update_url="https://api.github.com/repos/Nsfr750/ComicDB/releases/latest"
                    )
                    update_available, update_info = checker.check_for_updates(app, force_check=False)
                    if update_available and update_info:
                        checker.show_update_dialog(app, update_info)
                except Exception as e:
                    print(f"Error during update check: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Schedule the update check after the UI is shown
            app.after(3000, do_update_check)
            
        except Exception as e:
            print(f"Error setting up update check: {e}")
            import traceback
            traceback.print_exc()
        
        print("Starting main loop...")
        app.mainloop()
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"Errore in main: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        input("Premi Invio per uscire...")
        
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
                import traceback
                traceback.print_exc()
            finally:
                db = None

if __name__ == "__main__":
    print("Starting ComicDB...")
    main()
    print("ComicDB has exited.")
