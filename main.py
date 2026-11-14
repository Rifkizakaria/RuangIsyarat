#!/usr/bin/env python
"""RuangIsyarat - Main Application Entry Point (PyQt6 SABLE Editorial Edition)."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).parent))

import config
from modules.auth import login_user, register_user, _ensure_data_file
from modules.ui_login import LoginView
from modules.ui_dashboard import DashboardUI
from modules.ui_deteksi import DeteksiUI
from modules.ui_kamus import KamusView
from modules.ui_kuis import KuisView


SESSION_STATE = {
    "username": None,
}


class RuangIsyaratApp(QMainWindow):
    """Main application window implementing SABLE Editorial Monochrome UI & QStackedWidget routing."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SABLE / RUANG ISYARAT")
        self.setMinimumSize(1024, 680)
        self.resize(1280, 720)

        self.active_user = None

        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(config.SABLE_STYLESHEET)
        self.setStyleSheet(config.SABLE_STYLESHEET)

        self._build_layout()
        self.show_login_view()

    def _build_layout(self):
        central_container = QWidget(self)
        self.setCentralWidget(central_container)

        root_layout = QVBoxLayout(central_container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Sticky Header Navigation ---
        self.header_frame = QFrame(central_container)
        self.header_frame.setFixedHeight(72)
        self.header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {config.BONE_COLOR};
                border: none;
                border-bottom: 1px solid {config.INK_COLOR};
                border-radius: 0px;
            }}
        """)

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(48, 0, 48, 0)
        header_layout.setSpacing(16)

        self.lbl_brand = QLabel("SABLE / RUANG ISYARAT")
        self.lbl_brand.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: none;
        """)
        header_layout.addWidget(self.lbl_brand)

        header_layout.addStretch(1)

        nav_btn_style = f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {config.INK_COLOR};
                color: {config.INK_COLOR};
                padding: 10px 20px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: {config.INK_COLOR};
                color: {config.BONE_COLOR};
            }}
        """

        self.btn_nav_dashboard = QPushButton("INDEKS")
        self.btn_nav_dashboard.setStyleSheet(nav_btn_style)
        self.btn_nav_dashboard.clicked.connect(lambda: self.show_dashboard_view(self.active_user))
        header_layout.addWidget(self.btn_nav_dashboard)

        self.btn_nav_kamus = QPushButton("KAMUS")
        self.btn_nav_kamus.setStyleSheet(nav_btn_style)
        self.btn_nav_kamus.clicked.connect(self.show_kamus_view)
        header_layout.addWidget(self.btn_nav_kamus)

        self.btn_nav_deteksi = QPushButton("DETEKSI")
        self.btn_nav_deteksi.setStyleSheet(nav_btn_style)
        self.btn_nav_deteksi.clicked.connect(self.show_deteksi_view)
        header_layout.addWidget(self.btn_nav_deteksi)

        self.btn_nav_kuis = QPushButton("KUIS")
        self.btn_nav_kuis.setStyleSheet(nav_btn_style)
        self.btn_nav_kuis.clicked.connect(self.show_kuis_view)
        header_layout.addWidget(self.btn_nav_kuis)

        self.btn_nav_logout = QPushButton("LOGOUT")
        self.btn_nav_logout.setStyleSheet(nav_btn_style)
        self.btn_nav_logout.clicked.connect(self.handle_logout)
        header_layout.addWidget(self.btn_nav_logout)

        root_layout.addWidget(self.header_frame)

        # --- Stacked Widget for Page Routing ---
        self.stacked_widget = QStackedWidget(central_container)
        root_layout.addWidget(self.stacked_widget, 1)

        # Instantiate Pages
        self.login_page = LoginView(
            master=self,
            on_login=self.handle_login,
            on_register=self.handle_register,
        )
        self.dashboard_page = DashboardUI(
            master=self,
            nickname="PENGGUNA",
            on_kamus=self.show_kamus_view,
            on_deteksi=self.show_deteksi_view,
            on_kuis=self.show_kuis_view,
            on_logout=self.handle_logout,
        )
        self.deteksi_page = DeteksiUI(
            master=self,
            on_back=lambda: self.show_dashboard_view(self.active_user),
        )
        self.kamus_page = KamusView(
            master=self,
            on_back=lambda: self.show_dashboard_view(self.active_user),
        )
        self.kuis_page = KuisView(
            master=self,
            on_back=lambda: self.show_dashboard_view(self.active_user),
        )

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.deteksi_page)
        self.stacked_widget.addWidget(self.kamus_page)
        self.stacked_widget.addWidget(self.kuis_page)

        self.stacked_widget.currentChanged.connect(self._on_page_changed)

    def _stop_active_streams(self):
        if hasattr(self.deteksi_page, "stop_detection"):
            self.deteksi_page.stop_detection()
        if hasattr(self.kuis_page, "_stop_camera"):
            self.kuis_page._stop_camera()

    def _on_page_changed(self, index: int):
        current_widget = self.stacked_widget.widget(index)
        is_login = current_widget == self.login_page
        self.header_frame.setVisible(not is_login)

    def show_login_view(self):
        self._stop_active_streams()
        if hasattr(self.login_page, "reset_fields"):
            self.login_page.reset_fields()
        self.stacked_widget.setCurrentWidget(self.login_page)
        self.header_frame.setVisible(False)

    def show_dashboard_view(self, nickname: str = None):
        self._stop_active_streams()
        user = nickname or self.active_user or "PENGGUNA"
        self.dashboard_page.set_nickname(user)
        self.stacked_widget.setCurrentWidget(self.dashboard_page)
        self.header_frame.setVisible(True)

    def show_deteksi_view(self):
        if hasattr(self.kuis_page, "_stop_camera"):
            self.kuis_page._stop_camera()
        self.stacked_widget.setCurrentWidget(self.deteksi_page)
        self.header_frame.setVisible(True)

    def show_kamus_view(self):
        self._stop_active_streams()
        self.stacked_widget.setCurrentWidget(self.kamus_page)
        self.header_frame.setVisible(True)

    def show_kuis_view(self):
        if hasattr(self.deteksi_page, "stop_detection"):
            self.deteksi_page.stop_detection()
        self.stacked_widget.setCurrentWidget(self.kuis_page)
        self.header_frame.setVisible(True)

    def handle_login(self, nick: str, pwd: str):
        success, msg = login_user(nick, pwd)
        if success:
            self.active_user = nick.strip()
            SESSION_STATE["username"] = self.active_user
            self.show_dashboard_view(self.active_user)
        else:
            self.login_page.show_error(msg)

    def handle_register(self, nick: str, pwd: str):
        success, msg = register_user(nick, pwd)
        if success:
            self.login_page.show_message(msg)
        else:
            self.login_page.show_error(msg)

    def handle_logout(self):
        self._stop_active_streams()
        self.active_user = None
        SESSION_STATE["username"] = None
        self.show_login_view()

    def closeEvent(self, event):
        self._stop_active_streams()
        super().closeEvent(event)


def main():
    _ensure_data_file()
    app = QApplication(sys.argv)

    font = QFont("Archivo", 12)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    app.setStyleSheet(config.SABLE_STYLESHEET)

    window = RuangIsyaratApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
