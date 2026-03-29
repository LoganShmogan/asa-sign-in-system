# screens/profile_screen.py — Child / Caregiver Profile Screen

import tkinter as tk
from tkinter import ttk

import theme
import database
from components.widgets import (
    TouchButton, SectionLabel, MutedLabel,
    Divider, StyledEntry, PopupOverlay
)


class ProfileScreen(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.PAGE_BG)
        self.app    = app
        self.member = None
        self._fields_member   = {}
        self._fields_caregiver = {}
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        bar = tk.Frame(self, bg=theme.PAGE_BG)
        bar.pack(fill="x", padx=24, pady=(16, 0))

        TouchButton(bar, text="← Back",
                    command=self._go_back,
                    bg=theme.PAGE_BG, fg=theme.MUTED_TEXT,
                    hover_bg=theme.BORDER_COLOR,
                    font_cfg=theme.F_LABEL).pack(side="left")

        self._save_btn = TouchButton(bar, text="Save",
                    command=self._save,
                    bg=theme.BTN_SUCCESS_BG, fg=theme.SECONDARY_TEXT,
                    hover_bg=theme.BTN_SUCCESS_HOV,
                    font_cfg=theme.F_LABEL)
        self._save_btn.pack(side="right")

        TouchButton(bar, text="Delete Member",
                    command=self._confirm_delete,
                    bg=theme.BTN_DANGER_BG, fg=theme.SECONDARY_TEXT,
                    hover_bg=theme.BTN_DANGER_HOV,
                    font_cfg=theme.F_SMALL).pack(side="right", padx=8)

        SectionLabel(bar, text="Profile view").pack(side="left", padx=20)

        Divider(self).pack(fill="x", padx=24, pady=(8, 0))

        # Scrollable content area
        outer = tk.Frame(self, bg=theme.PAGE_BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=theme.PAGE_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._scroll_frame = tk.Frame(canvas, bg=theme.PAGE_BG)
        scroll_win = canvas.create_window((0, 0), window=self._scroll_frame,
                                          anchor="nw")
        self._scroll_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            scroll_win, width=e.width))

        # Touch scroll
        canvas.bind("<ButtonPress-1>", lambda e: setattr(self, "_sy0", e.y))
        canvas.bind("<B1-Motion>", lambda e: canvas.yview_scroll(
            int((self._sy0 - e.y) / 10), "units") or setattr(self, "_sy0", e.y))

        self._build_form(self._scroll_frame)

    def _build_form(self, parent):
        # ── Two column layout ─────────────────────────────────────────────────
        cols = tk.Frame(parent, bg=theme.PAGE_BG)
        cols.pack(fill="both", expand=True, padx=24, pady=12)

        left  = tk.Frame(cols, bg=theme.PAGE_BG)
        right = tk.Frame(cols, bg=theme.PAGE_BG)
        left.pack (side="left", fill="both", expand=True, padx=(0, 20))
        right.pack(side="left", fill="both", expand=True)

        # ── Left: Child info ──────────────────────────────────────────────────
        self._section(left, "Child Details")
        self._fields_member["first_name"]  = self._row(left, "First Name")
        self._fields_member["last_name"]   = self._row(left, "Last Name")
        self._fields_member["date_of_birth"] = self._row(left, "Date of Birth", hint="YYYY-MM-DD")
        self._fields_member["school"]      = self._row(left, "School Attending")

        self._section(left, "ASA Attendance")
        self._fields_member["mornings_asa"]   = self._checkbox_row(left, "Mornings attending ASA")
        self._fields_member["afternoons_asa"] = self._checkbox_row(left, "Afternoons attending ASA")
        self._fields_member["needs_pickup"]   = self._checkbox_row(left, "Will this child need pickup in the morning?")

        self._section(left, "Activity")
        self._fields_member["activity"]      = self._row(left, "What is the activity/s")
        self._fields_member["activity_time"] = self._row(left, "Time of activity/s")

        # Transport checkbox (cosmetic extra from Figma)
        self._transport_var = tk.IntVar()
        self._section(left, "Transport")
        tr_row = tk.Frame(left, bg=theme.PAGE_BG)
        tr_row.pack(fill="x", pady=2)
        tk.Label(tr_row, text="Is transport to activity/s required?",
                 bg=theme.PAGE_BG, fg=theme.SECONDARY_TEXT,
                 font=theme.F_SMALL).pack(side="left")
        yes_btn = tk.Checkbutton(tr_row, text="Yes", variable=self._transport_var,
                                  onvalue=1, offvalue=0,
                                  bg=theme.PAGE_BG, fg=theme.SECONDARY_TEXT,
                                  selectcolor=theme.BTN_SUCCESS_BG,
                                  font=theme.F_SMALL)
        yes_btn.pack(side="left", padx=8)
        self._fields_member["transport"] = self._transport_var

        # ── Right: Caregiver info ─────────────────────────────────────────────
        self._section(right, "Caregiver / Parent Details")
        self._fields_caregiver["full_name"]    = self._row(right, "Caregiver/Parent/s Name")
        self._fields_caregiver["phone"]        = self._row(right, "Phone Number")
        self._fields_caregiver["email"]        = self._row(right, "Email")
        self._fields_caregiver["street_address"] = self._row(right, "Street Address")
        self._fields_caregiver["suburb"]       = self._row(right, "Suburb")
        self._fields_caregiver["city"]         = self._row(right, "City")

        self._section(right, "Emergency Contact")
        self._fields_caregiver["emergency_contact_name"]  = self._row(right, "Emergency Contact Name")
        self._fields_caregiver["emergency_contact_phone"] = self._row(right, "Emergency Contact Phone Number")
        self._fields_caregiver["relationship"] = self._row(right, "Relationship")

        # Activity address (right side)
        self._section(right, "Activity Address")
        self._act_address = self._row(right, "Activity Address/es")

    # ── Form helpers ───────────────────────────────────────────────────────────

    def _section(self, parent, title):
        tk.Label(parent, text=title, bg=theme.PAGE_BG,
                 fg=theme.BTN_BG, font=theme.F_H3).pack(
                     anchor="w", pady=(14, 2))
        Divider(parent).pack(fill="x", pady=(0, 4))

    def _row(self, parent, label, hint=""):
        tk.Label(parent, text=label, bg=theme.PAGE_BG,
                 fg=theme.MUTED_TEXT, font=theme.F_SMALL).pack(anchor="w")
        ent = StyledEntry(parent, placeholder=hint or label, width=34)
        ent.pack(anchor="w", ipady=8, pady=(0, 2))
        return ent

    def _checkbox_row(self, parent, label):
        var = tk.IntVar()
        row = tk.Frame(parent, bg=theme.PAGE_BG)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg=theme.PAGE_BG,
                 fg=theme.SECONDARY_TEXT, font=theme.F_SMALL).pack(side="left")
        for text, val in [("Yes", 1), ("No", 0)]:
            tk.Checkbutton(row, text=text, variable=var,
                           onvalue=val, offvalue=1-val,
                           bg=theme.PAGE_BG, fg=theme.SECONDARY_TEXT,
                           selectcolor=theme.BTN_SUCCESS_BG,
                           font=theme.F_SMALL).pack(side="left", padx=4)
        return var

    # ── Populate / save ────────────────────────────────────────────────────────

    def _populate(self):
        if not self.member:
            return
        m  = self.member
        cg = database.get_caregiver(m["id"]) or {}

        _field_sets = {
            "first_name": m.get("first_name",""),
            "last_name":  m.get("last_name",""),
            "date_of_birth": m.get("date_of_birth",""),
            "school":     m.get("school",""),
            "activity":   m.get("activity",""),
            "activity_time": m.get("activity_time",""),
        }
        for key, val in _field_sets.items():
            widget = self._fields_member.get(key)
            if widget and isinstance(widget, StyledEntry):
                widget.delete(0, tk.END)
                widget.configure(fg=theme.PRIMARY_TEXT)
                widget.insert(0, val)

        for key in ("mornings_asa", "afternoons_asa", "needs_pickup"):
            var = self._fields_member.get(key)
            if var:
                var.set(int(m.get(key, 0)))

        cg_text = {
            "full_name": cg.get("full_name",""),
            "phone":     cg.get("phone",""),
            "email":     cg.get("email",""),
            "street_address": cg.get("street_address",""),
            "suburb":    cg.get("suburb",""),
            "city":      cg.get("city",""),
            "emergency_contact_name":  cg.get("emergency_contact_name",""),
            "emergency_contact_phone": cg.get("emergency_contact_phone",""),
            "relationship": cg.get("relationship",""),
        }
        for key, val in cg_text.items():
            widget = self._fields_caregiver.get(key)
            if widget and isinstance(widget, StyledEntry):
                widget.delete(0, tk.END)
                widget.configure(fg=theme.PRIMARY_TEXT)
                widget.insert(0, val)

    def _save(self):
        def _get(fields, key):
            w = fields.get(key)
            if w is None: return ""
            if isinstance(w, StyledEntry): return w.get_value()
            if isinstance(w, tk.IntVar):   return w.get()
            return ""

        member_data = {
            "id":            self.member["id"] if self.member else None,
            "first_name":    _get(self._fields_member, "first_name"),
            "last_name":     _get(self._fields_member, "last_name"),
            "date_of_birth": _get(self._fields_member, "date_of_birth"),
            "school":        _get(self._fields_member, "school"),
            "mornings_asa":  _get(self._fields_member, "mornings_asa"),
            "afternoons_asa":_get(self._fields_member, "afternoons_asa"),
            "needs_pickup":  _get(self._fields_member, "needs_pickup"),
            "activity":      _get(self._fields_member, "activity"),
            "activity_time": _get(self._fields_member, "activity_time"),
        }
        if not member_data["first_name"] or not member_data["last_name"]:
            popup = PopupOverlay(self.winfo_toplevel(), is_error=True)
            popup.set_message("First name and last name are required.")
            popup.add_button("OK", popup.destroy)
            return

        mid = database.upsert_member(member_data)

        cg_data = {
            "member_id":               mid,
            "full_name":               _get(self._fields_caregiver, "full_name"),
            "phone":                   _get(self._fields_caregiver, "phone"),
            "email":                   _get(self._fields_caregiver, "email"),
            "street_address":          _get(self._fields_caregiver, "street_address"),
            "suburb":                  _get(self._fields_caregiver, "suburb"),
            "city":                    _get(self._fields_caregiver, "city"),
            "emergency_contact_name":  _get(self._fields_caregiver, "emergency_contact_name"),
            "emergency_contact_phone": _get(self._fields_caregiver, "emergency_contact_phone"),
            "relationship":            _get(self._fields_caregiver, "relationship"),
        }
        database.upsert_caregiver(cg_data)

        # Update self.member so back navigation works
        self.member = database.get_member(mid)

        popup = PopupOverlay(self.winfo_toplevel(), is_error=False)
        popup.set_message("Profile saved successfully.")
        popup.add_button("OK", popup.destroy,
                         bg=theme.BTN_SUCCESS_BG, fg="white",
                         hover_bg=theme.BTN_SUCCESS_HOV)

    def _confirm_delete(self):
        if not self.member:
            return
        name = f"{self.member['first_name']} {self.member['last_name']}"
        popup = PopupOverlay(self.winfo_toplevel(), is_error=True, width=520)
        popup.set_message(
            f"Are you sure you want to permanently delete {name}? "
            "This cannot be undone."
        )
        popup.add_button("Cancel", popup.destroy)
        popup.add_button("Delete", lambda: self._do_delete(popup),
                         bg=theme.BTN_DANGER_BG, fg="white",
                         hover_bg=theme.BTN_DANGER_HOV)

    def _do_delete(self, popup):
        database.delete_member(self.member["id"])
        popup.destroy()
        self._go_back()

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _go_back(self):
        if self.member:
            self.app.show_screen("signature", member=self.member)
        else:
            self.app.show_screen("signin")

    def on_show(self, member=None):
        self.member = member
        self._populate()
