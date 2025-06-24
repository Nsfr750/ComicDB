import sys
import os
import traceback

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
        print("Setting up logging...")
        from struttura.logger import setup_global_exception_logging
        setup_global_exception_logging()
        
        # Initialize database
        print("Initializing database...")
        if not init_database():
            print("Failed to initialize database. Exiting...")
            input("Press Enter to exit...")
            return
        
        print("Importing MainWindow...")
        from gui.main_window import MainWindow
        
        print("Creating main window...")
        app = MainWindow()
        
        # Check for updates on startup (non-blocking)
        try:
            from struttura.updates import check_for_updates
            from struttura.version import get_version
            
            # Use after() to schedule the update check after the UI is shown
            app.after(3000, lambda: check_for_updates(app, get_version()))
        except Exception as e:
            print(f"Error setting up update check: {e}")
        
        print("Starting main loop...")
        app.mainloop()
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        input("Press Enter to exit...")
        
    finally:
        # Clean up database connections
        if db:
            if hasattr(db, 'close_all_connections'):
                db.close_all_connections()
            else:
                db.close()

if __name__ == "__main__":
    print("Starting ComicDB...")
    main()
    print("ComicDB has exited.")
