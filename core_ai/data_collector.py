import os
import csv
import cv2
import mediapipe as mp

DATASET_FILE = "dataset_sibi.csv"

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def init_dataset_file(filename: str) -> None:
    if not os.path.exists(filename):
        headers = ["label"]
        for i in range(21):
            headers.extend([f"x_{i}", f"y_{i}", f"z_{i}"])
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def extract_normalized_landmarks(hand_landmarks) -> list:
    base_x = hand_landmarks.landmark[0].x
    base_y = hand_landmarks.landmark[0].y
    base_z = hand_landmarks.landmark[0].z

    features = []
    for lm in hand_landmarks.landmark:
        features.extend([
            round(lm.x - base_x, 6),
            round(lm.y - base_y, 6),
            round(lm.z - base_z, 6),
        ])
    return features


def main():
    init_dataset_file(DATASET_FILE)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("⚠️ Gagal membuka webcam. Pastikan kamera terhubung dan izin akses diberikan.")
        return

    print("=" * 60)
    print("TOOL PEREKAM DATASET SIBI (STAND-ALONE CLI)")
    print("Petunjuk:")
    print("- Arahkan tangan ke depan kamera.")
    print("- Tekan tombol huruf A-Z pada keyboard untuk merekam titik landmark.")
    print("- Tekan 'ESC' atau 'q' untuk menghentikan program.")
    print(f"- Data tersimpan di: {DATASET_FILE}")
    print("=" * 60)

    last_recorded_status = "Siap merekam..."

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    ) as hands:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("⚠️ Tidak dapat membaca frame dari webcam.")
                break

            # Mirroring frame agar natural
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # Konversi BGR ke RGB untuk MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            results = hands.process(rgb_frame)
            rgb_frame.flags.writeable = True

            hand_detected = False
            current_landmarks = None

            if results.multi_hand_landmarks:
                hand_detected = True
                current_landmarks = results.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(
                    frame,
                    current_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )

            # Overlay Status di Layar OpenCV
            status_color = (0, 255, 0) if hand_detected else (0, 0, 255)
            status_text = "Tangan Terdeteksi: YA" if hand_detected else "Tangan Terdeteksi: TIDAK"
            cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            cv2.putText(frame, "Tekan A-Z untuk rekam | ESC / q untuk keluar", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"Status: {last_recorded_status}", (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow("RuangIsyarat - Perekam Dataset SIBI", frame)

            key = cv2.waitKey(1) & 0xFF

            if key in (27, ord('q'), ord('Q')):
                print("\nMenutup perekam dataset...")
                break

            # Jika menekan karakter A-Z atau a-z
            if (ord('a') <= key <= ord('z')) or (ord('A') <= key <= ord('Z')):
                char_label = chr(key).upper()
                if hand_detected and current_landmarks is not None:
                    row_data = [char_label] + extract_normalized_landmarks(current_landmarks)
                    with open(DATASET_FILE, mode="a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(row_data)

                    last_recorded_status = f"✅ Berhasil rekam sampel '{char_label}'"
                    print(f"[REKAM] Huruf: '{char_label}' | 21 Landmark (63 fitur) berhasil disimpan ke {DATASET_FILE}")
                else:
                    last_recorded_status = f"⚠️ Gagal rekam '{char_label}': Tangan belum terdeteksi!"
                    print(f"[GAGAL] Huruf: '{char_label}' diabaikan karena tangan tidak terdeteksi.")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

