# theme.py — Colours, fonts, and style helpers for the ASA Sign-in System

# ── Colours ──────────────────────────────────────────────────────────────────

# General
PAGE_BG         = "#372976"   # Deep purple — main background
INFO_BG         = "#2a1f5e"   # Slightly darker purple — notices / info panels

# Entry fields
ENT_BG          = "#ffffff"
ENT_BORDER      = "#d1d004"

# Buttons
BTN_BG          = "#d1d004"   # Yellow
BTN_HOVER       = "#eded00"
BTN_DANGER_BG   = "#c0392b"   # Red — sign-out / destructive
BTN_DANGER_HOV  = "#e74c3c"
BTN_SUCCESS_BG  = "#27ae60"   # Green — sign-in / confirm
BTN_SUCCESS_HOV = "#2ecc71"
BTN_ORANGE_BG   = "#c98330"   # Orange — secondary actions
BTN_ORANGE_HOV  = "#c38c4a"

# Links
LINK_TEXT       = "#c98330"
LINK_HOVER      = "#c38c4a"

# Status
ERROR_BG        = "#c0392b"
ERROR_FG        = "#ffffff"
SUCCESS_BG      = "#27ae60"
SUCCESS_FG      = "#ffffff"

# Text
PRIMARY_TEXT    = "#000000"
SECONDARY_TEXT  = "#ffffff"
MUTED_TEXT      = "#b0a8d8"   # Light purple-grey for subtle labels

# Separator / border
BORDER_COLOR    = "#4a3a8a"

# ── Fonts ─────────────────────────────────────────────────────────────────────
# Montserrat is preferred; falls back to system sans-serif on Pi if not installed.

FONT_FAMILY     = "Montserrat"
FONT_FALLBACK   = "DejaVu Sans"

def font(size=14, weight="normal", family=None):
    f = family or FONT_FAMILY
    return (f, size, weight)

# Convenience presets
F_H1    = font(28, "bold")
F_H2    = font(22, "bold")
F_H3    = font(16, "bold")
F_BODY  = font(13)
F_SMALL = font(11)
F_BTN   = font(14, "bold")
F_LABEL = font(12)
F_INPUT = font(13)


# ── Widget style helpers ──────────────────────────────────────────────────────

def style_button(btn, bg=BTN_BG, fg=PRIMARY_TEXT, hover_bg=BTN_HOVER,
                 font_cfg=None, padx=20, pady=12, relief="flat", cursor="hand2"):
    """Apply consistent styling to a tk.Button and wire hover colours."""
    if font_cfg is None:
        font_cfg = F_BTN
    btn.configure(
        bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
        font=font_cfg, padx=padx, pady=pady, relief=relief,
        bd=0, cursor=cursor, highlightthickness=0
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))


def style_entry(ent, width=30):
    ent.configure(
        bg=ENT_BG, fg=PRIMARY_TEXT, font=F_INPUT,
        relief="flat", bd=0, highlightthickness=2,
        highlightbackground=ENT_BORDER, highlightcolor=BTN_BG,
        insertbackground=PRIMARY_TEXT, width=width
    )


def style_label(lbl, fg=SECONDARY_TEXT, bg=PAGE_BG, font_cfg=None):
    if font_cfg is None:
        font_cfg = F_BODY
    lbl.configure(fg=fg, bg=bg, font=font_cfg)
