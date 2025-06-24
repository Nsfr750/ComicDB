import tkinter as tk
from tkinter import ttk
from struttura.menu import create_menu_bar
from struttura.logger import log_info, log_error, log_warning
from struttura.lang import tr
import os

class MainWindow(ttk.Frame):
    def __init__(self, parent, db_config=None):
        super().__init__(parent)
        self.parent = parent
        self.parent.title(tr('app_title'))
        self.parent.geometry('1024x768')
        self.db_config = db_config or {
            'database': 'comicdb.sqlite',
            'db_type': 'sqlite'
        }
        self.pack(fill=tk.BOTH, expand=True)
        
        # Set up window close handler on the parent window
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Menu bar - use parent window for menu
        create_menu_bar(self.parent, self)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # Create comics panel
        self._create_comics_panel()
        
        # Log frame
        log_frame = ttk.LabelFrame(self, text=tr('log'))
        log_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        # Configure log frame grid
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        # Log box with scrollbar
        self.log_box = tk.Text(log_frame, height=8, state='disabled', wrap='word')
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for log box and scrollbar
        self.log_box.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        scrollbar.grid(row=0, column=1, sticky='ns', padx=0, pady=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self, 
            textvariable=self.status_var,
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.grid(row=3, column=0, sticky='ew', padx=5, pady=2)
        
        # Initial status update
        self._update_status()
    
    def _create_comics_panel(self):
        """Create and add the comics panel to the notebook."""
        try:
            from gui.comics_panel import ComicsPanel
            
            # Database configuration - using SQLite
            db_config = {
                'database': 'comicdb.sqlite',  # SQLite database file
                'db_type': 'sqlite'  # Indicate we're using SQLite
            }
            
            # Create and add the comics panel
            self.comics_panel = ComicsPanel(self.notebook, db_config)
            self.notebook.add(self.comics_panel, text='Comics')  # Use hardcoded text instead of tr()
            
        except ImportError as e:
            log_error(f"Error importing comics panel: {e}")
            error_label = ttk.Label(
                self.notebook, 
                text=f"Error loading comics panel: {e}",
                foreground='red',
                wraplength=400,
                padding=10
            )
            self.notebook.add(error_label, text='Error')  # Use hardcoded text instead of tr()
        except Exception as e:
            log_error(f"Unexpected error creating comics panel: {e}")
            import traceback
            error_details = traceback.format_exc()
            log_error(f"Error details: {error_details}")
            
            error_label = ttk.Label(
                self.notebook, 
                text=f"Error: {str(e)}\n\nPlease check the log file for more details.",
                foreground='red',
                wraplength=400,
                padding=10
            )
            self.notebook.add(error_label, text='Error')
    
    def show_comics_tab(self, tab_name: str) -> None:
        """Switch to a specific tab in the comics panel.
        
        Args:
            tab_name: Name of the tab to show ('import', 'browse', or 'database')
        """
        try:
            # Make sure the comics panel is visible
            if self.notebook.index('end') == 0:
                self._create_comics_panel()
            
            # Select the comics tab (first tab)
            self.notebook.select(0)
            
            # If the comics panel has a method to switch tabs, call it
            if hasattr(self, 'comics_panel') and hasattr(self.comics_panel, 'show_tab'):
                self.comics_panel.show_tab(tab_name)
                
        except Exception as e:
            log_error(f"Error showing comics tab '{tab_name}': {e}")
            messagebox.showerror(
                "Error",
                f"Could not switch to {tab_name} tab: {str(e)}"
            )
    
    def _update_status(self):
        """Update the status bar with current information."""
        try:
            # Get database stats if available
            if hasattr(self, 'comics_panel') and hasattr(self.comics_panel, 'db'):
                count = self.comics_panel.db.get_comic_count()
                self.status_var.set(tr('comics_in_database', count=count))
            else:
                self.status_var.set(tr('not_connected_to_database'))
        except Exception as e:
            log_error(f"Error updating status: {e}")
            self.status_var.set(tr('error_loading_status'))
  
    def append_log(self, text):
        """Append text to the log box."""
        try:
            self.log_box.config(state='normal')
            self.log_box.insert(tk.END, text + '\n')
            self.log_box.see(tk.END)
            self.log_box.config(state='disabled')
            log_info(text.strip())
        except Exception as e:
            log_error(f"Error appending to log: {e}")

    def _show_success(self, msg):
        """Show a success message in the log."""
        log_info(f"SUCCESS: {msg}")
        self.append_log(f"SUCCESS: {msg}")

    def _show_error(self, msg):
        """Show an error message in the log."""
        log_error(f"ERROR: {msg}")
        self.append_log(f"ERROR: {msg}")
    
    def on_close(self):
        """Handle window close event."""
        from tkinter import messagebox
        if messagebox.askokcancel(tr('quit'), tr('Do you want to quit?')):
            self.cleanup()
            # First destroy all widgets
            for widget in self.parent.winfo_children():
                widget.destroy()
            # Stop any running loops
            self.parent.quit()
            # Ensure the application exits
            self.parent.destroy()
            # Force exit the application
            import os
            os._exit(0)
    
    def cleanup(self):
        """Clean up resources before closing the application."""
        try:
            # Clean up the comics panel if it exists
            if hasattr(self, 'comics_panel') and hasattr(self.comics_panel, 'cleanup'):
                self.comics_panel.cleanup()
                
            # Commit any pending transactions and close database connections
            if hasattr(self, 'comics_panel') and hasattr(self.comics_panel, 'db') and self.comics_panel.db:
                try:
                    if hasattr(self.comics_panel.db.conn, 'commit'):
                        self.comics_panel.db.conn.commit()
                        log_info("Committed pending transactions")
                except Exception as commit_error:
                    log_error(f"Error committing transactions: {commit_error}")
                
                # Close the database connection
                try:
                    if hasattr(self.comics_panel.db, 'close'):
                        self.comics_panel.db.close()
                        log_info("Database connection closed")
                except Exception as close_error:
                    log_error(f"Error closing database: {close_error}")
            
            # Clear any after events
            if hasattr(self, 'parent') and self.parent:
                for after_id in self.parent.tk.eval('after info').split():
                    self.parent.after_cancel(after_id)
                    
        except Exception as e:
            log_error(f"Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
