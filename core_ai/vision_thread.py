import threading
import queue
import time
import cv2
import mediapipe as mp
from PIL import Image

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class CameraVisionThread(threading.Thread):
    def __init__(self, camera_index: int = 0, queue_size: int = 2):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.frame_queue = queue.Queue(maxsize=queue_size)
        self._stop_event = threading.Event()
        self.cap = None
        self.error_message = None

    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                self.error_message = "Kamera tidak terdeteksi ⚠️"
                self._safe_put((None, None, self.error_message))
                return

            with mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5,
            ) as hands:
                while not self._stop_event.is_set():
                    success, frame = self.cap.read()
                    if not success:
                        time.sleep(0.01)
                        continue

                    # Mirror horizontal agar natural seperti cermin
                    frame = cv2.flip(frame, 1)

                    # Pemrosesan MediaPipe
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    rgb_frame.flags.writeable = False
                    results = hands.process(rgb_frame)
                    rgb_frame.flags.writeable = True

                    prediction_text = "Menunggu Tangan..."
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                frame,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style(),
                            )
                        # Placeholder Dummy Sesuai Spesifikasi Fase 4
                        prediction_text = "Huruf A"

                    # Konversi OpenCV BGR -> PIL Image untuk Tkinter
                    display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(display_frame)

                    self._safe_put((pil_img, prediction_text, None))
                    time.sleep(0.015)  # Batasi FPS ke ~60 fps untuk efisiensi CPU

        except Exception as e:
            self.error_message = f"Terjadi kesalahan kamera: {str(e)} ⚠️"
            self._safe_put((None, None, self.error_message))

        finally:
            if self.cap is not None:
                self.cap.release()
                self.cap = None

    def _safe_put(self, item):
        try:
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self.frame_queue.put_nowait(item)
        except queue.Full:
            pass

    def stop(self):
        self._stop_event.set()
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

