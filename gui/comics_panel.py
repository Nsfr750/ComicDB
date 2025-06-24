import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
import logging

# Local imports
from struttura.database import ComicDatabase
from struttura.comic_scanner import ComicScanner, ComicMetadata
from struttura.lang import tr
from struttura.logger import log_info, log_error, log_warning

class ComicsPanel(ttk.Frame):
    """Panel for managing comic book archives."""
    
    def __init__(self, parent: ttk.Widget, db_config: Dict[str, Any], **kwargs) -> None:
        """Initialize the comics panel.
        
        Args:
            parent: Parent widget
            db_config: Database configuration dictionary with keys:
                - host: Database host
                - user: Database username
                - password: Database password
                - database: Database name
        """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.db_config = db_config
        self.db: Optional[ComicDatabase] = None
        self.scanner: Optional[ComicScanner] = None
        self.stop_scan = False
        
        # UI components
        self.notebook = None
        self.import_tab = None
        self.browse_tab = None
        self.db_tab = None
        self.status_var = tk.StringVar()
        self.dir_var = tk.StringVar()
        self.recursive_var = tk.BooleanVar(value=True)
        self.search_var = tk.StringVar()
        self.publisher_var = tk.StringVar()
        self.series_var = tk.StringVar()
        self.stats_var = tk.StringVar()
        self.progress_var = tk.StringVar()
        self.progress = None
        self.start_btn = None
        self.stop_btn = None
        self.tree = None
        self.publisher_cb = None
        self.series_cb = None
        self.context_menu = None
        
        # Initialize database connection
        self._init_database()
        
        # Set up UI
        self._setup_ui()
        
        # Initial status update
        self._update_status()
    
    def _init_database(self) -> None:
        """Initialize the database connection and create tables if they don't exist."""
        try:
            # Add default db_type if not specified
            if 'db_type' not in self.db_config:
                self.db_config['db_type'] = 'sqlite'
                
            # If using SQLite, ensure the database file path is absolute
            if self.db_config.get('db_type') == 'sqlite' and 'database' in self.db_config:
                db_path = Path(self.db_config['database'])
                if not db_path.is_absolute():
                    # Make path relative to the application directory
                    app_dir = Path(__file__).parent.parent
                    self.db_config['database'] = str(app_dir / db_path)
            
            # Create database directory if it doesn't exist
            if self.db_config.get('db_type') == 'sqlite' and 'database' in self.db_config:
                db_dir = Path(self.db_config['database']).parent
                db_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            self.db = ComicDatabase(**self.db_config)
            
            # Create tables if they don't exist
            if not self.db.create_tables():
                log_error("Failed to create database tables")
                messagebox.showerror(
                    "Error",
                    "Failed to initialize database tables. Check the log for details."
                )
                return
                
            log_info("Database initialized successfully")
            
        except Exception as e:
            log_error(f"Error initializing database: {e}")
            import traceback
            error_details = traceback.format_exc()
            log_error(f"Error details: {error_details}")
            
            # Show error message with details
            error_msg = f"Failed to initialize database: {str(e)}\n\n"
            error_msg += "Please check the following:\n"
            error_msg += "1. Database server is running (if using MySQL)\n"
            error_msg += "2. Database credentials are correct\n"
            error_msg += "3. You have write permissions to the database file (if using SQLite)\n\n"
            error_msg += "Check the log file for more details."
            
            messagebox.showerror(
                "Database Error",
                error_msg
            )
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Create tabs
        self._create_import_tab()
        self._create_browse_tab()
        self._create_database_tab()
        
        # Map tab names to their indices
        self.tab_indices = {
            'import': 0,
            'browse': 1,
            'database': 2
        }
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=1, column=0, sticky='ew', padx=5, pady=2)
        
        # Initial status update
        self._update_status()
    
    def show_tab(self, tab_name: str) -> None:
        """Switch to a specific tab in the panel.
        
        Args:
            tab_name: Name of the tab to show ('import', 'browse', or 'database')
        """
        try:
            if tab_name in self.tab_indices:
                self.notebook.select(self.tab_indices[tab_name])
                
                # Refresh the tab if needed
                if tab_name == 'browse':
                    self._load_comics()
                elif tab_name == 'database':
                    self._update_stats()
        except Exception as e:
            log_error(f"Error showing tab '{tab_name}': {e}")
            messagebox.showerror(
                "Error",
                f"Could not switch to {tab_name} tab: {str(e)}"
            )
    
    def _create_import_tab(self) -> None:
        """Create the import tab."""
        self.import_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.import_tab, text=tr('import_comics'))
        
        # Configure grid
        self.import_tab.grid_rowconfigure(0, weight=1)
        self.import_tab.grid_columnconfigure(0, weight=1)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(self.import_tab, text=tr('scan_directory'))
        dir_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        # Directory entry
        self.dir_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, state='readonly')
        dir_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        # Browse button
        browse_btn = ttk.Button(
            dir_frame,
            text=tr('browse'),
            command=self._browse_directory
        )
        browse_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.import_tab, text=tr('options'))
        options_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        # Recursive scan checkbox
        self.recursive_var = tk.BooleanVar(value=True)
        recursive_cb = ttk.Checkbutton(
            options_frame,
            text=tr('scan_recursively'),
            variable=self.recursive_var
        )
        recursive_cb.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        # Buttons frame
        btn_frame = ttk.Frame(self.import_tab)
        btn_frame.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        
        # Start scan button
        self.start_btn = ttk.Button(
            btn_frame,
            text=tr('start_scan'),
            command=self._start_scan
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        # Stop scan button
        self.stop_btn = ttk.Button(
            btn_frame,
            text=tr('stop_scan'),
            command=self._stop_scan,
            state='disabled'
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.import_tab, text=tr('progress'))
        progress_frame.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')
        progress_frame.grid_rowconfigure(0, weight=1)
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Progress text
        self.progress_var = tk.StringVar()
        progress_label = ttk.Label(
            progress_frame,
            textvariable=self.progress_var,
            wraplength=500
        )
        progress_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame,
            orient='horizontal',
            length=500,
            mode='determinate'
        )
        self.progress.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
    
    def _browse_directory(self) -> None:
        """Open a directory selection dialog."""
        directory = filedialog.askdirectory(title=tr('select_directory'))
        if directory:
            self.dir_var.set(directory)
    
    def _start_scan(self) -> None:
        """Start scanning the selected directory for comic files."""
        directory = self.dir_var.get()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror(tr('error'), tr('invalid_directory'))
            return
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_var.set(tr('scanning') + '...')
        self.progress['value'] = 0
        self.stop_scan = False
        
        # Start scan in a separate thread
        thread = threading.Thread(
            target=self._scan_directory,
            args=(directory, self.recursive_var.get()),
            daemon=True
        )
        thread.start()
    
    def _stop_scan(self) -> None:
        """Stop the current scan."""
        if messagebox.askyesno(
            tr('confirm_stop_scan'),
            tr('confirm_stop_scan_msg')
        ):
            self.stop_scan = True
    
    def _scan_directory(self, directory: str, recursive: bool) -> None:
        """Scan a directory for comic files.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
        """
        try:
            scanner = ComicScanner()
            files = scanner.find_comic_files(directory, recursive=recursive)
            
            if not files:
                self._update_ui_after_scan(0, 0)
                messagebox.showinfo(tr('info'), tr('no_comics_found'))
                return
            
            imported = 0
            total = len(files)
            
            for i, file_path in enumerate(files, 1):
                if self.stop_scan:
                    break
                
                # Update progress
                progress = (i / total) * 100
                self.progress['value'] = progress
                self.progress_var.set(f"Processing {i} of {total}: {os.path.basename(file_path)}")
                
                # Process file
                try:
                    if self.db and self.db.add_comic_from_file(file_path):
                        imported += 1
                except Exception as e:
                    log_error(f"Error processing {file_path}: {e}")
            
            # Update UI and show results
            self._update_ui_after_scan(total, imported)
            
        except Exception as e:
            log_error(f"Error scanning directory: {e}")
            self._update_ui_after_scan(0, 0)
            messagebox.showerror(tr('error'), tr('scan_error', error=str(e)))
    
    def _update_ui_after_scan(self, processed: int, imported: int) -> None:
        """Update the UI after a scan completes.
        
        Args:
            processed: Number of files processed
            imported: Number of files imported
        """
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress['value'] = 100
        
        if processed > 0:
            self.progress_var.set(
                tr('scan_complete_msg', processed=processed, imported=imported)
            )
            
            # Refresh UI
            self._load_filters()
            self._load_comics()
            self._update_stats()
            self._update_status()
    
    def _create_browse_tab(self) -> None:
        """Create the browse tab for viewing and managing comics."""
        self.browse_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.browse_tab, text=tr('browse_comics'))
        
        # Configure grid
        self.browse_tab.grid_rowconfigure(1, weight=1)
        self.browse_tab.grid_columnconfigure(0, weight=1)
        
        # Search and filter frame
        filter_frame = ttk.LabelFrame(self.browse_tab, text=tr('filters'))
        filter_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        # Search entry
        search_label = ttk.Label(filter_frame, text=tr('search') + ':')
        search_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        search_entry.bind('<Return>', lambda e: self._load_comics())
        
        # Filter dropdowns
        ttk.Label(filter_frame, text=tr('publisher') + ':').grid(
            row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.publisher_var = tk.StringVar()
        self.publisher_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.publisher_var,
            state='readonly'
        )
        self.publisher_cb.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.publisher_cb.bind('<<ComboboxSelected>>', lambda e: self._load_comics())
        
        ttk.Label(filter_frame, text=tr('series') + ':').grid(
            row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.series_var = tk.StringVar()
        self.series_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.series_var,
            state='readonly'
        )
        self.series_cb.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.series_cb.bind('<<ComboboxSelected>>', lambda e: self._load_comics())
        
        # Clear filters button
        clear_btn = ttk.Button(
            filter_frame,
            text=tr('clear_filters'),
            command=self._clear_filters
        )
        clear_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Comics list
        list_frame = ttk.Frame(self.browse_tab)
        list_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for comics - first column is hidden and contains the comic ID
        columns = ('id', 'title', 'series', 'issue', 'publisher', 'year')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='extended',  # Enable multiple selection
            displaycolumns=('title', 'series', 'issue', 'publisher', 'year')  # Hide the ID column
        )
        
        # Configure columns
        self.tree.heading('title', text=tr('title'))
        self.tree.heading('series', text=tr('series'))
        self.tree.heading('issue', text=tr('issue'))
        self.tree.heading('publisher', text=tr('publisher'))
        self.tree.heading('year', text=tr('year'))
        
        # Set column widths
        self.tree.column('title', width=200)
        self.tree.column('series', width=150)
        self.tree.column('issue', width=50, anchor='center')
        self.tree.column('publisher', width=150)
        self.tree.column('year', width=60, anchor='center')
        self.tree.column('id', width=0, stretch=False)  # Hide the ID column
        
        # Add scrollbars
        vsb = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(
            label=tr('open_file_location'),
            command=self._open_file_location
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label=tr('delete_from_database'),
            command=self._delete_selected_comic
        )
        
        # Bind right-click event
        self.tree.bind('<Button-3>', self._show_context_menu)
        
        # Load initial data
        self._load_filters()
        self._load_comics()
    
    def _load_filters(self) -> None:
        """Load filter options from the database."""
        if not self.db:
            return
        
        try:
            # Get publishers and series
            publishers = self.db.get_publishers()
            series = self.db.get_series()
            
            # Update comboboxes
            self.publisher_cb['values'] = [''] + [p[1] for p in publishers]
            self.series_cb['values'] = [''] + [s[1] for s in series]
            
        except Exception as e:
            log_error(f"Error loading filters: {e}")
    
    def _load_comics(self) -> None:
        """Load comics from the database with current filters."""
        if not self.db:
            return
        
        try:
            # Get filter values
            search = self.search_var.get().strip()
            publisher = self.publisher_var.get()
            series = self.series_var.get()
            
            # Clear current items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get comics from database
            comics = self.db.get_comics(
                search=search if search else None,
                publisher=publisher if publisher else None,
                series=series if series else None
            )
            
            # Add to treeview with safe field access
            # First value is the comic ID, which is hidden in the UI
            for comic in comics:
                self.tree.insert('', 'end', values=(
                    comic.get('id'),  # Hidden ID column
                    comic.get('title', ''),
                    comic.get('series', ''),
                    comic.get('issue', ''),
                    comic.get('publisher', ''),
                    comic.get('year', '')
                ))
            
            # Update status
            self.status_var.set(tr('comics_found', count=len(comics)))
            
        except Exception as e:
            error_msg = f"{tr('error_loading_comics')}\n\n{str(e)}"
            log_error(f"Error loading comics: {e}", exc_info=True)
            messagebox.showerror(tr('error'), error_msg)
    
    def _clear_filters(self) -> None:
        """Clear all filters and reload comics."""
        self.search_var.set('')
        self.publisher_var.set('')
        self.series_var.set('')
        self._load_comics()
    
    def _show_context_menu(self, event) -> None:
        """Show the context menu for the selected comic."""
        # Identify the row that was right-clicked
        item = self.tree.identify_row(event.y)
        if item:
            # Check if the right-clicked item is already selected
            selected = self.tree.selection()
            if item not in selected:
                # If not in current selection, select only this item
                self.tree.selection_set(item)
            # Show the context menu at the click position
            self.context_menu.post(event.x_root, event.y_root)
        else:
            # If clicking outside any item, clear the selection
            self.tree.selection_remove(self.tree.selection())
            return "break"  # Prevent default behavior
    
    def _open_file_location(self) -> None:
        """Open the file location of the selected comic."""
        selected = self.tree.selection()
        if not selected:
            return
        
        try:
            # Get the file path from the database
            comic_id = self.tree.item(selected[0])['values'][0]  # Assuming first column is ID
            if self.db:
                comic = self.db.get_comic(comic_id)
                if comic and 'file_path' in comic:
                    # Open the file location in the file explorer
                    os.startfile(os.path.dirname(comic['file_path']))
        except Exception as e:
            log_error(f"Error opening file location: {e}")
            messagebox.showerror(
                tr('error'),
                tr('error_opening_location', error=str(e))
            )
    
    def _delete_selected_comic(self) -> None:
        """Delete the selected comics from the database."""
        selected = self.tree.selection()
        if not selected:
            return
            
        try:
            # Get comic details for confirmation
            if len(selected) == 1:
                values = self.tree.item(selected[0])['values']
                title = values[0]
                message = tr('confirm_delete_comic', title=title)
            else:
                message = f"Sei sicuro di voler eliminare i {len(selected)} fumetti selezionati?"
            
            if not messagebox.askyesno(tr('confirm_delete'), message):
                return
                
            # Delete each selected comic
            success_count = 0
            for item in selected:
                try:
                    # Get the comic ID from the hidden first column
                    comic_id = self.tree.item(item)['values'][0]
                    if self.db and self.db.delete_comic(comic_id):
                        success_count += 1
                    else:
                        log_error(f"Failed to delete comic with ID: {comic_id}")
                except Exception as e:
                    log_error(f"Error deleting comic: {e}")
            
            # Update UI
            if success_count > 0:
                for item in selected:
                    self.tree.delete(item)
                self._update_stats()
                self._update_status()
                
                if success_count == 1:
                    messagebox.showinfo(tr('success'), tr('comic_deleted', title=title))
                else:
                    messagebox.showinfo(
                        tr('success'),
                        f"{success_count} fumetti eliminati con successo."
                    )
            
        except Exception as e:
            log_error(f"Error deleting comics: {e}")
            messagebox.showerror(
                tr('error'),
                tr('error_deleting_comic', error=str(e))
            )
    
    def _create_database_tab(self) -> None:
        """Create the database management tab."""
        self.db_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.db_tab, text=tr('manage_database'))
        
        # Configure grid
        self.db_tab.grid_rowconfigure(2, weight=1)
        self.db_tab.grid_columnconfigure(1, weight=1)
        
        # Database info frame
        info_frame = ttk.LabelFrame(self.db_tab, text=tr('database_info'))
        info_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        # Stats
        self.stats_var = tk.StringVar()
        stats_label = ttk.Label(
            info_frame,
            textvariable=self.stats_var,
            justify='left',
            font=('TkFixedFont', 10)
        )
        stats_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        # Buttons frame
        btn_frame = ttk.Frame(self.db_tab)
        btn_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Create tables button
        create_btn = ttk.Button(
            btn_frame,
            text=tr('create_tables'),
            command=self._create_tables
        )
        create_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Clear database button
        clear_btn = ttk.Button(
            btn_frame,
            text=tr('clear_database'),
            command=self._clear_database
        )
        clear_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Backup database button
        backup_btn = ttk.Button(
            btn_frame,
            text=tr('backup_database'),
            command=self._backup_database
        )
        backup_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Import/Export frame
        io_frame = ttk.LabelFrame(self.db_tab, text=tr('import_export'))
        io_frame.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        
        # Import button
        import_btn = ttk.Button(
            io_frame,
            text=tr('import_csv'),
            command=self._import_csv
        )
        import_btn.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        # Export button
        export_btn = ttk.Button(
            io_frame,
            text=tr('export_csv'),
            command=self._export_csv
        )
        export_btn.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        # Update stats
        self._update_stats()
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        if not self.db:
            return
        
        if messagebox.askyesno(tr('confirm'), tr('confirm_create_tables')):
            try:
                if self.db.create_tables():
                    messagebox.showinfo(tr('success'), tr('tables_created'))
                    self._update_stats()
                    self._load_filters()
                    self._load_comics()
                else:
                    messagebox.showerror(tr('error'), tr('error_creating_tables'))
            except Exception as e:
                log_error(f"Error creating tables: {e}")
                messagebox.showerror(tr('error'), tr('error_creating_tables'))
    
    def _clear_database(self) -> None:
        """Clear all data from the database."""
        if not self.db:
            return
        
        if messagebox.askyesno(tr('confirm'), tr('confirm_clear_database')):
            try:
                if self.db.clear_database():
                    messagebox.showinfo(tr('success'), tr('database_cleared'))
                    self._update_stats()
                    self._load_filters()
                    self._load_comics()
                else:
                    messagebox.showerror(tr('error'), tr('error_clearing_database'))
            except Exception as e:
                log_error(f"Error clearing database: {e}")
                messagebox.showerror(tr('error'), tr('error_clearing_database'))
    
    def _backup_database(self) -> None:
        """Create a backup of the database."""
        if not self.db:
            return
        
        default_filename = f"comicdb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        file_path = filedialog.asksaveasfilename(
            title=tr('save_backup_as'),
            defaultextension=".sql",
            initialfile=default_filename,
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if self.db.backup_database(file_path):
                    messagebox.showinfo(
                        tr('success'),
                        tr('backup_created', path=file_path)
                    )
                else:
                    messagebox.showerror(
                        tr('error'),
                        tr('error_creating_backup')
                    )
            except Exception as e:
                log_error(f"Error creating backup: {e}")
                messagebox.showerror(
                    tr('error'),
                    tr('error_creating_backup')
                )
    
    def _import_csv(self) -> None:
        """Import comics from a CSV file."""
        if not self.db:
            return
        
        file_path = filedialog.askopenfilename(
            title=tr('select_csv_file'),
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if self.db.import_from_csv(file_path):
                    messagebox.showinfo(
                        tr('success'),
                        tr('import_successful')
                    )
                    self._update_stats()
                    self._load_filters()
                    self._load_comics()
                else:
                    messagebox.showerror(
                        tr('error'),
                        tr('import_failed')
                    )
            except Exception as e:
                log_error(f"Error importing CSV: {e}")
                messagebox.showerror(
                    tr('error'),
                    tr('import_error', error=str(e))
                )
    
    def _export_csv(self) -> None:
        """Export comics to a CSV file."""
        if not self.db:
            return
        
        default_filename = f"comicdb_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            title=tr('save_export_as'),
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if self.db.export_to_csv(file_path):
                    messagebox.showinfo(
                        tr('success'),
                        tr('export_successful', path=file_path)
                    )
                else:
                    messagebox.showerror(
                        tr('error'),
                        tr('export_failed')
                    )
            except Exception as e:
                log_error(f"Error exporting to CSV: {e}")
                messagebox.showerror(
                    tr('error'),
                    tr('export_error', error=str(e))
                )
    
    def _update_stats(self) -> None:
        """Update the database statistics."""
        if not self.db:
            return
        
        try:
            stats = {
                'comics': self.db.get_comic_count(),
                'series': self.db.get_series_count(),
                'publishers': self.db.get_publisher_count()
            }
            
            stats_text = (
                f"{tr('comics')}: {stats['comics']}\n"
                f"{tr('series')}: {stats['series']}\n"
                f"{tr('publishers')}: {stats['publishers']}"
            )
            
            self.stats_var.set(stats_text)
            
        except Exception as e:
            log_error(f"Error updating stats: {e}")
            self.stats_var.set(tr('error_loading_stats'))
    
    def _update_status(self) -> None:
        """Update the status bar with current information."""
        if not self.db:
            self.status_var.set(tr('not_connected_to_database'))
            return
        
        try:
            count = self.db.get_comic_count()
            self.status_var.set(tr('comics_in_database', count=count))
        except Exception as e:
            log_error(f"Error updating status: {e}")
            self.status_var.set(tr('error_loading_status'))
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Signal any running scans to stop
            self.stop_scan = True
            
            # Close the database connection if it exists
            if self.db:
                try:
                    # Commit any pending changes
                    if hasattr(self.db, 'connection') and self.db.connection:
                        self.db.connection.commit()
                    
                    # Close all connections
                    if hasattr(self.db, 'close_all_connections'):
                        self.db.close_all_connections()
                    else:
                        self.db.close()
                except Exception as e:
                    log_error(f"Error during database cleanup: {e}")
                finally:
                    self.db = None
        except Exception as e:
            log_error(f"Error in cleanup: {e}")
