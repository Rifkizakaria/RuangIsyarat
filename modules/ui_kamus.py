#!/usr/bin/env python
"""SABLE Editorial Monochrome Kamus View for RuangIsyarat (PyQt6)."""

import string
from pathlib import Path
import cv2
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QComboBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QImage, QPixmap

import config


class LetterCard(QFrame):
    """Kartu huruf SABLE (#shop style) berisi QLabel gambar di atas dan teks huruf di bawah."""

    def __init__(self, letter: str, standard: str = "ASL", parent=None):
        super().__init__(parent)
        self.letter = letter.upper()
        self.standard = standard.upper()

        self.setMinimumSize(180, 230)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            LetterCard {{
                background-color: {config.BONE_COLOR};
                border: 1px solid {config.INK_COLOR};
                border-radius: 0px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Bagian Atas: QLabel Gambar Placeholder
        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setMinimumHeight(170)
        self.lbl_image.setStyleSheet(f"""
            background-color: transparent;
            color: {config.INK_COLOR};
            border: none;
            border-bottom: 1px solid {config.INK_COLOR};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            border-radius: 0px;
        """)
        layout.addWidget(self.lbl_image, 1)

        # Bagian Bawah: Teks Huruf
        self.lbl_letter = QLabel(f"HURUF // {self.letter}")
        self.lbl_letter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_letter.setFixedHeight(52)
        self.lbl_letter.setStyleSheet(f"""
            background-color: transparent;
            color: {config.INK_COLOR};
            border: none;
            font-size: 16px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            border-radius: 0px;
        """)
        layout.addWidget(self.lbl_letter)

        self.update_standard(self.standard)

    def update_standard(self, standard: str):
        self.standard = standard.upper()
        # CATATAN ARSITEKTUR SABLE:
        # Saat aset gambar asli per huruf dimasukkan nanti, gambar WAJIB diproses
        # menggunakan OpenCV:
        #   gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        #   sable_img = cv2.convertScaleAbs(gray, alpha=1.06, beta=0)
        # sebelum dikonversi menjadi QPixmap agar 100% monokrom ber-kontras tinggi.
        self.lbl_image.setText(f"[{self.standard} // {self.letter}]\nGRAYSCALE ASSET")
        self.lbl_letter.setText(f"{self.letter}")


class KamusUI(QWidget):
    """SABLE Editorial Monochrome Kamus View dengan 4-kolom QGridLayout (#shop)."""

    STANDARDS = ["ASL", "SIBI", "BISINDO"]

    def __init__(self, master=None, on_back=None):
        super().__init__(master)
        self.master = master
        self.on_back = on_back
        self.cards = []

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(48, 36, 48, 48)
        main_layout.setSpacing(24)

        # --- Header Filter Bar ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        lbl_filter = QLabel("STANDAR ISYARAT:")
        lbl_filter.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
        """)
        header_layout.addWidget(lbl_filter)

        # Flat QComboBox dengan border-bottom 1px solid #101010
        self.combo_standar = QComboBox()
        self.combo_standar.addItems(self.STANDARDS)
        self.combo_standar.setMinimumWidth(180)
        self.combo_standar.setStyleSheet(f"""
            QComboBox {{
                background-color: transparent;
                color: {config.INK_COLOR};
                border: none;
                border-bottom: 1px solid {config.INK_COLOR};
                padding: 8px 4px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
                border-radius: 0px;
            }}
            QComboBox::drop-down {{
                border: none;
                background: transparent;
            }}
            QComboBox QAbstractItemView {{
                background-color: {config.BONE_COLOR};
                color: {config.INK_COLOR};
                border: 1px solid {config.INK_COLOR};
                selection-background-color: {config.INK_COLOR};
                selection-color: {config.BONE_COLOR};
                border-radius: 0px;
            }}
        """)
        self.combo_standar.currentTextChanged.connect(self._on_standard_changed)
        header_layout.addWidget(self.combo_standar)

        header_layout.addStretch(1)

        if self.on_back is not None:
            self.btn_back = QPushButton("KEMBALI")
            self.btn_back.clicked.connect(self._on_back_click)
            header_layout.addWidget(self.btn_back)

        main_layout.addLayout(header_layout)

        # --- Scroll Area untuk 4-Kolom Grid (#shop) ---
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {config.BONE_COLOR};
                border: none;
                border-radius: 0px;
            }}
        """)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet(f"background-color: {config.BONE_COLOR};")

        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.setVerticalSpacing(20)

        for col in range(4):
            self.grid_layout.setColumnStretch(col, 1)

        # Buat 26 Placeholder Kartu Huruf (A-Z) dalam 4 Kolom
        # CATATAN: Gambar referensi setiap huruf akan diproses dengan cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # dan cv2.convertScaleAbs(gray, alpha=1.06, beta=0) saat data aset asli dimasukkan nanti.
        for idx, letter in enumerate(string.ascii_uppercase):
            row = idx // 4
            col = idx % 4
            card = LetterCard(letter=letter, standard="ASL", parent=self.grid_container)
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)

        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area, 1)

    def _on_standard_changed(self, choice: str):
        std = (choice or "ASL").strip().upper()
        for card in self.cards:
            card.update_standard(std)

    def _on_back_click(self):
        if self.on_back:
            self.on_back()


# Alias kompatibilitas
KamusView = KamusUI
