#!/usr/bin/env python3
# app.py — ASA Sign-in System  |  Entry point & screen controller
# Target: Raspberry Pi 3B+ at 1280×720 fullscreen touchscreen

import tkinter as tk
import sys
import os

# Ensure local modules resolve correctly when run from any CWD
sys.path.insert(0, os.path.dirname(__file__))

import database
import theme

# Screen imports
from screens.signin_screen    import SignInScreen
from screens.signature_screen import SignatureScreen
from screens.profile_screen   import ProfileScreen
from screens.admin_screen     import AdminPasswordScreen, AdminPanelScreen


# ── Application Controller ────────────────────────────────────────────────────

class App:
    """
    Manages the main Tk window and handles screen switching.
    All screens are created once and stacked via .lift() / .lower().
    """

    SCREEN_NAMES = ["signin", "signature", "profile",
                    "admin_password", "admin_panel"]

    def __init__(self):
        # ── Init DB ───────────────────────────────────────────────────────────
        database.init_db()

        # ── Root window ───────────────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("ASA Sign-in System")
        self.root.configure(bg=theme.PAGE_BG)

        # Fullscreen on Pi; Ctrl+Q to quit
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Control-q>", lambda e: self.root.destroy())
        self.root.bind("<Escape>",    lambda e: None)   # block accidental escape

        # Lock to 1280×720 (Pi resolution)
        self.root.geometry("1280x720")
        self.root.resizable(False, False)

        # ── Build screens ─────────────────────────────────────────────────────
        # Each screen fills the entire window; we raise the active one.
        self._screens: dict[str, tk.Frame] = {}

        self._screens["signin"]         = SignInScreen(self.root, self)
        self._screens["signature"]      = SignatureScreen(self.root, self)
        self._screens["profile"]        = ProfileScreen(self.root, self)
        self._screens["admin_password"] = AdminPasswordScreen(self.root, self)
        self._screens["admin_panel"]    = AdminPanelScreen(self.root, self)

        for screen in self._screens.values():
            screen.place(x=0, y=0, relwidth=1, relheight=1)

        # Show sign-in screen first
        self.show_screen("signin")

    def show_screen(self, name: str, **kwargs):
        """
        Raise the named screen above all others.
        Any keyword arguments (e.g. member=...) are passed to screen.on_show().
        """
        if name not in self._screens:
            raise ValueError(f"Unknown screen: {name!r}")

        screen = self._screens[name]
        screen.lift()

        # Let the screen configure itself for this visit
        if hasattr(screen, "on_show"):
            screen.on_show(**kwargs)

    def run(self):
        self.root.mainloop()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    App().run()
