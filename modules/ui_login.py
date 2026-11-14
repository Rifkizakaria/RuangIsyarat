#!/usr/bin/env python
"""SABLE Editorial Monochrome Login & Registration View for RuangIsyarat (PyQt6)."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

import config


class LoginView(QWidget):
    """SABLE Editorial Monochrome Login and Registration view widget."""

    login_requested = pyqtSignal(str, str)
    register_requested = pyqtSignal(str, str)

    def __init__(self, master=None, on_login=None, on_register=None):
        super().__init__(master)
        self.master = master
        self.on_login = on_login
        self.on_register = on_register

        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(48, 48, 48, 48)
        outer_layout.setSpacing(0)

        outer_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        # Center Box Container
        row_layout = QHBoxLayout()
        row_layout.addStretch(1)

        card = QFrame(self)
        card.setMinimumWidth(480)
        card.setMaximumWidth(540)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {config.BONE_COLOR};
                border: 1px solid {config.INK_COLOR};
                border-radius: 0px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(48, 48, 48, 48)
        card_layout.setSpacing(24)

        # Brand Tag
        lbl_brand = QLabel("SABLE // RUANG ISYARAT")
        lbl_brand.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
            border: none;
        """)
        card_layout.addWidget(lbl_brand)

        # Hero Title
        title_label = QLabel("IDENTIFIKASI\nPENGGUNA")
        title_label.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 40px;
            font-weight: 800;
            letter-spacing: -2px;
            text-transform: uppercase;
            border: none;
        """)
        card_layout.addWidget(title_label)

        # Nickname Input
        lbl_nick = QLabel("NICKNAME")
        lbl_nick.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: none;
        """)
        card_layout.addWidget(lbl_nick)

        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("MASUKKAN NICKNAME")
        card_layout.addWidget(self.nickname_input)

        # Password Input
        lbl_pwd = QLabel("PASSWORD")
        lbl_pwd.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: none;
        """)
        card_layout.addWidget(lbl_pwd)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("MASUKKAN PASSWORD")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._on_login_clicked)
        card_layout.addWidget(self.password_input)

        # Error / Notification Label (Hidden by default, thick border box when shown)
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setVisible(False)
        self.status_label.setStyleSheet(f"""
            color: {config.INK_COLOR};
            background-color: {config.BONE_COLOR};
            border: 2px solid {config.INK_COLOR};
            padding: 12px;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            border-radius: 0px;
        """)
        card_layout.addWidget(self.status_label)

        # Buttons (Full width)
        self.btn_login = QPushButton("MASUK")
        self.btn_login.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_login.clicked.connect(self._on_login_clicked)
        card_layout.addWidget(self.btn_login)

        self.btn_register = QPushButton("DAFTAR BARU")
        self.btn_register.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_register.clicked.connect(self._on_register_clicked)
        card_layout.addWidget(self.btn_register)

        row_layout.addWidget(card)
        row_layout.addStretch(1)

        outer_layout.addLayout(row_layout)

        outer_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

    def _on_login_clicked(self):
        nick = self.nickname_input.text().strip()
        pwd = self.password_input.text().strip()
        if not nick or not pwd:
            self.show_error("KOLOM TIDAK BOLEH KOSONG!")
            return
        if self.on_login:
            self.on_login(nick, pwd)

    def _on_register_clicked(self):
        nick = self.nickname_input.text().strip()
        pwd = self.password_input.text().strip()
        if not nick or not pwd:
            self.show_error("KOLOM TIDAK BOLEH KOSONG!")
            return
        if self.on_register:
            self.on_register(nick, pwd)

    def show_error(self, message: str):
        self.status_label.setText(str(message).upper())
        self.status_label.setVisible(True)

    def show_message(self, message: str):
        self.status_label.setText(str(message).upper())
        self.status_label.setVisible(True)

    def reset_fields(self):
        self.nickname_input.clear()
        self.password_input.clear()
        self.status_label.clear()
        self.status_label.setVisible(False)


LoginUI = LoginView
