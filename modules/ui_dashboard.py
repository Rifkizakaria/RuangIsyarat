import customtkinter as ctk
from config import (
    COLOR_BG_CARD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_ACCENT,
    COLOR_BTN_PRIMARY,
    COLOR_BTN_PRIMARY_HOVER,
    COLOR_BTN_SECONDARY,
    COLOR_BTN_SECONDARY_HOVER,
    COLOR_BTN_ACCENT,
    COLOR_BTN_ACCENT_HOVER,
    COLOR_BTN_TEXT,
    FONT_TITLE,
    FONT_BODY,
    FONT_BUTTON,
    CORNER_RADIUS,
)


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, nickname: str, on_kamus, on_deteksi, on_kuis, on_logout):
        super().__init__(master, fg_color="transparent")
        self.nickname = nickname
        self.on_kamus = on_kamus
        self.on_deteksi = on_deteksi
        self.on_kuis = on_kuis
        self.on_logout = on_logout

        self._build_ui()

    def _build_ui(self):
        # Header Bar
        header_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS)
        header_frame.pack(fill="x", padx=30, pady=(20, 15))

        lbl_welcome = ctk.CTkLabel(
            header_frame,
            text=f"Selamat Datang, {self.nickname}!",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_ACCENT,
            anchor="w",
        )
        lbl_welcome.pack(side="left", padx=25, pady=20)

        btn_logout = ctk.CTkButton(
            header_frame,
            text="Logout",
            font=FONT_BUTTON,
            fg_color=COLOR_BTN_SECONDARY,
            hover_color=COLOR_BTN_SECONDARY_HOVER,
            text_color=COLOR_BTN_TEXT,
            width=120,
            height=44,
            corner_radius=CORNER_RADIUS,
            command=self.on_logout,
        )
        btn_logout.pack(side="right", padx=25, pady=20)

        # Deskripsi Singkat
        lbl_desc = ctk.CTkLabel(
            self,
            text="Pusat navigasi RuangIsyarat. Pilih salah satu modul di bawah ini untuk belajar,\nmemindai gerakan isyarat melalui kamera, atau menguji pemahaman Anda.",
            font=FONT_BODY,
            text_color=COLOR_TEXT_SECONDARY,
            justify="center",
        )
        lbl_desc.pack(pady=(5, 25))

        # Grid Tombol Modul Raksasa
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=30, pady=10)

        menu_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="group1")
        menu_frame.grid_rowconfigure(0, weight=1)

        # Tombol 1: Kamus
        btn_kamus = ctk.CTkButton(
            menu_frame,
            text="📖\n\nKamus Isyarat\n(Edukasi)",
            font=FONT_BUTTON,
            fg_color=COLOR_BTN_PRIMARY,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            text_color=COLOR_BTN_TEXT,
            corner_radius=CORNER_RADIUS,
            command=self.on_kamus,
        )
        btn_kamus.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Tombol 2: Deteksi AI
        btn_deteksi = ctk.CTkButton(
            menu_frame,
            text="📷\n\nMulai Deteksi\n(Kamera Real-Time)",
            font=FONT_BUTTON,
            fg_color=COLOR_BTN_ACCENT,
            hover_color=COLOR_BTN_ACCENT_HOVER,
            text_color=COLOR_BTN_TEXT,
            corner_radius=CORNER_RADIUS,
            command=self.on_deteksi,
        )
        btn_deteksi.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # Tombol 3: Mode Kuis
        btn_kuis = ctk.CTkButton(
            menu_frame,
            text="🎯\n\nMode Kuis\n(Evaluasi Gestur)",
            font=FONT_BUTTON,
            fg_color=COLOR_BTN_PRIMARY,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            text_color=COLOR_BTN_TEXT,
            corner_radius=CORNER_RADIUS,
            command=self.on_kuis,
        )
        btn_kuis.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")

