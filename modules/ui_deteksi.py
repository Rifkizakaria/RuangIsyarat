import customtkinter as ctk
from PIL import Image
from config import (
    COLOR_BG_CARD,
    COLOR_BG_INPUT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_ACCENT,
    COLOR_BTN_SECONDARY,
    COLOR_BTN_SECONDARY_HOVER,
    COLOR_BTN_TEXT,
    COLOR_STATUS_ERROR,
    FONT_TITLE,
    FONT_HEADING,
    FONT_BODY,
    FONT_BUTTON,
    CORNER_RADIUS,
)
from core_ai.vision_thread import CameraVisionThread


class DeteksiView(ctk.CTkFrame):
    STANDARDS = ["SIBI", "BISINDO", "ASL"]

    def __init__(self, master, on_back):
        super().__init__(master, fg_color="transparent")
        self.on_back = on_back
        self.after_id = None

        self._build_ui()
        self._start_camera_thread()

    def _build_ui(self):
        # Header Navigasi
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
            text="Deteksi Bahasa Isyarat AI",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_ACCENT,
        )
        lbl_title.pack(side="left", padx=20, pady=15)

        # Kontrol Standar Bahasa Isyarat
        control_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS)
        control_frame.pack(fill="x", padx=30, pady=(0, 15))

        lbl_select = ctk.CTkLabel(
            control_frame,
            text="Standar Bahasa Isyarat:",
            font=FONT_HEADING,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_select.pack(side="left", padx=(25, 15), pady=15)

        self.combo_standar = ctk.CTkComboBox(
            control_frame,
            values=self.STANDARDS,
            font=FONT_BODY,
            dropdown_font=FONT_BODY,
            fg_color=COLOR_BG_INPUT,
            button_color=COLOR_BTN_SECONDARY,
            button_hover_color=COLOR_BTN_SECONDARY_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            width=180,
            height=38,
        )
        self.combo_standar.set("SIBI")
        self.combo_standar.pack(side="left", padx=10, pady=15)

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

        # Panel Hasil Prediksi Samping/Bawah
        self.result_card = ctk.CTkFrame(
            content_container,
            fg_color=COLOR_BG_CARD,
            corner_radius=CORNER_RADIUS,
            width=280,
        )
        self.result_card.pack(side="right", fill="both", padx=(0, 0))

        lbl_pred_header = ctk.CTkLabel(
            self.result_card,
            text="Hasil Prediksi AI",
            font=FONT_HEADING,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_pred_header.pack(pady=(35, 10), padx=20)

        # Label Teks Raksasa Hasil Prediksi
        self.lbl_prediction = ctk.CTkLabel(
            self.result_card,
            text="-",
            font=("Helvetica", 54, "bold"),
            text_color=COLOR_TEXT_ACCENT,
        )
        self.lbl_prediction.pack(expand=True, padx=20)

        self.lbl_error_status = ctk.CTkLabel(
            self.result_card,
            text="",
            font=FONT_BODY,
            text_color=COLOR_STATUS_ERROR,
            wraplength=240,
        )
        self.lbl_error_status.pack(side="bottom", pady=25, padx=15)

    def _start_camera_thread(self):
        self.vision_thread = CameraVisionThread(camera_index=0)
        self.vision_thread.start()
        self._update_feed()

    def _update_feed(self):
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
                    self.lbl_camera.image = ctk_img  # Menghindari garbage collection

                    if prediction_text:
                        self.lbl_prediction.configure(text=prediction_text)
                    self.lbl_error_status.configure(text="")
            except Exception:
                pass

        self.after_id = self.after(25, self._update_feed)

    def stop_and_exit(self):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

        if hasattr(self, "vision_thread") and self.vision_thread.is_alive():
            self.vision_thread.stop()
            self.vision_thread.join(timeout=1.0)

        self.on_back()

