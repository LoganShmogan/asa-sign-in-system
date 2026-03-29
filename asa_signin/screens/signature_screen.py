# screens/signature_screen.py — Sign-in / Sign-out Signature Screen

import tkinter as tk
from datetime import datetime

import theme
import database
from components.widgets import (
    TouchButton, SignInButton, SignOutButton,
    SectionLabel, MutedLabel, Divider,
    SignatureCanvas, PopupOverlay, StyledEntry
)


class SignatureScreen(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.PAGE_BG)
        self.app    = app
        self.member = None
        self._direction = tk.StringVar(value="IN")
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Back button
        back_row = tk.Frame(self, bg=theme.PAGE_BG)
        back_row.pack(fill="x", padx=24, pady=(16, 0))

        TouchButton(back_row, text="← Back",
                    command=self._go_back,
                    bg=theme.PAGE_BG, fg=theme.MUTED_TEXT,
                    hover_bg=theme.BORDER_COLOR,
                    font_cfg=theme.F_LABEL).pack(side="left")

        TouchButton(back_row, text="Edit Profile",
                    command=self._go_profile,
                    bg=theme.BTN_ORANGE_BG, fg=theme.SECONDARY_TEXT,
                    hover_bg=theme.BTN_ORANGE_HOV,
                    font_cfg=theme.F_LABEL).pack(side="right")

        Divider(self).pack(fill="x", padx=24, pady=(8, 0))

        # ── Main content row ──────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.PAGE_BG)
        content.pack(fill="both", expand=True, padx=40, pady=20)

        # Left column — greeting + IN/OUT + sign/submit
        left = tk.Frame(content, bg=theme.PAGE_BG)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Hello!", bg=theme.PAGE_BG,
                 fg=theme.SECONDARY_TEXT, font=theme.F_H1).pack(anchor="w")

        self._name_lbl = tk.Label(left, text="", bg=theme.PAGE_BG,
                                  fg=theme.MUTED_TEXT, font=theme.F_H3)
        self._name_lbl.pack(anchor="w", pady=(0, 20))

        # IN / OUT toggle buttons
        toggle_row = tk.Frame(left, bg=theme.PAGE_BG)
        toggle_row.pack(anchor="w", pady=(0, 24))

        self._btn_in  = SignInButton(toggle_row,  text="IN",  command=lambda: self._set_dir("IN"),
                                     font_cfg=theme.F_H2, width=8, height=2)
        self._btn_out = SignOutButton(toggle_row, text="OUT", command=lambda: self._set_dir("OUT"),
                                      font_cfg=theme.F_H2, width=8, height=2)
        self._btn_in.pack (side="left", padx=(0, 8))
        self._btn_out.pack(side="left")

        # Right column — timestamp, notes, signature
        right = tk.Frame(content, bg=theme.PAGE_BG, padx=40)
        right.pack(side="left", fill="both", expand=True)

        # Direction badge
        self._dir_badge = tk.Label(right, text="Sign-in", bg=theme.BTN_SUCCESS_BG,
                                   fg="white", font=theme.F_LABEL, padx=12, pady=4)
        self._dir_badge.pack(anchor="e")

        # Timestamp
        ts_row = tk.Frame(right, bg=theme.PAGE_BG)
        ts_row.pack(fill="x", pady=(8, 0))
        tk.Label(ts_row, text="Time Stamp", bg=theme.PAGE_BG,
                 fg=theme.SECONDARY_TEXT, font=theme.F_LABEL).pack(side="left")
        MutedLabel(ts_row, text="AUTO STAMP", bg=theme.PAGE_BG).pack(side="right")

        self._ts_lbl = tk.Label(right, text="", bg=theme.PAGE_BG,
                                fg=theme.MUTED_TEXT, font=theme.F_SMALL)
        self._ts_lbl.pack(anchor="w")

        Divider(right).pack(fill="x", pady=8)

        # Notes
        tk.Label(right, text="Notes", bg=theme.PAGE_BG,
                 fg=theme.SECONDARY_TEXT, font=theme.F_LABEL).pack(anchor="w")
        self._notes_text = tk.Text(right, width=36, height=4,
                                   bg=theme.ENT_BG, fg=theme.PRIMARY_TEXT,
                                   font=theme.F_INPUT, relief="flat",
                                   highlightthickness=2,
                                   highlightbackground=theme.ENT_BORDER,
                                   insertbackground="black")
        self._notes_text.pack(anchor="w", pady=(4, 0))

        Divider(right).pack(fill="x", pady=8)

        # Signature
        tk.Label(right, text="Signature", bg=theme.PAGE_BG,
                 fg=theme.SECONDARY_TEXT, font=theme.F_LABEL).pack(anchor="w")
        self._sig_canvas = SignatureCanvas(right, width=360, height=130)
        self._sig_canvas.pack(anchor="w", pady=(4, 0))

        sig_actions = tk.Frame(right, bg=theme.PAGE_BG)
        sig_actions.pack(anchor="w", pady=4)
        TouchButton(sig_actions, text="Clear",
                    command=self._sig_canvas.clear,
                    bg=theme.PAGE_BG, fg=theme.MUTED_TEXT,
                    hover_bg=theme.BORDER_COLOR,
                    font_cfg=theme.F_SMALL).pack(side="left")

        # Submit button (full width at bottom)
        Divider(self).pack(fill="x", padx=40, pady=(0, 8))

        self._submit_btn = TouchButton(
            self, text="SIGN IN",
            command=self._submit,
            bg=theme.BTN_SUCCESS_BG, fg=theme.SECONDARY_TEXT,
            hover_bg=theme.BTN_SUCCESS_HOV,
            font_cfg=theme.F_H3
        )
        self._submit_btn.pack(pady=(0, 20), ipady=12, ipadx=60)

    # ── Direction toggle ───────────────────────────────────────────────────────

    def _set_dir(self, direction):
        self._direction.set(direction)
        if direction == "IN":
            self._btn_in.configure(relief="sunken")
            self._btn_out.configure(relief="flat")
            self._dir_badge.configure(text="Sign-in",  bg=theme.BTN_SUCCESS_BG)
            self._submit_btn.configure(text="SIGN IN",
                                       bg=theme.BTN_SUCCESS_BG,
                                       activebackground=theme.BTN_SUCCESS_HOV)
            self._submit_btn._bg       = theme.BTN_SUCCESS_BG
            self._submit_btn._hover_bg = theme.BTN_SUCCESS_HOV
        else:
            self._btn_in.configure(relief="flat")
            self._btn_out.configure(relief="sunken")
            self._dir_badge.configure(text="Sign-out", bg=theme.BTN_DANGER_BG)
            self._submit_btn.configure(text="SIGN OUT",
                                       bg=theme.BTN_DANGER_BG,
                                       activebackground=theme.BTN_DANGER_HOV)
            self._submit_btn._bg       = theme.BTN_DANGER_BG
            self._submit_btn._hover_bg = theme.BTN_DANGER_HOV

    # ── Submit ─────────────────────────────────────────────────────────────────

    def _submit(self):
        if not self.member:
            return

        notes   = self._notes_text.get("1.0", tk.END).strip()
        sig_bytes = self._sig_canvas.export_bytes()
        direction = self._direction.get()

        database.record_sign(
            member_id=self.member["id"],
            direction=direction,
            notes=notes,
            signature=sig_bytes
        )

        name  = f"{self.member['first_name']} {self.member['last_name']}"
        label = "in" if direction == "IN" else "out"
        popup = PopupOverlay(self.winfo_toplevel(), title="Success",
                             is_error=False, width=480, height=220)
        popup.set_message(
            f"{name} has been signed {label} at "
            f"{datetime.now().strftime('%H:%M')}."
        )
        popup.add_button("Done", lambda: (popup.destroy(), self._go_back()),
                         bg=theme.BTN_SUCCESS_BG, fg="white",
                         hover_bg=theme.BTN_SUCCESS_HOV)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _go_back(self):
        self.app.show_screen("signin")

    def _go_profile(self):
        if self.member:
            self.app.show_screen("profile", member=self.member)

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def on_show(self, member=None):
        self.member = member
        if not member:
            return

        name = f"{member['first_name']} {member['last_name']}"
        self._name_lbl.configure(text=name)

        # Update timestamp
        self._ts_lbl.configure(
            text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))

        # Clear previous signature and notes
        self._sig_canvas.clear()
        self._notes_text.delete("1.0", tk.END)

        # Pre-fill notes if they have a note on their profile
        member_full = database.get_member(member["id"])
        if member_full:
            activity = member_full.get("activity", "")
            act_time = member_full.get("activity_time", "")
            if activity:
                self._notes_text.insert("1.0",
                    f"Activity: {activity}" + (f" — {act_time}" if act_time else ""))

        # Detect likely direction from last sign
        last = database.get_last_sign(member["id"])
        if last and last["direction"] == "IN":
            self._set_dir("OUT")
        else:
            self._set_dir("IN")
