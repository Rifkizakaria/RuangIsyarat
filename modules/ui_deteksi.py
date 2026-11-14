#!/usr/bin/env python
"""SABLE Editorial Monochrome Real-Time AI Detection View for RuangIsyarat (PyQt6)."""

import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QComboBox, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QImage, QPixmap

import config
from core_ai.camera import CameraThread
from core_ai.model_store import ModelStore


class DeteksiUI(QWidget):
    """Asymmetric 2-column SABLE Editorial real-time detection view (#cloth layout)."""

    def __init__(self, master=None, on_back=None):
        super().__init__(master)
        self.master = master
        self.on_back = on_back

        self.camera_thread = None
        self.running = False

        ModelStore().init()
        self._build_ui()

    def _build_ui(self):
        # Asymmetric Split Layout (#cloth: Left Metadata, Right Video Feed)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(48, 36, 48, 48)
        main_layout.setSpacing(32)

        # --- LEFT COLUMN: METADATA & HERO TYPOGRAPHY ---
        self.left_panel = QFrame(self)
        self.left_panel.setMinimumWidth(360)
        self.left_panel.setMaximumWidth(440)
        self.left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {config.BONE_COLOR};
                border: 1px solid {config.INK_COLOR};
                border-radius: 0px;
            }}
        """)

        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(32, 32, 32, 32)
        left_layout.setSpacing(18)

        # Index & Header Tag
        lbl_section = QLabel("02 // PEMINDAIAN GESTUR AI")
        lbl_section.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: none;
        """)
        left_layout.addWidget(lbl_section)

        # Standard Selector Row
        std_row = QHBoxLayout()
        std_row.setSpacing(12)

        lbl_std = QLabel("STANDAR MODEL:")
        lbl_std.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: none;
        """)
        std_row.addWidget(lbl_std)

        self.combo_standar = QComboBox()
        self.combo_standar.addItems(["ASL", "SIBI", "BISINDO"])
        self.combo_standar.currentTextChanged.connect(self._on_standard_changed)
        std_row.addWidget(self.combo_standar, 1)

        left_layout.addLayout(std_row)

        left_layout.addStretch(1)

        # Hero Caption
        lbl_hero_caption = QLabel("KLASIFIKASI HURUF")
        lbl_hero_caption.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: none;
        """)
        left_layout.addWidget(lbl_hero_caption)

        # Massive Hero Prediction Text
        self.lbl_prediction = QLabel("-")
        self.lbl_prediction.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_prediction.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 120px;
            font-weight: 800;
            letter-spacing: -2px;
            text-transform: uppercase;
            border: none;
            min-height: 140px;
        """)
        left_layout.addWidget(self.lbl_prediction)

        # Confidence Level Metadata & Flat Progress Bar
        self.lbl_confidence = QLabel("CONFIDENCE LEVEL // 0%")
        self.lbl_confidence.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: none;
        """)
        left_layout.addWidget(self.lbl_confidence)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setTextVisible(False)
        self.confidence_bar.setFixedHeight(16)
        self.confidence_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: transparent;
                border: 1px solid {config.INK_COLOR};
                border-radius: 0px;
            }}
            QProgressBar::chunk {{
                background-color: {config.INK_COLOR};
                border-radius: 0px;
            }}
        """)
        left_layout.addWidget(self.confidence_bar)

        self.lbl_status = QLabel("STATUS // SIAP")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: none;
        """)
        left_layout.addWidget(self.lbl_status)

        left_layout.addStretch(1)

        # Action Controls
        self.btn_toggle_camera = QPushButton("MULAI KAMERA")
        self.btn_toggle_camera.clicked.connect(self._toggle_camera)
        left_layout.addWidget(self.btn_toggle_camera)

        self.btn_back = QPushButton("KEMBALI KE DASHBOARD")
        self.btn_back.clicked.connect(self._handle_back)
        left_layout.addWidget(self.btn_back)

        main_layout.addWidget(self.left_panel, 2)

        # --- RIGHT COLUMN: MONOCHROME SABLE VIDEO FEED ---
        self.right_panel = QFrame(self)
        self.right_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {config.BONE_COLOR};
                border: 1px solid {config.INK_COLOR};
                border-radius: 0px;
            }}
        """)

        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.video_label = QLabel("FEED KAMERA NONAKTIF // TEKAN MULAI KAMERA")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(QSize(640, 480))
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_label.setStyleSheet(f"""
            color: {config.INK_COLOR};
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: none;
        """)
        right_layout.addWidget(self.video_label)

        main_layout.addWidget(self.right_panel, 3)

    @pyqtSlot(object, str, float)
    def update_view(self, frame_rgb, predicted_label: str, confidence_score: float):
        """
        Slot penerima sinyal dari CameraThread.
        Menerapkan filter monokrom SABLE (Grayscale + Contrast alpha=1.06, beta=0) khusus di level UI.
        """
        if frame_rgb is not None:
            try:
                if frame_rgb.ndim == 3:
                    gray_frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
                else:
                    gray_frame = frame_rgb

                sable_frame = cv2.convertScaleAbs(gray_frame, alpha=1.06, beta=0)

                height, width = sable_frame.shape
                bytes_per_line = width
                q_img = QImage(
                    sable_frame.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_Grayscale8,
                ).copy()

                pixmap = QPixmap.fromImage(q_img)
                self.video_label.setPixmap(
                    pixmap.scaled(
                        self.video_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            except Exception:
                pass

        clean_label = (predicted_label or "-").strip().upper()
        self.lbl_prediction.setText(clean_label)

        pct = max(0, min(100, int(round(float(confidence_score) * 100))))
        self.confidence_bar.setValue(pct)
        self.lbl_confidence.setText(f"CONFIDENCE LEVEL // {pct}%")

    def _on_standard_changed(self, std_name: str):
        if self.camera_thread is not None:
            self.camera_thread.set_standard(std_name)
        self.lbl_status.setText(f"STATUS // STANDAR {std_name.upper()} AKTIF")

    def _on_camera_error(self, message: str):
        self.lbl_status.setText(f"PERINGATAN // {message.upper()}")
        self.video_label.clear()
        self.video_label.setText(f"GALAT KAMERA // {message.upper()}")
        self.running = False
        self.btn_toggle_camera.setText("MULAI KAMERA")

    def _toggle_camera(self):
        if self.running:
            self.stop_detection()
        else:
            self.start_detection()

    def start_detection(self):
        if self.running:
            return

        std_name = self.combo_standar.currentText()
        self.camera_thread = CameraThread(camera_index=0, std_standar=std_name)
        self.camera_thread.prediction_ready.connect(self.update_view)
        self.camera_thread.error_message.connect(self._on_camera_error)
        self.camera_thread.start()

        self.running = True
        self.btn_toggle_camera.setText("HENTIKAN KAMERA")
        self.lbl_status.setText(f"STATUS // MEMINDAI ({std_name.upper()})")

    def stop_detection(self):
        if self.camera_thread is not None:
            try:
                self.camera_thread.prediction_ready.disconnect(self.update_view)
            except Exception:
                pass
            self.camera_thread.stop()
            self.camera_thread = None

        self.running = False
        self.btn_toggle_camera.setText("MULAI KAMERA")
        self.video_label.clear()
        self.video_label.setText("FEED KAMERA NONAKTIF // TEKAN MULAI KAMERA")
        self.lbl_prediction.setText("-")
        self.confidence_bar.setValue(0)
        self.lbl_confidence.setText("CONFIDENCE LEVEL // 0%")
        self.lbl_status.setText("STATUS // DIHENTIKAN")

    def _handle_back(self):
        self.stop_detection()
        if self.on_back:
            self.on_back()

    def closeEvent(self, event):
        self.stop_detection()
        super().closeEvent(event)


# Alias kompatibilitas
DeteksiView = DeteksiUI
