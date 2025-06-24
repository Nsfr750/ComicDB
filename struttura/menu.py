import tkinter as tk
from tkinter import messagebox
import sys
from struttura.about import About
from struttura.help import Help
from struttura.sponsor import Sponsor
from struttura.log_viewer import LogViewer
from struttura.version import show_version, get_version
from struttura.updates import UpdateChecker
from struttura.lang import tr, set_language

LANG_OPTIONS = {'English': 'en', 'Italiano': 'it'}

def create_menu_bar(root, app):
    menubar = tk.Menu(root)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    
    # Comics submenu
    comics_menu = tk.Menu(file_menu, tearoff=0)
    comics_menu.add_command(
        label=tr('import_comics'), 
        command=lambda: app.show_comics_tab('import')
    )
    comics_menu.add_command(
        label=tr('browse_comics'), 
        command=lambda: app.show_comics_tab('browse')
    )
    comics_menu.add_separator()
    comics_menu.add_command(
        label=tr('manage_database'), 
        command=lambda: app.show_comics_tab('database')
    )
    
    file_menu.add_cascade(label=tr('comics'), menu=comics_menu)
    file_menu.add_separator()
    file_menu.add_command(label=tr('exit'), command=root.quit)
    menubar.add_cascade(label=tr('file'), menu=file_menu)
    
    # Log menu
    log_menu = tk.Menu(menubar, tearoff=0)
    log_menu.add_command(label=tr('view_log'), command=lambda: LogViewer.show_log(root))
    menubar.add_cascade(label=tr('log'), menu=log_menu)
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label=tr('help'), command=lambda: Help.show_help(root))
    help_menu.add_separator()
    def do_update_check():
        try:
            checker = UpdateChecker(
                current_version=get_version(),
                update_url="https://api.github.com/repos/Nsfr750/ComicDB/releases/latest"
            )
            update_available, update_info = checker.check_for_updates(root, force_check=True)
            if update_available and update_info:
                checker.show_update_dialog(root, update_info)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Update Error", f"Failed to check for updates: {str(e)}")
    
    help_menu.add_command(label=tr('check_for_updates'), command=do_update_check)
    help_menu.add_separator()
    help_menu.add_command(label=tr('about'), command=lambda: About.show_about(root))
    help_menu.add_command(label=tr('sponsor'), command=lambda: Sponsor(root).show_sponsor())
    menubar.add_cascade(label=tr('help'), menu=help_menu)
    
    # Language menu
    def set_lang_and_restart(lang_code):
        from struttura.config import load_config, save_config
        set_language(lang_code)
        # Save the language preference to config
        config = load_config()
        config['language'] = lang_code
        save_config(config)
        # Restart the application
        root.destroy()
        import os
        os.execl(sys.executable, sys.executable, *sys.argv)

    lang_menu = tk.Menu(menubar, tearoff=0)
    for label, code in LANG_OPTIONS.items():
        lang_menu.add_command(label=label, command=lambda c=code: set_lang_and_restart(c))
    menubar.add_cascade(label=tr('language'), menu=lang_menu)

    root.config(menu=menubar)
    return menubar
