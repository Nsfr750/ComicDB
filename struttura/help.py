"""
Help Dialog Module

This module provides an enhanced Help dialog for ComicDB.
Features tabbed interface with comprehensive documentation,
keyboard shortcuts, and visual guides.

License: GPL v3.0 (see LICENSE)
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
from tkinter.scrolledtext import ScrolledText
from .lang import tr
import webbrowser

class Help:
    """Enhanced help system for ComicDB with improved UI and content organization."""
    
    @staticmethod
    def _create_section(parent, title, content, padx=5, pady=5):
        """Create a titled section with content."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=padx, pady=pady, anchor='nw')
        
        # Section title
        title_font = tkfont.Font(weight='bold', size=10)
        title_label = ttk.Label(frame, text=title, font=title_font)
        title_label.pack(anchor='w', pady=(0, 5))
        
        # Section content
        content_label = ttk.Label(
            frame, 
            text=content,
            wraplength=650,
            justify=tk.LEFT,
            anchor='nw'
        )
        content_label.pack(fill=tk.X, expand=True)
        
        return frame
    
    @classmethod
    def _create_usage_tab(cls, parent):
        """Create the Usage tab content."""
        frame = ttk.Frame(parent, padding=10)
        
        # Main description
        cls._create_section(
            frame,
            tr('getting_started'),
            tr('welcome_message')
        )
        
        # Importing Comics
        cls._create_section(
            frame,
            tr('importing_comics'),
            tr('import_steps')
        )
        
        # Browsing Your Collection
        cls._create_section(
            frame,
            tr('browsing_collection'),
            tr('browsing_tips')
        )
        
        return frame
    
    @classmethod
    def _create_features_tab(cls, parent):
        """Create the Features tab content."""
        frame = ttk.Frame(parent, padding=10)
        
        # Key Features
        cls._create_section(
            frame,
            tr('key_features'),
            tr('features_list')
        )
        
        # Keyboard Shortcuts
        cls._create_section(
            frame,
            tr('keyboard_shortcuts'),
            tr('shortcuts_list')
        )
        
        return frame
    
    @classmethod
    def _create_troubleshooting_tab(cls, parent):
        """Create the Troubleshooting tab content."""
        frame = ttk.Frame(parent, padding=10)
        
        # Common Issues
        cls._create_section(
            frame,
            tr('common_issues'),
            tr('common_issues_list')
        )
        
        # Support
        cls._create_section(
            frame,
            tr('getting_help'),
            tr('help_message')
        )
        
        # Support buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        def open_url(url):
            webbrowser.open(url)
        
        ttk.Button(
            btn_frame,
            text=tr('visit_support'),
            command=lambda: open_url("https://github.com/Nsfr750/ComicDB/issues")
        ).pack(side=tk.LEFT, padx=5)
        
        return frame
    
    @staticmethod
    def show_help(parent):
        """
        Display the enhanced Help dialog.
        
        Args:
            parent (tk.Tk): The parent window for the dialog
        """
        # Create and configure the help window
        help_window = tk.Toplevel(parent)
        help_window.title(f"{tr('help')} - ComicDB")
        help_window.geometry("800x600")
        help_window.minsize(700, 500)
        
        # Center the window on screen
        window_width = 800
        window_height = 600
        screen_width = help_window.winfo_screenwidth()
        screen_height = help_window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        help_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Create a notebook (tabbed interface)
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add tabs
        usage_tab = Help._create_usage_tab(notebook)
        features_tab = Help._create_features_tab(notebook)
        troubleshooting_tab = Help._create_troubleshooting_tab(notebook)
        
        notebook.add(usage_tab, text=tr('usage_tab'))
        notebook.add(features_tab, text=tr('features_tab'))
        notebook.add(troubleshooting_tab, text=tr('troubleshooting_tab'))
        
        # Close button
        btn_frame = ttk.Frame(help_window)
        btn_frame.pack(fill=tk.X, pady=10)
        
        close_btn = ttk.Button(
            btn_frame,
            text=tr('close'),
            command=help_window.destroy,
            width=15
        )
        close_btn.pack(side=tk.RIGHT, padx=10)
        
        # Make the window modal
        help_window.transient(parent)
        help_window.grab_set()
        help_window.focus_set()
        
        # Bind Escape key to close
        help_window.bind('<Escape>', lambda e: help_window.destroy())
        
        # Set focus to the window
        help_window.after(100, lambda: help_window.focus_force())
        
        parent.wait_window(help_window)
