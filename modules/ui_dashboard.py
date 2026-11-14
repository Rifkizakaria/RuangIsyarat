#!/usr/bin/env python
"""SABLE Editorial Monochrome Dashboard View for RuangIsyarat (PyQt6)."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

import config


class EditorialCard(QFrame):
    """SABLE 3:4 Aspect Ratio Editorial Card with hover reveal action."""

    def __init__(self, index_text: str, title_text: str, subtitle_text: str, on_click=None, parent=None):
        super().__init__(parent)
        self.on_click = on_click
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumSize(285, 380)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"""
            EditorialCard {{
                background-color: {config.BONE_COLOR};
                border: 1px solid {config.INK_COLOR};
                border-radius: 0px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(8)

        # Top-Left Index ("01", "02", "03")
        self.lbl_index = QLabel(index_text.upper())
        self.lbl_index.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.lbl_index.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 1px;
            border: none;
        """)
        layout.addWidget(self.lbl_index)

        layout.addStretch(1)

        # Center-Bottom Title & Subtitle
        self.lbl_title = QLabel(title_text.upper())
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 36px;
            font-weight: 800;
            letter-spacing: -1px;
            text-transform: uppercase;
            border: none;
        """)
        layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel(subtitle_text.upper())
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_subtitle.setWordWrap(True)
        self.lbl_subtitle.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: none;
            padding-bottom: 12px;
        """)
        layout.addWidget(self.lbl_subtitle)

        # Hover Reveal Action ("BUKA MODUL")
        self.btn_open = QPushButton("BUKA MODUL")
        self.btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_open.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.INK_COLOR};
                color: {config.BONE_COLOR};
                border: 1px solid {config.INK_COLOR};
                padding: 12px 24px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 2px;
                text-transform: uppercase;
                border-radius: 0px;
            }}
        """)
        self.btn_open.setVisible(False)
        if self.on_click:
            self.btn_open.clicked.connect(self.on_click)
        layout.addWidget(self.btn_open)

    def enterEvent(self, event):
        self.btn_open.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_open.setVisible(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.on_click:
            self.on_click()
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        # Pertahankan proporsi rasio 3:4
        w = self.width()
        target_h = int((w * 4) / 3)
        if abs(self.height() - target_h) > 40:
            self.setMinimumHeight(min(460, max(360, target_h)))
        super().resizeEvent(event)


class DashboardUI(QWidget):
    """SABLE Editorial Monochrome Dashboard View (#cats 3-column grid)."""

    def __init__(
        self,
        master=None,
        nickname: str = "PENGGUNA",
        on_kamus=None,
        on_deteksi=None,
        on_kuis=None,
        on_logout=None,
    ):
        super().__init__(master)
        self.master = master
        self.nickname = nickname
        self.on_kamus = on_kamus
        self.on_deteksi = on_deteksi
        self.on_kuis = on_kuis
        self.on_logout = on_logout

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(48, 36, 48, 48)
        main_layout.setSpacing(28)

        # Editorial Section Header
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)

        self.lbl_hero = QLabel("INDEKS MODUL UTAMA")
        self.lbl_hero.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 48px;
            font-weight: 800;
            letter-spacing: -2px;
            text-transform: uppercase;
        """)
        header_row.addWidget(self.lbl_hero)

        header_row.addStretch(1)

        self.lbl_session = QLabel(f"OPERATOR // {self.nickname.upper()}")
        self.lbl_session.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_session.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
        """)
        header_row.addWidget(self.lbl_session)

        main_layout.addLayout(header_row)

        # 3-Column Grid Layout (#cats)
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(24)
        self.grid_layout.setVerticalSpacing(24)
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setColumnStretch(2, 1)

        self.card_kamus = EditorialCard(
            index_text="01",
            title_text="KAMUS",
            subtitle_text="ARSIP VISUAL STANDAR ASL / SIBI / BISINDO",
            on_click=self._open_kamus,
            parent=self,
        )
        self.grid_layout.addWidget(self.card_kamus, 0, 0)

        self.card_deteksi = EditorialCard(
            index_text="02",
            title_text="DETEKSI",
            subtitle_text="PEMINDAIAN GESTUR TANGAN REAL-TIME AI",
            on_click=self._open_deteksi,
            parent=self,
        )
        self.grid_layout.addWidget(self.card_deteksi, 0, 1)

        self.card_kuis = EditorialCard(
            index_text="03",
            title_text="KUIS",
            subtitle_text="EVALUASI KETAHANAN GESTUR & SKOR",
            on_click=self._open_kuis,
            parent=self,
        )
        self.grid_layout.addWidget(self.card_kuis, 0, 2)

        main_layout.addLayout(self.grid_layout, 1)

    def set_nickname(self, nickname: str):
        self.nickname = nickname or "PENGGUNA"
        self.lbl_session.setText(f"OPERATOR // {self.nickname.upper()}")

    def _open_kamus(self):
        if self.on_kamus:
            self.on_kamus()

    def _open_deteksi(self):
        if self.on_deteksi:
            self.on_deteksi()

    def _open_kuis(self):
        if self.on_kuis:
            self.on_kuis()


# Alias kompatibilitas
DashboardView = DashboardUI
