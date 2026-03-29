# screens/signin_screen.py — Main Sign-in Screen (1280×720)
# Left panel: search + member list  |  Right panel: notices feed

import tkinter as tk
import threading
from datetime import datetime

import theme
import database
import facebook_api
from components.widgets import (
    TouchButton, SectionLabel, MutedLabel, Divider,
    NoticeCard, MemberListItem, StyledEntry
)


class SignInScreen(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.PAGE_BG)
        self.app = app          # reference to App controller for navigation
        self._search_after = None
        self._notice_index  = 0
        self._notices       = []

        self._build_ui()
        self.after(100, self._load_notices)

        # Auto-refresh notices every 15 minutes
        self._schedule_notice_refresh()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Left panel (800 px wide) ──────────────────────────────────────────
        self.frm_left = tk.Frame(self, bg=theme.PAGE_BG, width=800, height=720)
        self.frm_left.place(x=0, y=0)
        self.frm_left.pack_propagate(False)

        # Top bar
        top_bar = tk.Frame(self.frm_left, bg=theme.PAGE_BG, height=60)
        top_bar.pack(fill="x", padx=24, pady=(16, 0))

        tk.Label(top_bar, text="ASA", bg=theme.PAGE_BG, fg=theme.BTN_BG,
                 font=theme.F_H2).pack(side="left")

        self._clock_lbl = tk.Label(top_bar, text="", bg=theme.PAGE_BG,
                                   fg=theme.MUTED_TEXT, font=theme.F_SMALL)
        self._clock_lbl.pack(side="right", pady=4)
        self._tick_clock()

        TouchButton(top_bar, text="ADMIN",
                    command=self._go_admin,
                    bg=theme.BTN_ORANGE_BG, fg=theme.SECONDARY_TEXT,
                    hover_bg=theme.BTN_ORANGE_HOV,
                    font_cfg=theme.F_LABEL).pack(side="right", padx=8)

        Divider(self.frm_left).pack(fill="x", padx=24, pady=(8, 0))

        # Search label + entry
        tk.Label(self.frm_left, text="Search name", bg=theme.PAGE_BG,
                 fg=theme.SECONDARY_TEXT, font=theme.F_H3).pack(
                     anchor="w", padx=24, pady=(18, 4))

        search_row = tk.Frame(self.frm_left, bg=theme.PAGE_BG)
        search_row.pack(fill="x", padx=24)

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)

        self._search_entry = StyledEntry(
            search_row, placeholder="Type a name…",
            textvariable=self._search_var, width=44
        )
        self._search_entry.pack(side="left", ipady=10)

        TouchButton(search_row, text="✕", command=self._clear_search,
                    bg=theme.PAGE_BG, fg=theme.MUTED_TEXT,
                    hover_bg=theme.BORDER_COLOR,
                    font_cfg=theme.F_BODY).pack(side="left", padx=4)

        # Member list (scrollable)
        list_container = tk.Frame(self.frm_left, bg=theme.PAGE_BG)
        list_container.pack(fill="both", expand=True, padx=24, pady=8)

        self._list_canvas = tk.Canvas(list_container, bg=theme.PAGE_BG,
                                      highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical",
                                 command=self._list_canvas.yview)
        self._list_canvas.configure(yscrollcommand=scrollbar.set)

        self._list_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._list_frame = tk.Frame(self._list_canvas, bg=theme.PAGE_BG)
        self._list_window = self._list_canvas.create_window(
            (0, 0), window=self._list_frame, anchor="nw"
        )
        self._list_frame.bind("<Configure>", self._on_list_resize)
        self._list_canvas.bind("<Configure>", self._on_canvas_resize)

        # Touch scroll binding
        self._list_canvas.bind("<ButtonPress-1>", self._scroll_start)
        self._list_canvas.bind("<B1-Motion>",     self._scroll_move)

        # Initial population
        self._populate_list(database.search_members(""))

        # ── Right panel / notices (480 px wide) ──────────────────────────────
        self.frm_right = tk.Frame(self, bg=theme.INFO_BG, width=480, height=720)
        self.frm_right.place(x=800, y=0)
        self.frm_right.pack_propagate(False)

        notices_top = tk.Frame(self.frm_right, bg=theme.INFO_BG)
        notices_top.pack(fill="x", padx=24, pady=(20, 0))

        SectionLabel(notices_top, text="Notices",
                     bg=theme.INFO_BG).pack(side="left")

        self._refresh_btn = TouchButton(
            notices_top, text="⟳", command=self._manual_refresh_notices,
            bg=theme.INFO_BG, fg=theme.MUTED_TEXT,
            hover_bg=theme.BORDER_COLOR, font_cfg=theme.F_BODY
        )
        self._refresh_btn.pack(side="right")

        self._notice_status = MutedLabel(self.frm_right, text="",
                                         bg=theme.INFO_BG)
        self._notice_status.pack(anchor="w", padx=24, pady=(0, 8))

        Divider(self.frm_right, bg=theme.BORDER_COLOR).pack(
            fill="x", padx=20, pady=(0, 8))

        # Scrollable notices area
        notice_container = tk.Frame(self.frm_right, bg=theme.INFO_BG)
        notice_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self._notice_canvas = tk.Canvas(notice_container, bg=theme.INFO_BG,
                                        highlightthickness=0)
        n_scroll = tk.Scrollbar(notice_container, orient="vertical",
                                command=self._notice_canvas.yview)
        self._notice_canvas.configure(yscrollcommand=n_scroll.set)
        self._notice_canvas.pack(side="left", fill="both", expand=True)
        n_scroll.pack(side="right", fill="y")

        self._notice_frame = tk.Frame(self._notice_canvas, bg=theme.INFO_BG)
        self._notice_canvas.create_window((0, 0), window=self._notice_frame,
                                          anchor="nw")
        self._notice_frame.bind("<Configure>", lambda e: self._notice_canvas.configure(
            scrollregion=self._notice_canvas.bbox("all")))

        # Touch scroll
        self._notice_canvas.bind("<ButtonPress-1>", self._nscroll_start)
        self._notice_canvas.bind("<B1-Motion>",     self._nscroll_move)

    # ── Clock ──────────────────────────────────────────────────────────────────

    def _tick_clock(self):
        now = datetime.now().strftime("%A %-d %B  %H:%M")
        self._clock_lbl.configure(text=now)
        self.after(10_000, self._tick_clock)

    # ── Member list ────────────────────────────────────────────────────────────

    def _on_search_change(self, *_):
        if self._search_after:
            self.after_cancel(self._search_after)
        self._search_after = self.after(200, self._do_search)

    def _do_search(self):
        query = self._search_var.get()
        if query == self._search_entry._placeholder:
            query = ""
        members = database.search_members(query)
        self._populate_list(members)

    def _clear_search(self):
        self._search_var.set("")
        self._search_entry.delete(0, tk.END)
        self._search_entry.insert(0, self._search_entry._placeholder)
        self._search_entry.configure(fg=theme.MUTED_TEXT)
        self._populate_list(database.search_members(""))

    def _populate_list(self, members):
        for w in self._list_frame.winfo_children():
            w.destroy()

        if not members:
            MutedLabel(self._list_frame, text="No members found.",
                       bg=theme.PAGE_BG).pack(pady=20)
            return

        for m in members:
            item = MemberListItem(self._list_frame, m,
                                  on_select=self._on_member_select)
            item.pack(fill="x", pady=1)

    def _on_member_select(self, member):
        self.app.show_screen("signature", member=member)

    def _on_list_resize(self, e):
        self._list_canvas.configure(
            scrollregion=self._list_canvas.bbox("all"))

    def _on_canvas_resize(self, e):
        self._list_canvas.itemconfig(self._list_window, width=e.width)

    # Touch scroll helpers
    def _scroll_start(self, e): self._scroll_y0 = e.y
    def _scroll_move(self, e):
        delta = self._scroll_y0 - e.y
        self._list_canvas.yview_scroll(int(delta / 10), "units")
        self._scroll_y0 = e.y

    def _nscroll_start(self, e): self._nscroll_y0 = e.y
    def _nscroll_move(self, e):
        delta = self._nscroll_y0 - e.y
        self._notice_canvas.yview_scroll(int(delta / 10), "units")
        self._nscroll_y0 = e.y

    # ── Notices ────────────────────────────────────────────────────────────────

    def _load_notices(self, from_db_only=True):
        """Load notices from local DB (fast). Optionally trigger FB fetch."""
        notices = database.get_notices(limit=20)
        self._render_notices(notices)
        if not from_db_only:
            self._fetch_notices_from_fb()

    def _render_notices(self, notices):
        for w in self._notice_frame.winfo_children():
            w.destroy()
        if not notices:
            MutedLabel(self._notice_frame,
                       text="No notices yet.\nTap ⟳ to refresh from Facebook.",
                       bg=theme.INFO_BG).pack(pady=20)
            return
        for n in notices:
            card = NoticeCard(
                self._notice_frame,
                title=n.get("title", ""),
                body=n.get("body", ""),
                posted_at=n.get("posted_at", "")
            )
            card.pack(fill="x", pady=4, padx=2)

    def _manual_refresh_notices(self):
        self._notice_status.configure(text="Fetching from Facebook…")
        self._fetch_notices_from_fb()

    def _fetch_notices_from_fb(self):
        def _ok(posts):
            self.after(0, lambda: self._notice_status.configure(
                text=f"Updated — {len(posts)} posts"))
            self.after(0, lambda: self._load_notices(from_db_only=True))

        def _err(exc):
            msg = str(exc)
            self.after(0, lambda: self._notice_status.configure(
                text=f"Fetch failed: {msg[:60]}"))

        facebook_api.refresh_notices_async(on_success=_ok, on_error=_err)

    def _schedule_notice_refresh(self):
        """Refresh notices from Facebook every 15 minutes."""
        self._fetch_notices_from_fb()
        self.after(15 * 60 * 1000, self._schedule_notice_refresh)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _go_admin(self):
        self.app.show_screen("admin_password")

    def on_show(self):
        """Called each time this screen becomes visible."""
        self._populate_list(database.search_members(""))
