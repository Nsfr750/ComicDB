import os
import sqlite3
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, Union, Callable, Any, TypeVar, cast
from pathlib import Path
import pandas as pd
import json
import csv
import io
import threading
from functools import wraps

# Import MySQL connector only if needed
try:
    from mysql.connector import Error as MySQLError
except ImportError:
    # Define a dummy Error class if mysql-connector-python is not installed
    class MySQLError(Exception):
        pass

# Thread-local storage for database connections
_thread_local = threading.local()

def with_connection(method: Callable) -> Callable:
    """Decorator to ensure a database connection is available for the method."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # For SQLite, get or create a thread-local connection
        if self.db_type == 'sqlite':
            if not hasattr(_thread_local, 'connection') or _thread_local.connection is None:
                _thread_local.connection = sqlite3.connect(self.database, check_same_thread=False)
                _thread_local.connection.row_factory = sqlite3.Row
            self.connection = _thread_local.connection
            
        # For MySQL, use the existing connection logic
        elif self.db_type == 'mysql' and (self.connection is None or not self.connection.is_connected()):
            self.connect()
            
        return method(self, *args, **kwargs)
    return wrapper

logger = logging.getLogger(__name__)

class ComicDatabase:
    def __init__(self, database: str = "comicdb.sqlite", db_type: str = "sqlite",
                 host: str = None, user: str = None, password: str = None):
        """Initialize the database connection.
        
        Args:
            database: Database name (for SQLite) or database name (for MySQL)
            db_type: Type of database ('sqlite' or 'mysql')
            host: Database host (for MySQL)
            user: Database user (for MySQL)
            password: Database password (for MySQL)
        """
        self.db_type = db_type.lower()
        self.database = database
        self.connection = None
        
        if self.db_type == 'mysql':
            self.config = {
                'host': host or 'localhost',
                'user': user or 'root',
                'password': password or '',
                'database': database,
                'raise_on_warnings': True
            }
        
        self.connect()

    def connect(self) -> bool:
        """Establish a connection to the database."""
        try:
            if self.db_type == 'sqlite':
                # Ensure the database file and directory exist
                db_dir = os.path.dirname(self.database)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                
                # Create the database file if it doesn't exist
                if not os.path.exists(self.database):
                    open(self.database, 'a').close()
                
                # Create a new connection
                self.connection = sqlite3.connect(
                    self.database,
                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                )
                self.connection.row_factory = sqlite3.Row
                
                # Enable foreign key support
                cursor = self.connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                self.connection.commit()
                cursor.close()
                
                logger.info(f"Connected to SQLite database: {self.database}")
                return True
                
            else:  # MySQL
                import mysql.connector
                from mysql.connector import Error
                self.connection = mysql.connector.connect(**self.config)
                logger.info("Connected to MySQL database")
                return True
                
        except Exception as e:
            logger.error(f"Error connecting to database: {e}", exc_info=True)
            self.connection = None
            return False

    def close(self) -> None:
        """Close the database connection."""
        if not self.connection:
            return
            
        try:
            if self.db_type == 'mysql':
                if self.connection.is_connected():
                    self.connection.close()
                    logger.info("MySQL database connection closed")
            else:  # SQLite
                # For SQLite, ensure all statements are completed
                self.connection.commit()
                self.connection.close()
                logger.info("SQLite database connection closed")
                
        except Exception as e:
            logger.error(f"Error closing database connection: {e}", exc_info=True)
        finally:
            self.connection = None
    
    def close_all_connections(self) -> None:
        """Close all SQLite connections (for cleanup)."""
        if hasattr(_thread_local, 'connection') and _thread_local.connection is not None:
            try:
                _thread_local.connection.close()
                logger.info("SQLite connection closed")
            except Exception as e:
                logger.error(f"Error closing SQLite connection: {e}")
            finally:
                _thread_local.connection = None
            
    def is_connected(self) -> bool:
        """Check if the database connection is active."""
        if not self.connection:
            return False
        try:
            if self.db_type == 'sqlite':
                # For SQLite, try a simple query
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
            else:
                # For MySQL, use the ping method
                return self.connection.is_connected()
        except Exception:
            return False

    @with_connection
    def get_comics(self, search: str = None, publisher: str = None, 
                   series: str = None) -> List[Dict[str, Any]]:
        """Get comics from the database with optional filters.
        
        Args:
            search: Search term to match against title, series, or description
            publisher: Filter by publisher
            series: Filter by series
            
        Returns:
            List of comic dictionaries
        """
        query = """
            SELECT 
                c.id, c.title, c.year, c.issue_number, c.file_path,
                c.cover_image, c.cover_image_type, c.last_updated,
                s.name as series,
                p.name as publisher
            FROM comics c
            LEFT JOIN series s ON c.series_id = s.id
            LEFT JOIN publishers p ON s.publisher_id = p.id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (c.title LIKE ? OR s.name LIKE ? OR c.file_path LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
            
        if publisher:
            query += " AND p.name = ?"
            params.append(publisher)
            
        if series:
            query += " AND s.name = ?"
            params.append(series)
            
        query += " ORDER BY s.name, CAST(c.issue_number AS INTEGER)"
        
        try:
            return self.execute_query(query, params, fetch=True) or []
        except Exception as e:
            logger.error(f"Error getting comics: {e}")
            return []

    @with_connection
    def execute_query(self, query: str, params: tuple = None, 
                     fetch: bool = False) -> Optional[Union[List[Dict[str, Any]], int]]:
        """Execute a SQL query and optionally fetch results."""
        cursor = None
        try:
            if self.db_type == 'sqlite':
                cursor = self.connection.cursor()
                # Convert MySQL %s placeholders to SQLite ? placeholders
                if params:
                    cursor.execute(query.replace('%s', '?'), params)
                else:
                    cursor.execute(query)
                self.connection.commit()
                
                if fetch:
                    # Convert sqlite3.Row objects to dicts for consistency
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows] if rows else []
            else:  # MySQL
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                if fetch:
                    return cursor.fetchall()
            self.connection.commit()
            return None
            
        except (sqlite3.Error, MySQLError) as e:
            logger.error(f"Error executing query: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def create_tables(self, force_recreate: bool = False) -> bool:
        """Create the necessary tables if they don't exist.
        
        Args:
            force_recreate: If True, drop and recreate all tables if they exist
        """
        cursor = None
        try:
            # Ensure we have a valid connection
            if not self.connection:
                if not self.connect():
                    logger.error("Failed to establish database connection")
                    return False
            
            cursor = self.connection.cursor()
            
            if force_recreate:
                # Drop tables in reverse order to respect foreign key constraints
                tables_to_drop = [
                    'comic_authors',
                    'comics',
                    'subseries',
                    'series',
                    'authors',
                    'publishers'
                ]
                for table in tables_to_drop:
                    try:
                        cursor.execute(f"DROP TABLE IF EXISTS {table}")
                        logger.debug(f"Dropped table: {table}")
                    except Exception as e:
                        logger.warning(f"Could not drop table {table}: {e}")
                self.connection.commit()
            
            if self.db_type == 'sqlite':
                tables = ["""
                    CREATE TABLE IF NOT EXISTS publishers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS series (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        publisher_id INTEGER,
                        FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE SET NULL,
                        UNIQUE (name, publisher_id)
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS subseries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        series_id INTEGER NOT NULL,
                        FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
                        UNIQUE (name, series_id)
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS authors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS comics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        series_id INTEGER,
                        subseries_id INTEGER,
                        issue_number TEXT,
                        year INTEGER,
                        publisher TEXT,
                        summary TEXT,
                        page_count INTEGER,
                        file_path TEXT NOT NULL UNIQUE,
                        file_size INTEGER,
                        file_modified REAL,
                        file_created REAL,
                        file_extension TEXT,
                        isbn TEXT,
                        notes TEXT,
                        cover_image BLOB,
                        cover_image_type TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET NULL,
                        FOREIGN KEY (subseries_id) REFERENCES subseries(id) ON DELETE SET NULL
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS comic_authors (
                        comic_id INTEGER NOT NULL,
                        author_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        PRIMARY KEY (comic_id, author_id, role),
                        FOREIGN KEY (comic_id) REFERENCES comics(id) ON DELETE CASCADE,
                        FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
                    )"""]
                
                # SQLite specific triggers
                triggers = ["""
                    CREATE TRIGGER IF NOT EXISTS update_comics_timestamp
                    AFTER UPDATE ON comics
                    BEGIN
                        UPDATE comics SET last_updated = CURRENT_TIMESTAMP WHERE id = NEW.id;
                    END;
                """]
                
            else:  # MySQL
                tables = ["""
                    CREATE TABLE IF NOT EXISTS publishers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS series (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        publisher_id INT,
                        FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE SET NULL,
                        UNIQUE KEY unique_series (name, publisher_id)
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS subseries (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        series_id INT NOT NULL,
                        FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
                        UNIQUE KEY unique_subseries (name, series_id)
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS authors (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS comics (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        series_id INT,
                        subseries_id INT,
                        issue_number VARCHAR(50),
                        year INT,
                        publisher VARCHAR(255),
                        summary TEXT,
                        page_count INT,
                        file_path TEXT NOT NULL UNIQUE,
                        file_size BIGINT,
                        file_modified DOUBLE,
                        file_created DOUBLE,
                        file_extension VARCHAR(10),
                        isbn VARCHAR(20),
                        notes TEXT,
                        cover_image LONGBLOB,
                        cover_image_type VARCHAR(20),
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        metadata JSON,
                        FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET NULL,
                        FOREIGN KEY (subseries_id) REFERENCES subseries(id) ON DELETE SET NULL
                    )""",
                    """
                    CREATE TABLE IF NOT EXISTS comic_authors (
                        comic_id INT NOT NULL,
                        author_id INT NOT NULL,
                        role VARCHAR(100) NOT NULL,
                        PRIMARY KEY (comic_id, author_id, role),
                        FOREIGN KEY (comic_id) REFERENCES comics(id) ON DELETE CASCADE,
                        FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
                    )"""]
                triggers = []  # No triggers needed for MySQL as it has ON UPDATE CURRENT_TIMESTAMP
            
            # Execute table creation queries
            for table_query in tables:
                try:
                    cursor.execute(table_query)
                except (sqlite3.Error, MySQLError) as e:
                    logger.error(f"Error creating table: {e}")
                    logger.error(f"Query was: {table_query}")
                    self.connection.rollback()
                    return False
            
            # Execute trigger creation for SQLite
            for trigger_query in triggers:
                try:
                    cursor.execute(trigger_query)
                except (sqlite3.Error, MySQLError) as e:
                    logger.error(f"Error creating trigger: {e}")
                    logger.error(f"Query was: {trigger_query}")
                    self.connection.rollback()
                    return False
            
            self.connection.commit()
            logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}", exc_info=True)
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def clear_database(self) -> bool:
        """Remove all data from the database but keep the structure."""
        cursor = None
        try:
            cursor = self.connection.cursor()
            if self.db_type == 'sqlite':
                # For SQLite, we need to delete data with foreign key constraints handled
                cursor.execute("PRAGMA foreign_keys = OFF")
                
                # Delete all data from tables in the correct order to respect foreign key constraints
                tables = ["comic_authors", "comics", "subseries", "series", "publishers", "authors"]
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                
                # Reset autoincrement counters
                cursor.execute("DELETE FROM sqlite_sequence")
                
                # Re-enable foreign key constraints
                cursor.execute("PRAGMA foreign_keys = ON")
            else:  # MySQL
                # Disable foreign key checks temporarily
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                
                # Get all tables
                tables = ["comic_authors", "comics", "subseries", "series", "publishers", "authors"]
                
                # Truncate all tables
                for table in tables:
                    cursor.execute(f"TRUNCATE TABLE {table}")
                
                # Re-enable foreign key checks
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            self.connection.commit()
            logger.info("Database cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing database: {e}", exc_info=True)
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database to a SQL file."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Get all table names
            tables = ["publishers", "series", "subseries", "authors", "comics", "comic_authors"]
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"-- ComicDB Backup\n")
                f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Disable foreign key checks
                f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                
                # For each table, get data and write to file
                for table in tables:
                    # Get table structure
                    self.execute_query(f"SHOW CREATE TABLE {table}")
                    create_table = self.execute_query(f"SHOW CREATE TABLE {table}", fetch=True)[0]['Create Table']
                    
                    # Write table structure
                    f.write(f"--\n-- Table structure for table `{table}`\n--\n")
                    f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                    f.write(f"{create_table};\n\n")
                    
                    # Get table data
                    rows = self.execute_query(f"SELECT * FROM {table}", fetch=True)
                    if rows:
                        f.write(f"--\n-- Dumping data for table `{table}`\n--\n")
                        
                        # Get column names
                        columns = list(rows[0].keys())
                        columns_str = ', '.join([f'`{col}`' for col in columns])
                        
                        # Write INSERT statements
                        for row in rows:
                            values = []
                            for col in columns:
                                val = row[col]
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                elif isinstance(val, datetime):
                                    values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                                else:
                                    # Escape single quotes
                                    val_str = str(val).replace("'", "''")
                                    values.append(f"'{val_str}'")
                            
                            f.write(f"INSERT INTO `{table}` ({columns_str}) VALUES ({", ".join(values)});\n")
                        f.write("\n")
                
                # Re-enable foreign key checks
                f.write("SET FOREIGN_KEY_CHECKS=1;\n")
            
            logger.info(f"Database backup created at {backup_path}")
            return True
            
        except Error as e:
            logger.error(f"Error creating database backup: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating backup: {e}")
            return False

    def import_from_csv(self, csv_path: str) -> bool:
        """Import comic data from a CSV file."""
        try:
            # Read CSV file
            df = pd.read_csv(csv_path, keep_default_na=False)
            
            # Required columns
            required_columns = ['title', 'file_path']
            for col in required_columns:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return False
            
            # Process each row
            for _, row in df.iterrows():
                # Get or create publisher
                publisher_id = None
                if 'publisher' in df.columns and row['publisher']:
                    publisher_id = self._get_or_create_publisher(row['publisher'])
                
                # Get or create series
                series_id = None
                if 'series' in df.columns and row['series']:
                    series_id = self._get_or_create_series(row['series'], publisher_id)
                
                # Get or create subseries
                subseries_id = None
                if 'subseries' in df.columns and row['subseries'] and series_id:
                    subseries_id = self._get_or_create_subseries(row['subseries'], series_id)
                
                # Prepare comic data
                comic_data = {
                    'title': row['title'],
                    'year': int(row.get('year', 0)) if row.get('year') else None,
                    'issue_number': str(row.get('issue_number', '')) if row.get('issue_number') else None,
                    'file_path': row['file_path'],
                    'series_id': series_id,
                    'subseries_id': subseries_id
                }
                
                # Check if comic already exists
                existing = self.execute_query(
                    "SELECT id FROM comics WHERE file_path = %s", 
                    (row['file_path'],), 
                    fetch=True
                )
                
                if existing:
                    # Update existing comic
                    comic_id = existing[0]['id']
                    set_clause = ", ".join([f"{k} = %s" for k in comic_data.keys()])
                    values = list(comic_data.values()) + [comic_id]
                    self.execute_query(
                        f"UPDATE comics SET {set_clause} WHERE id = %s",
                        tuple(values)
                    )
                else:
                    # Insert new comic
                    placeholders = ", ".join(["%s"] * len(comic_data))
                    columns = ", ".join(comic_data.keys())
                    self.execute_query(
                        f"INSERT INTO comics ({columns}) VALUES ({placeholders})",
                        tuple(comic_data.values())
                    )
                    comic_id = self.connection.cursor().lastrowid
                
                # Handle authors
                if 'authors' in df.columns and row['authors']:
                    # Remove existing author relationships
                    self.execute_query(
                        "DELETE FROM comic_authors WHERE comic_id = %s",
                        (comic_id,)
                    )
                    
                    # Add new author relationships
                    authors = [a.strip() for a in str(row['authors']).split(';') if a.strip()]
                    for author_name in authors:
                        author_id = self._get_or_create_author(author_name)
                        self.execute_query(
                            """INSERT INTO comic_authors (comic_id, author_id, role) 
                               VALUES (%s, %s, 'creator')""",
                            (comic_id, author_id)
                        )
            
            self.connection.commit()
            logger.info(f"Successfully imported data from {csv_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def export_to_csv(self, csv_path: str) -> bool:
        """Export comic data to a CSV file."""
        try:
            # Get all comics with related data
            query = """
                SELECT 
                    c.id,
                    c.title,
                    c.year,
                    c.issue_number,
                    c.file_path,
                    p.name AS publisher,
                    s.name AS series,
                    ss.name AS subseries,
                    GROUP_CONCAT(DISTINCT a.name SEPARATOR '; ') AS authors
                FROM comics c
                LEFT JOIN series s ON c.series_id = s.id
                LEFT JOIN publishers p ON s.publisher_id = p.id
                LEFT JOIN subseries ss ON c.subseries_id = ss.id
                LEFT JOIN comic_authors ca ON c.id = ca.comic_id
                LEFT JOIN authors a ON ca.author_id = a.id
                GROUP BY c.id, c.title, c.year, c.issue_number, c.file_path, p.name, s.name, ss.name
                ORDER BY p.name, s.name, c.year, c.issue_number, c.title
            """
            
            comics = self.execute_query(query, fetch=True)
            
            if not comics:
                logger.warning("No comics found to export")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(comics)
            
            # Reorder columns
            columns = ['title', 'year', 'issue_number', 'publisher', 'series', 'subseries', 
                     'authors', 'file_path']
            df = df[columns]
            
            # Save to CSV
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
            logger.info(f"Successfully exported {len(comics)} comics to {csv_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    def _get_or_create_publisher(self, name: str) -> int:
        """Get or create a publisher and return its ID."""
        cursor = self.connection.cursor()
        try:
            # Use ? placeholder for SQLite, %s for MySQL
            query = "SELECT id FROM publishers WHERE name = ?" if self.db_type == 'sqlite' else \
                    "SELECT id FROM publishers WHERE name = %s"
            cursor.execute(query, (name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Use ? placeholder for SQLite, %s for MySQL
                query = "INSERT INTO publishers (name) VALUES (?)" if self.db_type == 'sqlite' else \
                        "INSERT INTO publishers (name) VALUES (%s)"
                cursor.execute(query, (name,))
                return cursor.lastrowid
        finally:
            cursor.close()

    def _get_or_create_series(self, name: str, publisher_id: int = None) -> int:
        """Get or create a series and return its ID."""
        cursor = self.connection.cursor()
        try:
            # Use ? placeholders for SQLite, %s for MySQL
            if publisher_id:
                query = """
                    SELECT id FROM series 
                    WHERE name = ? AND publisher_id = ?
                """ if self.db_type == 'sqlite' else """
                    SELECT id FROM series 
                    WHERE name = %s AND publisher_id = %s
                """
                cursor.execute(query, (name, publisher_id))
            else:
                query = """
                    SELECT id FROM series 
                    WHERE name = ? AND publisher_id IS NULL
                """ if self.db_type == 'sqlite' else """
                    SELECT id FROM series 
                    WHERE name = %s AND publisher_id IS NULL
                """
                cursor.execute(query, (name,))
            
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Use ? placeholders for SQLite, %s for MySQL
                query = """
                    INSERT INTO series (name, publisher_id) 
                    VALUES (?, ?)
                """ if self.db_type == 'sqlite' else """
                    INSERT INTO series (name, publisher_id) 
                    VALUES (%s, %s)
                """
                cursor.execute(query, (name, publisher_id))
                return cursor.lastrowid
        finally:
            cursor.close()

    def _get_or_create_subseries(self, name: str, series_id: int) -> int:
        """Get or create a subseries and return its ID."""
        cursor = self.connection.cursor()
        try:
            # Use ? placeholders for SQLite, %s for MySQL
            query = """
                SELECT id FROM subseries 
                WHERE name = ? AND series_id = ?
            """ if self.db_type == 'sqlite' else """
                SELECT id FROM subseries 
                WHERE name = %s AND series_id = %s
            """
            cursor.execute(query, (name, series_id))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Use ? placeholders for SQLite, %s for MySQL
                query = """
                    INSERT INTO subseries (name, series_id) 
                    VALUES (?, ?)
                """ if self.db_type == 'sqlite' else """
                    INSERT INTO subseries (name, series_id) 
                    VALUES (%s, %s)
                """
                cursor.execute(query, (name, series_id))
                return cursor.lastrowid
        finally:
            cursor.close()

    def _get_or_create_author(self, name: str) -> int:
        """Get or create an author and return its ID."""
        cursor = self.connection.cursor()
        try:
            # Use ? placeholder for SQLite, %s for MySQL
            query = "SELECT id FROM authors WHERE name = ?" if self.db_type == 'sqlite' else \
                    "SELECT id FROM authors WHERE name = %s"
            cursor.execute(query, (name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Use ? placeholder for SQLite, %s for MySQL
                query = "INSERT INTO authors (name) VALUES (?)" if self.db_type == 'sqlite' else \
                        "INSERT INTO authors (name) VALUES (%s)"
                cursor.execute(query, (name,))
                return cursor.lastrowid
        finally:
            cursor.close()

    def get_publishers(self) -> List[Dict[str, Any]]:
        """Get all publishers from the database.
        
        Returns:
            List of publisher dictionaries with 'id' and 'name' keys
        """
        try:
            return self.execute_query(
                "SELECT id, name FROM publishers ORDER BY name", 
                fetch=True
            ) or []
        except Exception as e:
            logger.error(f"Error getting publishers: {e}")
            return []
    
    def add_comic_from_file(self, file_path: str) -> Optional[int]:
        """Add a comic to the database from a file.
        
        Args:
            file_path: Path to the comic file (CBR, CBZ, PDF)
            
        Returns:
            ID of the added comic, or None if failed.
            Raises:
                FileNotFoundError: If the file doesn't exist
                ValueError: If the file is not a valid comic or is corrupted
                Exception: For other unexpected errors
        """
        from struttura.comic_scanner import ComicScanner, ComicMetadata
        
        # Verify file exists and is accessible before proceeding
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
            
        try:
            # Initialize scanner and extract metadata
            scanner = ComicScanner()
            metadata_dict = scanner.scan_file(file_path)
            
            # Check for errors in metadata extraction
            if not metadata_dict:
                error_msg = f"Failed to process file (unknown error): {file_path}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if 'error' in metadata_dict:
                error_msg = f"Failed to process file: {metadata_dict['error']}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            try:
                metadata = ComicMetadata.from_dict(metadata_dict)
            except Exception as e:
                error_msg = f"Invalid metadata format in {file_path}: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg) from e
            
            # Start transaction
            cursor = self.connection.cursor()
            
            try:
                # Get or create publisher
                publisher_id = None
                if metadata.publisher:
                    publisher_id = self._get_or_create_publisher(metadata.publisher)
                
                # Get or create series
                series_id = None
                if metadata.series:
                    series_id = self._get_or_create_series(metadata.series, publisher_id)
                
                # Get or create subseries if available
                subseries_id = None
                if metadata.subseries and series_id:
                    subseries_id = self._get_or_create_subseries(metadata.subseries, series_id)
                
                # Get file attributes with defaults
                file_extension = os.path.splitext(file_path)[1] if hasattr(metadata, 'file_extension') else os.path.splitext(file_path)[1]
                file_created = getattr(metadata, 'file_created', None) or os.path.getctime(file_path)
                file_modified = getattr(metadata, 'file_modified', None) or os.path.getmtime(file_path)
                file_size = getattr(metadata, 'file_size', None) or os.path.getsize(file_path)
                
                # Create a serializable version of metadata_dict
                serializable_metadata = {}
                for key, value in metadata_dict.items():
                    # Skip binary data or other non-serializable values
                    if isinstance(value, (str, int, float, bool, type(None))):
                        serializable_metadata[key] = value
                    elif isinstance(value, (list, tuple, dict)):
                        # Recursively check nested structures
                        try:
                            json.dumps(value)  # Test if value is JSON serializable
                            serializable_metadata[key] = value
                        except (TypeError, OverflowError):
                            serializable_metadata[key] = str(value)  # Convert to string if not serializable
                    else:
                        serializable_metadata[key] = str(value)  # Convert to string for other types
                
                # Insert comic
                cursor.execute("""
                    INSERT INTO comics (
                        title, series_id, subseries_id, issue_number, year, 
                        publisher, summary, page_count, file_path, file_size, 
                        file_modified, file_created, file_extension, 
                        isbn, notes, cover_image, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                """, (
                    metadata.title, series_id, subseries_id, 
                    getattr(metadata, 'issue_number', None), 
                    getattr(metadata, 'year', None),
                    getattr(metadata, 'publisher', None), 
                    getattr(metadata, 'summary', None), 
                    getattr(metadata, 'page_count', None), 
                    file_path, file_size,
                    file_modified, file_created, file_extension,
                    getattr(metadata, 'isbn', None), 
                    getattr(metadata, 'notes', None), 
                    getattr(metadata, 'cover_image', None), 
                    json.dumps(serializable_metadata)
                ))
                
                comic_id = cursor.fetchone()[0]
                
                # Add authors
                if metadata.authors:
                    for author_name in metadata.authors:
                        author_id = self._get_or_create_author(author_name)
                        self._add_comic_author(comic_id, author_id, "Writer")
                
                self.connection.commit()
                logger.info(f"Successfully added comic: {metadata.title} (ID: {comic_id})")
                return comic_id
                
            except Exception as e:
                self.connection.rollback()
                logger.error(f"Database error while adding comic {file_path}: {str(e)}", exc_info=True)
                raise  # Re-raise the exception with full traceback
                
        except Exception as e:
            # Log the error with full traceback
            logger.error(f"Unexpected error processing {file_path}: {str(e)}", exc_info=True)
            
            # If it's a known error type, re-raise it
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
                
            # For other errors, wrap in a more descriptive exception
            raise Exception(f"Failed to add comic from {file_path}: {str(e)}") from e
    
    def _add_comic_author(self, comic_id: int, author_id: int, role: str) -> bool:
        """Add an author to a comic with a specific role."""
        try:
            # Use ? placeholders for SQLite compatibility
            query = """
                INSERT INTO comic_authors (comic_id, author_id, role)
                VALUES (?, ?, ?)
                ON CONFLICT DO NOTHING
            """ if self.db_type == 'sqlite' else """
                INSERT INTO comic_authors (comic_id, author_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """
            self.execute_query(query, (comic_id, author_id, role))
            return True
        except Exception as e:
            logger.error(f"Error adding author to comic: {e}")
            return False
            
    def get_series(self, publisher: str = None) -> List[Dict[str, Any]]:
        """Get all series from the database, optionally filtered by publisher.
        
        Args:
            publisher: Optional publisher name to filter series by
            
        Returns:
            List of series dictionaries with 'id', 'name', and 'publisher' keys
        """
        try:
            query = """
                SELECT s.id, s.name, p.name as publisher
                FROM series s
                LEFT JOIN publishers p ON s.publisher_id = p.id
            """
            params = []
            
            if publisher:
                query += " WHERE p.name = ?"
                params.append(publisher)
                
            query += " ORDER BY s.name"
            
            return self.execute_query(query, params, fetch=True) or []
        except Exception as e:
            logger.error(f"Error getting series: {e}")
            return []
    
    def get_comic_count(self) -> int:
        """Get the total number of comics in the database."""
        try:
            result = self.execute_query("SELECT COUNT(*) as count FROM comics", fetch=True)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting comic count: {e}")
            return 0
    
    def get_series_count(self) -> int:
        """Get the total number of series in the database."""
        try:
            result = self.execute_query("SELECT COUNT(*) as count FROM series", fetch=True)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting series count: {e}")
            return 0
            
    def get_publisher_count(self) -> int:
        """Get the total number of publishers in the database."""
        try:
            result = self.execute_query("SELECT COUNT(*) as count FROM publishers", fetch=True)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting publisher count: {e}")
            return 0
