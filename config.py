# Konfigurasi Tema & Aksesibilitas (A11y & SABLE Editorial Edition)

# Global Design Tokens - SABLE Editorial Monochrome
BONE_COLOR = "#EFEDE8"
INK_COLOR = "#101010"

# Konstanta Kompatibilitas Modul (Diarahkan ke Palet Monokrom SABLE)
COLOR_BG_MAIN = BONE_COLOR
COLOR_BG_CARD = BONE_COLOR
COLOR_BG_INPUT = BONE_COLOR

COLOR_TEXT_PRIMARY = INK_COLOR
COLOR_TEXT_SECONDARY = INK_COLOR
COLOR_TEXT_ACCENT = INK_COLOR

COLOR_BTN_PRIMARY = INK_COLOR
COLOR_BTN_PRIMARY_HOVER = INK_COLOR
COLOR_BTN_SECONDARY = BONE_COLOR
COLOR_BTN_SECONDARY_HOVER = INK_COLOR
COLOR_BTN_ACCENT = INK_COLOR
COLOR_BTN_ACCENT_HOVER = INK_COLOR
COLOR_BTN_TEXT = BONE_COLOR

COLOR_STATUS_SUCCESS = INK_COLOR
COLOR_STATUS_ERROR = INK_COLOR
COLOR_STATUS_INFO = INK_COLOR

# Tipografi
FONT_FAMILY = "Archivo"
FONT_TITLE = (FONT_FAMILY, 36, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 20, "bold")
FONT_HEADING = (FONT_FAMILY, 18, "bold")
FONT_BODY = (FONT_FAMILY, 16, "normal")
FONT_BUTTON = (FONT_FAMILY, 14, "bold")
FONT_INPUT = (FONT_FAMILY, 18, "normal")
FONT_STATUS = (FONT_FAMILY, 14, "bold")

# Dimensi Interaksi (Sudut Tajam 0px sesuai SABLE)
BTN_HEIGHT = 52
BTN_PAD_X = 32
BTN_PAD_Y = 16
CORNER_RADIUS = 0

# Global Qt Style Sheet (QSS) - SABLE Editorial Monochrome
SABLE_STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {BONE_COLOR};
    color: {INK_COLOR};
    font-family: "Archivo", "Segoe UI", system-ui, sans-serif;
    font-size: 16px;
    font-weight: 400;
    border-radius: 0px;
}}

QLabel {{
    background-color: transparent;
    color: {INK_COLOR};
    border: none;
    border-radius: 0px;
}}

QPushButton {{
    background-color: transparent;
    border: 1px solid {INK_COLOR};
    color: {INK_COLOR};
    padding: 16px 32px;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    border-radius: 0px;
}}

QPushButton:hover {{
    background-color: {INK_COLOR};
    color: {BONE_COLOR};
}}

QPushButton:pressed {{
    background-color: {INK_COLOR};
    color: {BONE_COLOR};
}}

QLineEdit {{
    background-color: transparent;
    color: {INK_COLOR};
    border: none;
    border-bottom: 2px solid {INK_COLOR};
    padding: 12px 0px;
    font-size: 18px;
    border-radius: 0px;
    selection-background-color: {INK_COLOR};
    selection-color: {BONE_COLOR};
}}

QLineEdit:focus {{
    border: none;
    border-bottom: 3px solid {INK_COLOR};
}}

QComboBox {{
    background-color: transparent;
    color: {INK_COLOR};
    border: none;
    border-bottom: 2px solid {INK_COLOR};
    padding: 8px 0px;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    border-radius: 0px;
}}

QComboBox::drop-down {{
    border: none;
    background: transparent;
}}

QComboBox QAbstractItemView {{
    background-color: {BONE_COLOR};
    color: {INK_COLOR};
    border: 1px solid {INK_COLOR};
    selection-background-color: {INK_COLOR};
    selection-color: {BONE_COLOR};
    border-radius: 0px;
}}

QProgressBar {{
    background-color: transparent;
    border: 1px solid {INK_COLOR};
    border-radius: 0px;
    text-align: center;
    color: {INK_COLOR};
}}

QProgressBar::chunk {{
    background-color: {INK_COLOR};
    border-radius: 0px;
}}
"""
