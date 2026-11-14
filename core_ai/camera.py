#!/usr/bin/env python
"""Camera & Real-Time MediaPipe Inference Thread for RuangIsyarat (PyQt6)."""

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from core_ai.model_store import ModelStore

try:
    import mediapipe as mp
    MP_AVAILABLE = True
    _mp_hands = mp.solutions.hands
    _mp_drawing = mp.solutions.drawing_utils
except ImportError:
    MP_AVAILABLE = False
    _mp_hands = None
    _mp_drawing = None


class CameraThread(QThread):
    """Camera capture and inference thread running independently of the GUI main loop."""

    # Signals
    prediction_ready = pyqtSignal(object, str, float)
    frame_ready = pyqtSignal(np.ndarray)
    error_message = pyqtSignal(str)

    def __init__(self, camera_index: int = 0, std_standar: str = "ASL"):
        super().__init__()
        self.camera_index = camera_index
        self.std_standar = std_standar
        self._running = False
        self._cap = None
        self.latest_frame = None

        self._model = None
        self._label_encoder = None
        self._gesture_buffer = []
        self._buffer_size = 10
        self._load_model()

    def _load_model(self):
        """Load the trained model for the selected standard."""
        self._model, self._label_encoder = ModelStore.get_model(self.std_standar)

    def set_standard(self, std_standar: str):
        """Switch sign language standard dynamically."""
        self.std_standar = std_standar.upper()
        self._gesture_buffer.clear()
        self._load_model()

    def _smooth_gesture(self):
        """Smooth gesture prediction using majority vote in buffer."""
        if not self._gesture_buffer:
            return "-", 0.0

        label_counts = {}
        for lbl, _ in self._gesture_buffer:
            label_counts[lbl] = label_counts.get(lbl, 0) + 1

        most_common_label = max(label_counts, key=label_counts.get)
        most_common_count = label_counts[most_common_label]
        label_confs = [
            conf for lbl, conf in self._gesture_buffer if lbl == most_common_label
        ]
        avg_conf = sum(label_confs) / len(label_confs) if label_confs else 0.0

        if most_common_count >= 3:
            return most_common_label, float(avg_conf)

        last_label, last_conf = self._gesture_buffer[-1]
        return last_label, float(last_conf)

    def run(self):
        """Main thread loop - captures frames, extracts MediaPipe landmarks, and runs model.predict()."""
        hands = None
        try:
            self._running = True
            self._cap = cv2.VideoCapture(self.camera_index)

            if not self._cap.isOpened():
                self.error_message.emit("Kamera tidak terdeteksi")
                return

            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            if MP_AVAILABLE and _mp_hands is not None:
                hands = _mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5,
                )

            landmark_spec = (
                _mp_drawing.DrawingSpec(color=(239, 237, 232), thickness=1, circle_radius=2)
                if _mp_drawing is not None
                else None
            )
            connection_spec = (
                _mp_drawing.DrawingSpec(color=(16, 16, 16), thickness=1, circle_radius=1)
                if _mp_drawing is not None
                else None
            )

            while self._running:
                success, raw_bgr = self._cap.read()
                if not success:
                    self.error_message.emit("Gagal membaca frame dari kamera")
                    break

                # Mirror horizontal agar natural seperti cermin
                flipped_bgr = cv2.flip(raw_bgr, 1)
                self.latest_frame = flipped_bgr.copy()

                # Konversi BGR ke RGB murni
                frame = cv2.cvtColor(flipped_bgr, cv2.COLOR_BGR2RGB)

                label = "-"
                confidence = 0.0

                if hands is not None:
                    frame.flags.writeable = False
                    results = hands.process(frame)
                    frame.flags.writeable = True

                    if results.multi_hand_landmarks:
                        hand_landmarks = results.multi_hand_landmarks[0]

                        if _mp_drawing is not None:
                            _mp_drawing.draw_landmarks(
                                frame,
                                hand_landmarks,
                                _mp_hands.HAND_CONNECTIONS,
                                landmark_spec,
                                connection_spec,
                            )

                        # Ekstraksi 21 titik koordinat (63 fitur: x, y, z)
                        landmarks = []
                        for lm in hand_landmarks.landmark:
                            landmarks.extend([lm.x, lm.y, lm.z])

                        # Normalisasi koordinat relatif terhadap pangkal telapak tangan (landmark 0)
                        base_x = landmarks[0]
                        base_y = landmarks[1]
                        base_z = landmarks[2]

                        normalized = []
                        for i in range(0, 63, 3):
                            normalized.extend([
                                round(landmarks[i] - base_x, 6),
                                round(landmarks[i + 1] - base_y, 6),
                                round(landmarks[i + 2] - base_z, 6),
                            ])

                        if self._model is not None:
                            prediction = self._model.predict([normalized])[0]
                            probabilities = self._model.predict_proba([normalized])[0]
                            raw_conf = float(max(probabilities))

                            raw_label = str(prediction)
                            if self._label_encoder is not None:
                                try:
                                    raw_label = str(
                                        self._label_encoder.inverse_transform([prediction])[0]
                                    )
                                except Exception:
                                    pass

                            self._gesture_buffer.append((raw_label, raw_conf))
                            if len(self._gesture_buffer) > self._buffer_size:
                                self._gesture_buffer.pop(0)

                            label, confidence = self._smooth_gesture()
                    else:
                        self._gesture_buffer.clear()

                self.frame_ready.emit(flipped_bgr)
                self.prediction_ready.emit(frame, label, confidence)

                self.msleep(33)

        except Exception as e:
            self.error_message.emit(f"Terjadi kesalahan kamera: {str(e)}")
        finally:
            if hands is not None:
                try:
                    hands.close()
                except Exception:
                    pass
            if self._cap is not None:
                self._cap.release()
                self._cap = None

    def stop(self):
        """Stop the camera thread gracefully."""
        self._running = False
        self.wait(3000)
