# components/widgets.py — Reusable touch-friendly widgets

import tkinter as tk

import theme


class TouchButton(tk.Button):
    """A large, touch-friendly button with hover colour transitions."""

    def __init__(
        self,
        parent,
        text,
        command=None,
        bg=None,
        fg=None,
        hover_bg=None,
        font_cfg=None,
        width=None,
        height=None,
        **kwargs,
    ):
        bg = bg or theme.BTN_BG
        fg = fg or theme.PRIMARY_TEXT
        hover_bg = hover_bg or theme.BTN_HOVER
        font_cfg = font_cfg or theme.F_BTN
        self._bg = bg
        self._hover_bg = hover_bg

        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            font=font_cfg,
            relief="flat",
            bd=0,
            cursor="hand2",
            highlightthickness=0,
            **kwargs,
        )
        if width:
            self.configure(width=width)
        if height:
            self.configure(height=height)

        self.bind("<Enter>", lambda e: self.configure(bg=self._hover_bg))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))


class SignInButton(TouchButton):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=theme.BTN_SUCCESS_BG,
            fg=theme.SECONDARY_TEXT,
            hover_bg=theme.BTN_SUCCESS_HOV,
            **kwargs,
        )


class SignOutButton(TouchButton):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=theme.BTN_DANGER_BG,
            fg=theme.SECONDARY_TEXT,
            hover_bg=theme.BTN_DANGER_HOV,
            **kwargs,
        )


class SectionLabel(tk.Label):
    """Bold section heading label."""

    def __init__(self, parent, text, bg=None, fg=None, font_cfg=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            bg=bg or theme.PAGE_BG,
            fg=fg or theme.SECONDARY_TEXT,
            font=font_cfg or theme.F_H3,
            **kwargs,
        )


class MutedLabel(tk.Label):
    def __init__(self, parent, text, bg=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            bg=bg or theme.PAGE_BG,
            fg=theme.MUTED_TEXT,
            font=theme.F_SMALL,
            **kwargs,
        )


class Divider(tk.Frame):
    def __init__(self, parent, bg=None, **kwargs):
        super().__init__(parent, height=1, bg=bg or theme.BORDER_COLOR, **kwargs)


class StyledEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, **kwargs)
        theme.style_entry(self)
        self._placeholder = placeholder
        self._has_focus = False
        if placeholder:
            self.insert(0, placeholder)
            self.configure(fg=theme.MUTED_TEXT)
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, _):
        if not self._has_focus and self.get() == self._placeholder:
            self.delete(0, tk.END)
            self.configure(fg=theme.PRIMARY_TEXT)
        self._has_focus = True

    def _on_focus_out(self, _):
        if not self.get():
            self.insert(0, self._placeholder)
            self.configure(fg=theme.MUTED_TEXT)
        self._has_focus = False

    def get_value(self):
        val = self.get()
        return "" if val == self._placeholder else val


class PopupOverlay(tk.Toplevel):
    """
    Centred modal popup.
    Usage:
        p = PopupOverlay(root, title="Error", is_error=True)
        p.set_message("Something went wrong.")
        p.add_button("OK", p.destroy)
    """

    def __init__(self, root, title="", is_error=False, width=500, height=260):
        super().__init__(root)
        self.overrideredirect(True)
        self.configure(
            bg=theme.PAGE_BG,
            highlightthickness=2,
            highlightbackground=theme.BORDER_COLOR,
        )

        # Centre on screen
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.grab_set()

        accent = theme.ERROR_BG if is_error else theme.SUCCESS_BG
        status_text = "ERROR" if is_error else "SUCCESS"

        # Accent bar
        bar = tk.Frame(self, bg=accent, height=10)
        bar.pack(fill="x")

        # Badge
        badge = tk.Label(
            self,
            text=status_text,
            bg=accent,
            fg="white",
            font=theme.F_H3,
            padx=16,
            pady=4,
        )
        badge.pack(anchor="w", padx=20, pady=(12, 0))

        # Message
        self._msg = tk.Label(
            self,
            text="",
            bg=theme.PAGE_BG,
            fg=theme.SECONDARY_TEXT,
            font=theme.F_BODY,
            wraplength=460,
            justify="left",
        )
        self._msg.pack(padx=20, pady=8, fill="x")

        Divider(self).pack(fill="x", padx=20, pady=4)

        # Button row
        self._btn_row = tk.Frame(self, bg=theme.PAGE_BG)
        self._btn_row.pack(pady=8)

    def set_message(self, msg):
        self._msg.configure(text=msg)

    def add_button(self, label, command, bg=None, fg=theme.PRIMARY_TEXT, hover_bg=None):
        btn = TouchButton(
            self._btn_row,
            text=label,
            command=command,
            bg=bg or theme.BTN_BG,
            fg=fg,
            hover_bg=hover_bg or theme.BTN_HOVER,
        )
        btn.pack(side="left", padx=6)


