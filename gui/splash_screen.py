import tkinter as tk
from PIL import Image, ImageTk
import os
from pathlib import Path

class SplashScreen:
    def __init__(self, root, image_path=None, duration=5000):
        """
        Create a splash screen that displays an image for a specified duration.
        
        Args:
            root: The root window
            image_path: Path to the splash image (default: looks for 'splash.png' in assets folder)
            duration: How long to display the splash screen in milliseconds (default: 5000ms)
        """
        self.root = root
        self.duration = duration
        
        # Hide the root window
        self.root.withdraw()
        
        # Create a top-level window for the splash screen
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)  # Remove window decorations
        
        # Set window position to center of screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Default image path if none provided
        if image_path is None:
            # Look for splash.png in the assets folder
            assets_dir = Path(__file__).parent.parent / 'images'
            image_path = assets_dir / 'splash.png'
            
            # Create assets directory if it doesn't exist
            assets_dir.mkdir(exist_ok=True)
            
            # If splash image doesn't exist, create a default one
            if not image_path.exists():
                self._create_default_splash(image_path)
        
        try:
            # Load the image
            img = Image.open(image_path)
            photo = ImageTk.PhotoImage(img)
            
            # Set window size to image size
            width, height = img.size
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.splash.geometry(f'{width}x{height}+{x}+{y}')
            
            # Display the image
            label = tk.Label(self.splash, image=photo)
            label.image = photo  # Keep a reference
            label.pack()
            
            # Close the splash screen after duration
            self.splash.after(self.duration, self.close)
            
        except Exception as e:
            print(f"Error loading splash image: {e}")
            self.splash.destroy()
            self.root.deiconify()
    
    def _create_default_splash(self, image_path):
        """Create a default splash image if none exists."""
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        # Create a simple blue gradient background
        width, height = 600, 400
        img = Image.new('RGB', (width, height), (30, 30, 60))
        draw = ImageDraw.Draw(img)
        
        # Add a gradient
        for i in range(height):
            r = int(30 + (i / height) * 50)
            g = int(30 + (i / height) * 50)
            b = int(60 + (i / height) * 60)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Add text
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
        
        app_name = "ComicDB"
        version = "1.0.0"
        
        # Draw app name
        text_bbox = draw.textbbox((0, 0), app_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 30
        
        # Draw text with shadow for better visibility
        draw.text((x+2, y+2), app_name, fill=(0, 0, 0), font=font)
        draw.text((x, y), app_name, fill=(255, 255, 255), font=font)
        
        # Draw version
        version_font = font.font_variant(size=16)
        version_bbox = draw.textbbox((0, 0), f"Version {version}", font=version_font)
        version_width = version_bbox[2] - version_bbox[0]
        
        x = (width - version_width) // 2
        y = (height + text_height) // 2 + 10
        
        draw.text((x+1, y+1), f"Version {version}", fill=(0, 0, 0), font=version_font)
        draw.text((x, y), f"Version {version}", fill=(200, 200, 255), font=version_font)
        
        # Save the image
        img.save(image_path, 'PNG')
    
    def close(self):
        """Close the splash screen and show the main window."""
        self.splash.destroy()
        self.root.deiconify()  # Show the main window
