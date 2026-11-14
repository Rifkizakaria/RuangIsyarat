#!/usr/bin/env python
"""SABLE Editorial Monochrome Kuis View for RuangIsyarat (PyQt6)."""

import random
import string
import time
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt6.QtGui import QImage, QPixmap

import config
from core_ai.camera import CameraThread
from core_ai.model_store import ModelStore


class KuisUI(QWidget):
    """SABLE Editorial Monochrome Kuis Evaluasi View dengan elemen terpusat."""

    TRACK_WIDTH = 520

    def __init__(self, master=None, on_back=None):
        super().__init__(master)
        self.master = master
        self.on_back = on_back

        self.skor = 0
        self.target_huruf = random.choice(string.ascii_uppercase)
        self.hold_start_time = None
        self.hold_required = 2.0

        self.camera_thread = None
        self.running = False

        self.feedback_timer = QTimer(self)
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(self._hide_feedback)

        ModelStore().init()
        self._build_ui()

    def _build_ui(self):
        # Sentralisasi penuh menggunakan VBox dan HBox Spacer
        outer_vbox = QVBoxLayout(self)
        outer_vbox.setContentsMargins(48, 24, 48, 24)
        outer_vbox.setSpacing(0)

        outer_vbox.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        center_hbox = QHBoxLayout()
        center_hbox.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        # Kontainer Utama di Tengah Layar
        content_box = QWidget(self)
        content_layout = QVBoxLayout(content_box)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Metadata Skor
        self.lbl_score = QLabel(f"03 // EVALUASI KUIS — SKOR: {self.skor}")
        self.lbl_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_score.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: none;
        """)
        content_layout.addWidget(self.lbl_score, 0, Qt.AlignmentFlag.AlignHCenter)

        # Tipografi Hero: QLabel Raksasa (font-size: 100px, font-weight: 800)
        self.lbl_target = QLabel(f"PERAGAKAN: [ {self.target_huruf} ]")
        self.lbl_target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_target.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 100px;
            font-weight: 800;
            letter-spacing: -2px;
            text-transform: uppercase;
            border: none;
        """)
        content_layout.addWidget(self.lbl_target, 0, Qt.AlignmentFlag.AlignHCenter)

        # Custom SABLE Thin Progress Bar (QFrame height: 2px, border 1px solid #101010)
        self.progress_track = QFrame(content_box)
        self.progress_track.setFixedSize(self.TRACK_WIDTH, 2)
        self.progress_track.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: 1px solid {config.INK_COLOR};
                border-radius: 0px;
            }}
        """)

        self.progress_fill = QFrame(self.progress_track)
        self.progress_fill.setGeometry(0, 0, 0, 2)
        self.progress_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {config.INK_COLOR};
                border: none;
                border-radius: 0px;
            }}
        """)
        content_layout.addWidget(self.progress_track, 0, Qt.AlignmentFlag.AlignHCenter)

        # Umpan Balik: QLabel "BERHASIL (+10)" Tersembunyi Secara Default, Kotak Tegas Uppercase
        self.lbl_feedback = QLabel("BERHASIL (+10)")
        self.lbl_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_feedback.setVisible(False)
        self.lbl_feedback.setFixedWidth(self.TRACK_WIDTH)
        self.lbl_feedback.setStyleSheet(f"""
            background-color: {config.INK_COLOR};
            color: {config.BONE_COLOR};
            border: 1px solid {config.INK_COLOR};
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            border-radius: 0px;
        """)
        content_layout.addWidget(self.lbl_feedback, 0, Qt.AlignmentFlag.AlignHCenter)

        # Area Video Kamera Monokrom SABLE
        self.lbl_camera = QLabel("KAMERA NONAKTIF // TEKAN MULAI KUIS")
        self.lbl_camera.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_camera.setFixedSize(QSize(520, 320))
        self.lbl_camera.setStyleSheet(f"""
            background-color: {config.BONE_COLOR};
            color: {config.INK_COLOR};
            border: 1px solid {config.INK_COLOR};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            border-radius: 0px;
        """)
        content_layout.addWidget(self.lbl_camera, 0, Qt.AlignmentFlag.AlignHCenter)

        # Tombol Kontrol
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        self.btn_toggle_camera = QPushButton("MULAI KUIS")
        self.btn_toggle_camera.clicked.connect(self._toggle_camera)
        btn_row.addWidget(self.btn_toggle_camera)

        if self.on_back is not None:
            self.btn_back = QPushButton("KEMBALI")
            self.btn_back.clicked.connect(self._on_back)
            btn_row.addWidget(self.btn_back)

        content_layout.addLayout(btn_row)

        center_hbox.addWidget(content_box)
        center_hbox.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        outer_vbox.addLayout(center_hbox)

        outer_vbox.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

    def set_progress(self, ratio: float):
        """Update lebar background (#101010) pada QFrame tipis secara dinamis (0.0 - 1.0)."""
        clamped = max(0.0, min(1.0, float(ratio)))
        fill_width = int(self.TRACK_WIDTH * clamped)
        self.progress_fill.setGeometry(0, 0, fill_width, 2)

    @pyqtSlot(object, str, float)
    def update_view(self, frame_rgb, predicted_label: str, confidence_score: float):
        if frame_rgb is not None:
            try:
                if frame_rgb.ndim == 2:
                    rgb_frame = cv2.cvtColor(frame_rgb, cv2.COLOR_GRAY2RGB)
                else:
                    rgb_frame = np.ascontiguousarray(frame_rgb)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                q_img = QImage(
                    rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
                ).copy()
                pixmap = QPixmap.fromImage(q_img)
                self.lbl_camera.setPixmap(
                    pixmap.scaled(
                        self.lbl_camera.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            except Exception:
                pass

        self._evaluate_prediction(predicted_label, confidence_score)

    def _evaluate_prediction(self, label: str, confidence: float):
        if confidence < 0.7 or (label or "").strip().upper() != self.target_huruf:
            self.hold_start_time = None
            self.set_progress(0.0)
            return

        if self.hold_start_time is None:
            self.hold_start_time = time.monotonic()

        elapsed = time.monotonic() - self.hold_start_time
        self.set_progress(elapsed / self.hold_required)

        if elapsed >= self.hold_required:
            self.skor += 10
            self.lbl_score.setText(f"03 // EVALUASI KUIS — SKOR: {self.skor}")
            self.lbl_feedback.setText("BERHASIL (+10)")
            self.lbl_feedback.setVisible(True)
            self.feedback_timer.start(1300)

            available = [c for c in string.ascii_uppercase if c != self.target_huruf]
            self.target_huruf = random.choice(available)
            self.lbl_target.setText(f"PERAGAKAN: [ {self.target_huruf} ]")
            self.hold_start_time = None
            self.set_progress(0.0)

    def _hide_feedback(self):
        self.lbl_feedback.setVisible(False)

    def _on_camera_error(self, message: str):
        self.lbl_camera.setText(f"GALAT KAMERA // {message.upper()}")
        self.running = False
        self.btn_toggle_camera.setText("MULAI KUIS")

    def _toggle_camera(self):
        if self.running:
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        if self.running:
            return
        self.camera_thread = CameraThread(camera_index=0, std_standar="ASL")
        self.camera_thread.prediction_ready.connect(self.update_view)
        self.camera_thread.error_message.connect(self._on_camera_error)
        self.camera_thread.start()
        self.running = True
        self.btn_toggle_camera.setText("HENTIKAN KUIS")

    def _stop_camera(self):
        if self.camera_thread is not None:
            try:
                self.camera_thread.prediction_ready.disconnect(self.update_view)
            except Exception:
                pass
            self.camera_thread.stop()
            self.camera_thread = None
        self.running = False
        self.btn_toggle_camera.setText("MULAI KUIS")
        self.lbl_camera.clear()
        self.lbl_camera.setText("KAMERA NONAKTIF // TEKAN MULAI KUIS")
        self.set_progress(0.0)
        self.hold_start_time = None

    def _on_back(self):
        self._stop_camera()
        if self.on_back:
            self.on_back()

    def closeEvent(self, event):
        self._stop_camera()
        super().closeEvent(event)


# Alias kompatibilitas
KuisView = KuisUI
