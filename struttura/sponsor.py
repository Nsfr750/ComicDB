import tkinter as tk
import webbrowser
from .lang import tr

# Sponsor Class

class Sponsor:
    def __init__(self, root):
        self.root = root

    def show_sponsor(self):
        dialog = tk.Toplevel(self.root)
        dialog.title(tr('sponsor'))
        dialog.geometry('500x150')
        
        # Sponsor buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        buttons = [
            (tr('sponsor_on_github'), "https://github.com/sponsors/Nsfr750"),
            (tr('join_discord'), "https://discord.gg/BvvkUEP9"),
            (tr('buy_me_a_coffee'), "https://paypal.me/3dmega"),
            (tr('join_the_patreon'), "https://www.patreon.com/Nsfr750")
        ]
        
        for text, url in buttons:
            btn = tk.Button(btn_frame, text=text, pady=5,
                          command=lambda u=url: webbrowser.open(u))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        tk.Button(dialog, text=tr('close'), command=dialog.destroy).pack(pady=10)
