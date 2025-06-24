import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import re
from datetime import datetime
import threading
import queue
from .lang import tr

LOG_FILE = 'traceback.log'
LOG_LEVELS = ["ALL", "INFO", "WARNING", "ERROR"]
LOG_COLORS = {
    'INFO': 'black',
    'WARNING': 'orange',
    'ERROR': 'red',
    'CRITICAL': 'purple',
    'DEBUG': 'blue'
}

class LogViewer:
    """
    An enhanced log viewer with filtering, search, and auto-refresh capabilities.
    """
    @classmethod
    def show_log(cls, root):
        """Show the log viewer dialog."""
        log_window = tk.Toplevel(root)
        log_viewer = cls(log_window, root)
        log_window.transient(root)
        log_window.grab_set()
        root.wait_window(log_window)
    
    def __init__(self, parent, root_window):
        self.parent = parent
        self.root_window = root_window
        self.log_queue = queue.Queue()
        self.auto_refresh = tk.BooleanVar(value=True)
        self.word_wrap = tk.BooleanVar(value=True)
        self.font_size = tk.IntVar(value=10)
        self.last_file_size = 0
        self.filter_pattern = tk.StringVar()
        self.setup_ui()
        self.update_log()
        self.schedule_update()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.parent.title(f"{tr('log_viewer_title')} - {LOG_FILE}")
        self.parent.geometry('900x600')
        self.parent.minsize(600, 400)
        
        # Configure grid weights
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Toolbar frame
        toolbar = ttk.Frame(self.parent)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=2)
        
        # Log level filter
        ttk.Label(toolbar, text="Level:").pack(side=tk.LEFT, padx=2)
        self.selected_level = tk.StringVar(value="ALL")
        for level in LOG_LEVELS:
            btn = ttk.Radiobutton(
                toolbar, text=level, variable=self.selected_level, 
                value=level, command=self.update_display
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Search box
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(10, 2))
        search_entry = ttk.Entry(toolbar, textvariable=self.filter_pattern, width=30)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind('<Return>', lambda e: self.update_display())
        
        # Buttons frame
        btn_frame = ttk.Frame(toolbar)
        btn_frame.pack(side=tk.RIGHT, padx=5)
        
        # Font controls
        ttk.Button(btn_frame, text="A-", command=self.decrease_font).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="A+", command=self.increase_font).pack(side=tk.LEFT, padx=2)
        
        # Toggle buttons
        ttk.Checkbutton(
            btn_frame, text="Auto-refresh", variable=self.auto_refresh
        ).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(
            btn_frame, text="Word Wrap", variable=self.word_wrap, 
            command=self.toggle_word_wrap
        ).pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        ttk.Button(btn_frame, text="Refresh", command=self.force_update).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Copy", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        
        # Log text area
        text_frame = ttk.Frame(self.parent)
        text_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        self.text_area = tk.Text(
            text_frame, wrap=tk.WORD, font=('Consolas', self.font_size.get()),
            bg='white', fg='black', insertbackground='black',
            padx=5, pady=5, undo=True
        )
        
        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        hsb = ttk.Scrollbar(text_frame, orient="horizontal", command=self.text_area.xview)
        self.text_area.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.text_area.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(
            self.parent, textvariable=self.status_var,
            relief=tk.SUNKEN, anchor=tk.W, padding=2
        )
        status_bar.grid(row=2, column=0, sticky='ew')
        
        # Context menu
        self.context_menu = tk.Menu(self.text_area, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_command(label="Clear", command=self.clear_log)
        
        self.text_area.bind("<Button-3>", self.show_context_menu)
        
        # Close window handler
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Initial status
        self.update_status()
    
    def load_log_lines(self):
        """Load log lines from file."""
        if not os.path.exists(LOG_FILE):
            return []
        try:
            with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                return f.readlines()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read log file: {e}")
            return []
    
    def filter_lines(self, lines, level, pattern=None):
        """Filter log lines by level and search pattern."""
        filtered = []
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Filter by level
            if level != "ALL" and f"[{level}]" not in line:
                continue
                
            # Filter by search pattern
            if pattern and pattern.lower() not in line.lower():
                continue
                
            filtered.append(line)
        return filtered
    
    def update_display(self, event=None):
        """Update the log display with filtered content."""
        try:
            lines = self.load_log_lines()
            filtered = self.filter_lines(
                lines, 
                self.selected_level.get(),
                self.filter_pattern.get() if self.filter_pattern.get().strip() else None
            )
            
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            
            if not filtered:
                self.text_area.insert(tk.END, tr('no_log_entries', level=self.selected_level.get()))
            else:
                self.apply_syntax_highlighting('\n'.join(filtered))
            
            self.text_area.see(tk.END)
            self.text_area.config(state=tk.DISABLED)
            self.update_status(len(filtered), len(lines))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update log display: {e}")
    
    def apply_syntax_highlighting(self, text):
        """Apply syntax highlighting to log entries."""
        for level, color in LOG_COLORS.items():
            pattern = re.compile(fr'(\[\d-]+\s[\d:]+\]\s*\[\s*{level}\])')
            for match in pattern.finditer(text):
                start = match.start()
                end = text.find('\n', start)
                if end == -1:
                    end = len(text)
                self.text_area.insert(tk.END, text[start:end] + '\n')
                self.text_area.tag_add(level, f"{self.text_area.index('end-2l')} linestart", f"{self.text_area.index('end-1l')} lineend")
                self.text_area.tag_config(level, foreground=color)
    
    def update_status(self, filtered_count=None, total_count=None):
        """Update the status bar."""
        try:
            size = os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0
            size_str = f"{size/1024:.1f} KB"
            count_str = f"{filtered_count}/{total_count}" if filtered_count is not None and total_count is not None else ""
            self.status_var.set(f"File: {LOG_FILE} | Size: {size_str} | Entries: {count_str} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def schedule_update(self):
        """Schedule the next log update."""
        if self.auto_refresh.get():
            self.update_log()
        self.parent.after(2000, self.schedule_update)
    
    def update_log(self):
        """Check for log file changes and update display if needed."""
        try:
            current_size = os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0
            if current_size != self.last_file_size:
                self.last_file_size = current_size
                self.update_display()
        except Exception as e:
            self.status_var.set(f"Error checking log file: {e}")
    
    def force_update(self):
        """Force an immediate log update."""
        self.update_display()
    
    def copy_to_clipboard(self):
        """Copy selected text to clipboard."""
        try:
            selected_text = self.text_area.get("sel.first", "sel.last")
            if not selected_text:
                selected_text = self.text_area.get(1.0, tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection
    
    def clear_log(self):
        """Clear the log file after confirmation."""
        if messagebox.askyesno("Confirm", "Clear the entire log file? This cannot be undone."):
            try:
                with open(LOG_FILE, 'w', encoding='utf-8') as f:
                    f.write("")
                self.update_display()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear log file: {e}")
    
    def toggle_word_wrap(self):
        """Toggle word wrap on/off."""
        wrap_mode = tk.WORD if self.word_wrap.get() else tk.NONE
        self.text_area.config(wrap=wrap_mode)
    
    def increase_font(self):
        """Increase the font size."""
        self.font_size.set(min(24, self.font_size.get() + 1))
        self.text_area.config(font=('Consolas', self.font_size.get()))
    
    def decrease_font(self):
        """Decrease the font size."""
        self.font_size.set(max(6, self.font_size.get() - 1))
        self.text_area.config(font=('Consolas', self.font_size.get()))
    
    def select_all(self):
        """Select all text in the log viewer."""
        self.text_area.tag_add('sel', '1.0', 'end')
    
    def show_context_menu(self, event):
        """Show the context menu."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def on_close(self):
        """Handle window close event."""
        self.parent.destroy()
