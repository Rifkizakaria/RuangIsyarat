# Spec-Driven Development (SDD) - RuangIsyarat

## 1. Arsitektur Teknologi (Tech Stack)

* **Bahasa Utama:** Python 3.9+
* **GUI Framework:** `customtkinter` (membungkus Tkinter bawaan Python untuk tampilan modern dan dukungan tema).
* **Computer Vision:** `opencv-python` (`cv2`).
* **AI Hand Tracking:** `mediapipe` (menyediakan 21 titik koordinat X,Y,Z dari setiap sendi tangan).
* **Machine Learning (Klasifikasi):** `scikit-learn` (menggunakan algoritma *Random Forest Classifier* atau *SVC*, disimpan/dibaca menggunakan modul `pickle` bawaan Python).
* **Data Handling:** `json` (untuk *users*), `csv`, `pandas` / `numpy` (untuk pemrosesan titik koordinat).

## 2. Struktur Direktori Proyek

AI Agent harus membuat dan mengikuti struktur ini dengan ketat:

```text
RuangIsyarat/
│
├── main.py                     # Entry point, Controller untuk routing UI
├── config.py                   # Konstanta UI (Warna A11y, Ukuran Font, Padding)
│
├── data/
│   └── users.json              # File database login (auto-generate list kosong jika tidak ada)
│
├── modules/
│   ├── __init__.py
│   ├── auth.py                 # Class/Fungsi login & register (mengolah users.json)
│   ├── ui_dashboard.py         # View untuk Dashboard utama
│   ├── ui_kamus.py             # View untuk Kamus
│   └── ui_kuis.py              # View & Logika Mode Kuis
│
├── core_ai/
│   ├── __init__.py
│   ├── vision_thread.py        # PENTING: Class Threading untuk OpenCV + MediaPipe
│   └── data_collector.py       # Skrip CLI stand-alone untuk rekam CSV dataset
│
├── models/                     # Tempat menyimpan file `.pkl`
│   ├── model_asl.pkl
│   └── model_sibi.pkl          # (Kosong awalnya, dihasilkan dari data_collector.py)
│
└── assets/                     # Folder gambar untuk Kamus (e.g., sibi_a.png)
```

## 3. Skema Data

### 3.1. Akun Pengguna (`users.json`)
Struktur data Array of Objects sederhana:
```json
[
  {
    "nickname": "budi123",
    "password": "hashed_or_plain_password"
  }
]
```

### 3.2. Ekstraksi Fitur MediaPipe (Input Model)
Untuk setiap *frame* tangan yang terdeteksi, `mediapipe` menghasilkan 21 *Landmarks*.
Karena jarak ke kamera bisa berubah-ubah, sebelum data dimasukkan ke model prediksi, koordinat harus di-**normalisasi** (dihitung jarak relatifnya terhadap pangkal telapak tangan / titik ke-0).

## 4. Mekanisme Multithreading (Penanganan Lag UI)

Ini adalah aturan krusial untuk AI Agent. OpenCV dan CustomTkinter **TIDAK BOLEH** berjalan di satu *thread* yang sama (akan menyebabkan `Not Responding`).

**Pola Implementasi Wajib:**
1. Gunakan kelas turunan dari `threading.Thread`.
2. *Thread* ini memiliki *loop* `while is_running:` yang melakukan `cv2.VideoCapture.read()`.
3. Di dalam *loop* ini, jalankan proses MediaPipe dan prediksi dengan `scikit-learn`.
4. Konversi hasil *frame* OpenCV (BGR) menjadi format gambar yang dikenali CustomTkinter (PIL Image / `CTkImage`).
5. Kirim gambar dan teks hasil prediksi ke antarmuka menggunakan mekanisme *event* bawaan Tkinter (seperti `after()`) atau simpan ke variabel instance yang secara konstan dibaca oleh UI melalui metode `after()` setiap 30ms.
6. Saat pengguna menekan "Kembali" untuk keluar dari halaman Deteksi, pastikan *flag* `is_running` diatur ke `False`, jalankan `cap.release()`, dan matikan *thread* dengan `thread.join()`.