class SignatureCanvas(tk.Canvas):
    """A canvas that captures touch/mouse signature strokes."""

    def __init__(self, parent, width=300, height=120, bg="white", **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg,
            cursor="pencil",
            highlightthickness=2,
            highlightbackground=theme.ENT_BORDER,
            **kwargs,
        )
        self._last_x = None
        self._last_y = None
        self._strokes = []

        self.bind("<ButtonPress-1>", self._start)
        self.bind("<B1-Motion>", self._draw)
        self.bind("<ButtonRelease-1>", self._end)

        # Touch events (Raspberry Pi touchscreen)
        self.bind("<ButtonPress-4>", self._start)
        self.bind("<B4-Motion>", self._draw)
        self.bind("<ButtonRelease-4>", self._end)

    def _start(self, e):
        self._last_x, self._last_y = e.x, e.y

    def _draw(self, e):
        if self._last_x is not None:
            self.create_line(
                self._last_x,
                self._last_y,
                e.x,
                e.y,
                fill="black",
                width=2,
                smooth=True,
                capstyle="round",
            )
            self._strokes.append((self._last_x, self._last_y, e.x, e.y))
        self._last_x, self._last_y = e.x, e.y

    def _end(self, _):
        self._last_x = self._last_y = None

    def clear(self):
        self.delete("all")
        self._strokes.clear()

    def has_signature(self) -> bool:
        return len(self._strokes) > 0

    def export_bytes(self) -> bytes | None:
        """Export stroke data as compact bytes for DB storage."""
        if not self._strokes:
            return None
        return str(self._strokes).encode()


class NoticeCard(tk.Frame):
    """A single notice card for the notices panel."""

    def __init__(self, parent, title, body, posted_at="", **kwargs):
        super().__init__(parent, bg=theme.INFO_BG, padx=12, pady=10, **kwargs)
        self.configure(highlightthickness=1, highlightbackground=theme.BORDER_COLOR)

        if title:
            tk.Label(
                self,
                text=title,
                bg=theme.INFO_BG,
                fg=theme.BTN_BG,
                font=theme.F_LABEL,
                wraplength=300,
                justify="left",
                anchor="w",
            ).pack(fill="x")

        preview = body[:160] + ("…" if len(body) > 160 else "")
        tk.Label(
            self,
            text=preview,
            bg=theme.INFO_BG,
            fg=theme.SECONDARY_TEXT,
            font=theme.F_SMALL,
            wraplength=300,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        if posted_at:
            MutedLabel(self, text=posted_at, bg=theme.INFO_BG).pack(
                anchor="e", pady=(4, 0)
            )


class MemberListItem(tk.Frame):
    """Touchable row for the member search list."""

    def __init__(self, parent, member: dict, on_select, **kwargs):
        super().__init__(
            parent, bg=theme.PAGE_BG, cursor="hand2", pady=4, padx=8, **kwargs
        )

        name = f"{member['first_name']} {member['last_name']}"
        self._label = tk.Label(
            self,
            text=name,
            bg=theme.PAGE_BG,
            fg=theme.SECONDARY_TEXT,
            font=theme.F_BODY,
            anchor="w",
        )
        self._label.pack(fill="x")
        Divider(self).pack(fill="x")

        # Hover highlight
        for widget in (self, self._label):
            widget.bind("<Enter>", lambda e: self._hover(True))
            widget.bind("<Leave>", lambda e: self._hover(False))
            widget.bind("<ButtonPress-1>", lambda e, m=member: on_select(m))

    def _hover(self, active):
        col = theme.BORDER_COLOR if active else theme.PAGE_BG
        self.configure(bg=col)
        self._label.configure(bg=col)
