import random
import string
import customtkinter as ctk
from PIL import Image
from config import (
    COLOR_BG_CARD,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_ACCENT,
    COLOR_BTN_SECONDARY,
    COLOR_BTN_SECONDARY_HOVER,
    COLOR_BTN_TEXT,
    COLOR_STATUS_SUCCESS,
    COLOR_STATUS_ERROR,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADING,
    FONT_BODY,
    FONT_BUTTON,
    CORNER_RADIUS,
)
from core_ai.vision_thread import CameraVisionThread


class KuisView(ctk.CTkFrame):
    CONSECUTIVE_REQUIRED = 20

    def __init__(self, master, on_back):
        super().__init__(master, fg_color="transparent")
        self.on_back = on_back
        self.after_id = None

        # State Evaluasi & Gamifikasi
        self.skor = 0
        self.target_huruf = random.choice(string.ascii_uppercase)
        self.consecutive_match = 0
        self.feedback_timer = 0

        self._build_ui()
        self._start_camera_thread()

    def _build_ui(self):
        # Header Navigasi & Papan Skor
        nav_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS)
        nav_frame.pack(fill="x", padx=30, pady=(20, 15))

        btn_stop = ctk.CTkButton(
            nav_frame,
            text="← Berhenti & Kembali",
            font=FONT_BUTTON,
            fg_color=COLOR_BTN_SECONDARY,
            hover_color=COLOR_BTN_SECONDARY_HOVER,
            text_color=COLOR_BTN_TEXT,
            width=200,
            height=44,
            corner_radius=CORNER_RADIUS,
            command=self.stop_and_exit,
        )
        btn_stop.pack(side="left", padx=20, pady=15)

        lbl_title = ctk.CTkLabel(
            nav_frame,
            text="Mode Kuis Isyarat",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_ACCENT,
        )
        lbl_title.pack(side="left", padx=20, pady=15)

        self.lbl_score = ctk.CTkLabel(
            nav_frame,
            text=f"Skor: {self.skor}",
            font=("Helvetica", 24, "bold"),
            text_color=COLOR_STATUS_SUCCESS,
        )
        self.lbl_score.pack(side="right", padx=25, pady=15)

        # Main Viewport Container
        content_container = ctk.CTkFrame(self, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Kotak Kamera
        self.camera_card = ctk.CTkFrame(
            content_container,
            fg_color=COLOR_BG_CARD,
            corner_radius=CORNER_RADIUS,
        )
        self.camera_card.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.lbl_camera = ctk.CTkLabel(
            self.camera_card,
            text="Menghubungkan ke kamera...",
            font=FONT_HEADING,
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.lbl_camera.pack(expand=True, fill="both", padx=15, pady=15)

        # Panel Instruksi & Evaluasi Samping
        self.eval_card = ctk.CTkFrame(
            content_container,
            fg_color=COLOR_BG_CARD,
            corner_radius=CORNER_RADIUS,
            width=300,
        )
        self.eval_card.pack(side="right", fill="both", padx=(0, 0))

        lbl_instruksi_header = ctk.CTkLabel(
            self.eval_card,
            text="Tantangan Isyarat:",
            font=FONT_HEADING,
            text_color=COLOR_TEXT_SECONDARY,
        )
        lbl_instruksi_header.pack(pady=(25, 5), padx=20)

        # Label Huruf Instruksi Raksasa
        self.lbl_target = ctk.CTkLabel(
            self.eval_card,
            text=f"Peragakan:\n[ {self.target_huruf} ]",
            font=("Helvetica", 32, "bold"),
            text_color=COLOR_TEXT_ACCENT,
        )
        self.lbl_target.pack(pady=10, padx=20)

        # Indikator Ketahanan Gestur
        self.lbl_streak = ctk.CTkLabel(
            self.eval_card,
            text="Tahan posisi: 0 / 20 frame",
            font=FONT_BODY,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_streak.pack(pady=10, padx=20)

        self.progress_bar = ctk.CTkProgressBar(
            self.eval_card,
            width=220,
            height=16,
            corner_radius=8,
            progress_color=COLOR_STATUS_SUCCESS,
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(pady=5, padx=20)

        # Label Notifikasi Evaluasi (BENAR!)
        self.lbl_feedback = ctk.CTkLabel(
            self.eval_card,
            text="",
            font=("Helvetica", 22, "bold"),
            text_color=COLOR_STATUS_SUCCESS,
        )
        self.lbl_feedback.pack(pady=20, padx=20)

        self.lbl_error_status = ctk.CTkLabel(
            self.eval_card,
            text="",
            font=FONT_BODY,
            text_color=COLOR_STATUS_ERROR,
            wraplength=260,
        )
        self.lbl_error_status.pack(side="bottom", pady=20, padx=15)

    def _start_camera_thread(self):
        self.vision_thread = CameraVisionThread(camera_index=0)
        self.vision_thread.start()
        self._update_quiz_loop()

    def _update_quiz_loop(self):
        if not self.vision_thread.frame_queue.empty():
            try:
                pil_img, prediction_text, error_msg = self.vision_thread.frame_queue.get_nowait()
                if error_msg:
                    self.lbl_camera.configure(text=error_msg, image="")
                    self.lbl_error_status.configure(text=error_msg)
                elif pil_img:
                    ctk_img = ctk.CTkImage(
                        light_image=pil_img,
                        dark_image=pil_img,
                        size=(560, 420),
                    )
                    self.lbl_camera.configure(image=ctk_img, text="")
                    self.lbl_camera.image = ctk_img
                    self.lbl_error_status.configure(text="")

                    # Logika Evaluasi Kesesuaian Gestur
                    self._evaluate_prediction(prediction_text)
            except Exception:
                pass

        # Pembersihan pesan feedback "BENAR!" setelah beberapa tick
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0:
                self.lbl_feedback.configure(text="")

        self.after_id = self.after(25, self._update_quiz_loop)

    def _evaluate_prediction(self, prediction_text: str):
        if not prediction_text:
            return

        # Normalisasi pengecekan huruf target terhadap keluaran model
        predicted_char = prediction_text.replace("Huruf", "").strip().upper()

        if predicted_char == self.target_huruf:
            self.consecutive_match += 1
        else:
            self.consecutive_match = max(0, self.consecutive_match - 1)

        # Update HUD progress bar & status ketahanan
        progress_val = min(1.0, self.consecutive_match / self.CONSECUTIVE_REQUIRED)
        self.progress_bar.set(progress_val)
        self.lbl_streak.configure(text=f"Tahan posisi: {self.consecutive_match} / {self.CONSECUTIVE_REQUIRED} frame")

        # Kondisi Menang / Validasi Berhasil
        if self.consecutive_match >= self.CONSECUTIVE_REQUIRED:
            self.skor += 10
            self.lbl_score.configure(text=f"Skor: {self.skor}")
            self.lbl_feedback.configure(
                text="✅ BENAR! (+10)",
                text_color=COLOR_STATUS_SUCCESS,
            )
            self.feedback_timer = 40  # Tampilkan pesan sekitar 1 detik

            # Ganti Target Huruf Acak Baru
            available_letters = [c for c in string.ascii_uppercase if c != self.target_huruf]
            self.target_huruf = random.choice(available_letters)
            self.lbl_target.configure(text=f"Peragakan:\n[ {self.target_huruf} ]")
            self.consecutive_match = 0
            self.progress_bar.set(0.0)

    def stop_and_exit(self):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

        if hasattr(self, "vision_thread") and self.vision_thread.is_alive():
            self.vision_thread.stop()
            self.vision_thread.join(timeout=1.0)

        self.on_back()

