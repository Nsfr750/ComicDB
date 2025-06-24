import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from pathlib import Path

class SplashScreen:
    def __init__(self, root, duration=3000):
        """
        Create a simple splash screen that displays for the specified duration.
        
        Args:
            root: The root window
            duration: Display duration in milliseconds (default: 3000ms)
        """
        self.root = root
        self.duration = duration
        
        # Create a top-level window for the splash screen
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)  # Remove window decorations
        
        # Set window size and position
        width, height = 400, 200
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create a canvas for drawing
        self.canvas = tk.Canvas(self.splash, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Draw the splash screen
        self._draw_splash()
        
        # Close after duration
        self.root.after(self.duration, self.close)
    
    def _draw_splash(self):
        """Draw the splash screen content."""
        # Draw background
        self.canvas.create_rectangle(0, 0, 400, 200, fill='#2c3e50', outline='')
        
        # Draw title
        self.canvas.create_text(
            200, 80,
            text="ComicDB",
            font=('Helvetica', 32, 'bold'),
            fill='#ecf0f1',
            anchor='center'
        )
        
        # Draw version
        from struttura.version import get_version
        self.canvas.create_text(
            200, 130,
            text=f"Version {get_version()}",
            font=('Helvetica', 12),
            fill='#bdc3c7',
            anchor='center'
        )
        
        # Draw loading text
        self.canvas.create_text(
            200, 170,
            text="Loading...",
            font=('Helvetica', 10),
            fill='#7f8c8d',
            anchor='center'
        )
    
    def close(self):
        """Close the splash screen."""
        self.splash.destroy()
        self.root.deiconify()  # Show the main window
