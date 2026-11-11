import customtkinter as ctk
from config import (
    COLOR_BG_CARD,
    COLOR_BG_INPUT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_ACCENT,
    COLOR_BTN_SECONDARY,
    COLOR_BTN_SECONDARY_HOVER,
    COLOR_BTN_TEXT,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADING,
    FONT_BODY,
    FONT_BUTTON,
    CORNER_RADIUS,
)


class KamusView(ctk.CTkFrame):
    STANDARDS = ["SIBI", "BISINDO", "ASL"]

    def __init__(self, master, on_back):
        super().__init__(master, fg_color="transparent")
        self.on_back = on_back

        self._build_ui()

    def _build_ui(self):
        # Top Bar Navigasi
        nav_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS)
        nav_frame.pack(fill="x", padx=30, pady=(20, 15))

        btn_back = ctk.CTkButton(
            nav_frame,
            text="← Kembali ke Dashboard",
            font=FONT_BUTTON,
            fg_color=COLOR_BTN_SECONDARY,
            hover_color=COLOR_BTN_SECONDARY_HOVER,
            text_color=COLOR_BTN_TEXT,
            width=200,
            height=44,
            corner_radius=CORNER_RADIUS,
            command=self.on_back,
        )
        btn_back.pack(side="left", padx=20, pady=15)

        lbl_title = ctk.CTkLabel(
            nav_frame,
            text="Kamus Bahasa Isyarat",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_ACCENT,
        )
        lbl_title.pack(side="left", padx=20, pady=15)

        # Kontrol Pilihan Standar
        control_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS)
        control_frame.pack(fill="x", padx=30, pady=(0, 15))

        lbl_select = ctk.CTkLabel(
            control_frame,
            text="Pilih Standar Isyarat:",
            font=FONT_HEADING,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_select.pack(side="left", padx=(25, 15), pady=18)

        self.combo_standar = ctk.CTkComboBox(
            control_frame,
            values=self.STANDARDS,
            font=FONT_BODY,
            dropdown_font=FONT_BODY,
            fg_color=COLOR_BG_INPUT,
            button_color=COLOR_BTN_SECONDARY,
            button_hover_color=COLOR_BTN_SECONDARY_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            width=200,
            height=40,
            command=self._on_standard_changed,
        )
        self.combo_standar.set("SIBI")
        self.combo_standar.pack(side="left", padx=10, pady=18)

        # Kotak Tampilan Aset Referensi (Placeholder Jujur R-38)
        self.display_box = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_CARD,
            corner_radius=CORNER_RADIUS,
            border_width=2,
            border_color="#374151",
        )
        self.display_box.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        self.lbl_asset_placeholder = ctk.CTkLabel(
            self.display_box,
            text=f"ASSET GAMBAR {self.combo_standar.get()} - TBD",
            font=("Helvetica", 24, "bold"),
            text_color=COLOR_TEXT_ACCENT,
        )
        self.lbl_asset_placeholder.pack(expand=True, pady=30)

        lbl_note = ctk.CTkLabel(
            self.display_box,
            text="Katalog kartu gestur visual dan ilustrasi abjad sedang disiapkan pada direktori assets/.",
            font=FONT_BODY,
            text_color=COLOR_TEXT_SECONDARY,
        )
        lbl_note.pack(side="bottom", pady=(0, 30))

    def _on_standard_changed(self, choice: str):
        self.lbl_asset_placeholder.configure(
            text=f"ASSET GAMBAR {choice} - TBD"
        )

