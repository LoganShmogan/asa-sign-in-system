# screens/admin_screen.py — Admin Password Gate + Settings Panel

import tkinter as tk

import theme
import database
import facebook_api
from components.widgets import (
    TouchButton, SectionLabel, MutedLabel,
    Divider, StyledEntry, PopupOverlay
)


# ── Password Gate ─────────────────────────────────────────────────────────────

class AdminPasswordScreen(tk.Frame):
    """Shown when the user taps ADMIN. Password gates the admin panel."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.PAGE_BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Centre everything
        outer = tk.Frame(self, bg=theme.PAGE_BG)
        outer.place(relx=0.5, rely=0.5, anchor="center")

        SectionLabel(outer, text="PASSWORD PROTECTED",
                     font_cfg=theme.F_H2).pack(pady=(0, 8))
        MutedLabel(outer, text="Enter the admin password to continue.").pack()
        Divider(outer).pack(fill="x", pady=12)

        self._pw_entry = StyledEntry(outer, placeholder="Password", width=30,
                                     show="•")
        self._pw_entry.pack(ipady=12, pady=(0, 16))

        btn_row = tk.Frame(outer, bg=theme.PAGE_BG)
        btn_row.pack()

        TouchButton(btn_row, text="Cancel",
                    command=self._go_back,
                    bg=theme.PAGE_BG, fg=theme.MUTED_TEXT,
                    hover_bg=theme.BORDER_COLOR).pack(side="left", padx=6)

        TouchButton(btn_row, text="Enter",
                    command=self._attempt,
                    bg=theme.BTN_BG, fg=theme.PRIMARY_TEXT).pack(side="left", padx=6)

        # Allow Enter key on touchscreen keyboards
        self._pw_entry.bind("<Return>", lambda e: self._attempt())

    def _attempt(self):
        pw = self._pw_entry.get()
        if database.check_admin_password(pw):
            self._pw_entry.delete(0, tk.END)
            self.app.show_screen("admin_panel")
        else:
            popup = PopupOverlay(self.winfo_toplevel(), is_error=True)
            popup.set_message("Incorrect password. Please try again.")
            popup.add_button("OK", popup.destroy)
            self._pw_entry.delete(0, tk.END)

    def _go_back(self):
        self.app.show_screen("signin")

    def on_show(self, **_):
        self._pw_entry.delete(0, tk.END)
        self.after(100, lambda: self._pw_entry.focus_set())


# ── Admin Panel ───────────────────────────────────────────────────────────────

class AdminPanelScreen(tk.Frame):
    """Full admin settings: Facebook credentials, password change, add member."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.PAGE_BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Top bar
        bar = tk.Frame(self, bg=theme.PAGE_BG)
        bar.pack(fill="x", padx=24, pady=(16, 0))

        TouchButton(bar, text="← Back",
                    command=lambda: self.app.show_screen("signin"),
                    bg=theme.PAGE_BG, fg=theme.MUTED_TEXT,
                    hover_bg=theme.BORDER_COLOR,
                    font_cfg=theme.F_LABEL).pack(side="left")

        SectionLabel(bar, text="Admin Settings").pack(side="left", padx=20)

        Divider(self).pack(fill="x", padx=24, pady=(8, 16))

        # ── Scrollable content ────────────────────────────────────────────────
        outer = tk.Frame(self, bg=theme.PAGE_BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=theme.PAGE_BG, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        sf = tk.Frame(canvas, bg=theme.PAGE_BG)
        win = canvas.create_window((0, 0), window=sf, anchor="nw")
        sf.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))

        # Build sections inside sf
        cols = tk.Frame(sf, bg=theme.PAGE_BG)
        cols.pack(fill="both", expand=True, padx=40, pady=8)

        left  = tk.Frame(cols, bg=theme.PAGE_BG)
        right = tk.Frame(cols, bg=theme.PAGE_BG)
        left.pack (side="left", fill="both", expand=True, padx=(0, 40))
        right.pack(side="left", fill="both", expand=True)

        # ── LEFT: Facebook settings ───────────────────────────────────────────
        self._section(left, "Facebook Notices (Graph API)")

        MutedLabel(left, text="Page ID").pack(anchor="w")
        self._fb_page = StyledEntry(left, placeholder="e.g. 123456789012345", width=38)
        self._fb_page.pack(anchor="w", ipady=8, pady=(0, 8))

        MutedLabel(left, text="Page Access Token").pack(anchor="w")
        self._fb_token = StyledEntry(left, placeholder="EAAxxxx…", width=38)
        self._fb_token.pack(anchor="w", ipady=8, pady=(0, 4))

        MutedLabel(left, text=(
            "Get a long-lived Page Access Token from\n"
            "developers.facebook.com → Graph API Explorer.\n"
            "Token never leaves this device."
        )).pack(anchor="w", pady=(0, 8))

        btn_row_fb = tk.Frame(left, bg=theme.PAGE_BG)
        btn_row_fb.pack(anchor="w")
        TouchButton(btn_row_fb, text="Save Credentials",
                    command=self._save_fb,
                    bg=theme.BTN_BG, fg=theme.PRIMARY_TEXT,
                    font_cfg=theme.F_LABEL).pack(side="left", padx=(0, 8))
        TouchButton(btn_row_fb, text="Test & Fetch Now",
                    command=self._test_fb,
                    bg=theme.BTN_ORANGE_BG, fg=theme.SECONDARY_TEXT,
                    hover_bg=theme.BTN_ORANGE_HOV,
                    font_cfg=theme.F_LABEL).pack(side="left")

        self._fb_status = MutedLabel(left, text="")
        self._fb_status.pack(anchor="w", pady=4)

        # ── RIGHT: Password + Add Member ──────────────────────────────────────
        self._section(right, "Change Admin Password")

        MutedLabel(right, text="New Password").pack(anchor="w")
        self._new_pw = StyledEntry(right, placeholder="New password", width=32,
                                   show="•")
        self._new_pw.pack(anchor="w", ipady=8, pady=(0, 4))

        MutedLabel(right, text="Confirm Password").pack(anchor="w")
        self._conf_pw = StyledEntry(right, placeholder="Confirm password", width=32,
                                    show="•")
        self._conf_pw.pack(anchor="w", ipady=8, pady=(0, 8))

        TouchButton(right, text="Update Password",
                    command=self._change_pw,
                    bg=theme.BTN_BG, fg=theme.PRIMARY_TEXT,
                    font_cfg=theme.F_LABEL).pack(anchor="w")

        self._pw_status = MutedLabel(right, text="")
        self._pw_status.pack(anchor="w", pady=4)

        Divider(right).pack(fill="x", pady=12)

        self._section(right, "Add New Member")
        MutedLabel(right, text=(
            "To add a new member, tap the button below.\n"
            "You will be taken to a blank profile form."
        )).pack(anchor="w", pady=(0, 8))

        TouchButton(right, text="+ New Member",
                    command=self._new_member,
                    bg=theme.BTN_SUCCESS_BG, fg=theme.SECONDARY_TEXT,
                    hover_bg=theme.BTN_SUCCESS_HOV,
                    font_cfg=theme.F_LABEL).pack(anchor="w")

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _section(self, parent, title):
        tk.Label(parent, text=title, bg=theme.PAGE_BG,
                 fg=theme.BTN_BG, font=theme.F_H3).pack(anchor="w", pady=(12, 2))
        Divider(parent).pack(fill="x", pady=(0, 8))

    # ── Facebook ───────────────────────────────────────────────────────────────

    def _save_fb(self):
        page_id = self._fb_page.get_value().strip()
        token   = self._fb_token.get_value().strip()
        if not page_id or not token:
            self._fb_status.configure(text="Both Page ID and Token are required.")
            return
        facebook_api.set_fb_credentials(page_id, token)
        self._fb_status.configure(text="✓ Credentials saved to config.json")

    def _test_fb(self):
        self._save_fb()
        self._fb_status.configure(text="Fetching posts…")

        def _ok(posts):
            self.after(0, lambda: self._fb_status.configure(
                text=f"✓ Success — {len(posts)} posts fetched and saved."))

        def _err(exc):
            self.after(0, lambda: self._fb_status.configure(
                text=f"✗ Error: {str(exc)[:80]}"))

        facebook_api.refresh_notices_async(on_success=_ok, on_error=_err)

    # ── Password ───────────────────────────────────────────────────────────────

    def _change_pw(self):
        new  = self._new_pw.get()
        conf = self._conf_pw.get()
        if not new:
            self._pw_status.configure(text="Password cannot be empty.")
            return
        if new != conf:
            self._pw_status.configure(text="Passwords do not match.")
            return
        if len(new) < 6:
            self._pw_status.configure(text="Password must be at least 6 characters.")
            return
        database.set_admin_password(new)
        self._new_pw.delete(0, tk.END)
        self._conf_pw.delete(0, tk.END)
        self._pw_status.configure(text="✓ Password updated successfully.")

    # ── New member ─────────────────────────────────────────────────────────────

    def _new_member(self):
        self.app.show_screen("profile", member=None)

    def on_show(self, **_):
        # Pre-fill existing FB credentials if set
        page_id, token = facebook_api.get_fb_credentials()
        if page_id:
            self._fb_page.delete(0, tk.END)
            self._fb_page.configure(fg=theme.PRIMARY_TEXT)
            self._fb_page.insert(0, page_id)
        if token:
            self._fb_token.delete(0, tk.END)
            self._fb_token.configure(fg=theme.PRIMARY_TEXT)
            self._fb_token.insert(0, token)
        self._fb_status.configure(text="")
        self._pw_status.configure(text="")
