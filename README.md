# RuangIsyarat — SABLE Editorial Edition

Aplikasi desktop edukasi dan deteksi bahasa isyarat (*ASL*, *SIBI*, *BISINDO*) secara *real-time* menggunakan *Computer Vision* dan *Machine Learning*. Dibangun di atas **PyQt6** dengan estetika **SABLE Editorial** (palet *Bone* `#EFEDE8` & *Ink* `#101010`, sudut tajam `0px`, sistem *grid* presisi, tipografi *hero* masif, dan *feed* kamera berwarna *real-time*).

---

## Fitur Utama

| Modul | Kelas Utama | Deskripsi Teknis |
| :--- | :--- | :--- |
| **Autentikasi Pengguna** | `LoginView` (`modules/ui_login.py`) | Login & registrasi lokal berbasis `data/users.json` dengan *hashing* kata sandi `SHA-256`. |
| **Indeks Modul (Dashboard)** | `DashboardUI` (`modules/ui_dashboard.py`) | Tata letak `QGridLayout` 3 kolom dengan kartu editorial rasio `3:4` (`01 KAMUS`, `02 DETEKSI`, `03 KUIS`) dan aksi *hover* `BUKA MODUL`. |
| **Kamus Isyarat** | `KamusUI` (`modules/ui_kamus.py`) | Katalog abjad `A–Z` dalam `QGridLayout` 4 kolom dengan *selector* standar *flat* (`ASL`, `SIBI`, `BISINDO`). |
| **Deteksi AI Real-Time** | `DeteksiUI` (`modules/ui_deteksi.py`) | Tata letak 2 kolom asimetris: panel kiri menampilkan *Hero Text* (`120px`) & *confidence bar* datar; panel kanan merender *feed* video kamera berwarna (`RGB888`). |
| **Mode Kuis Evaluasi** | `KuisUI` (`modules/ui_kuis.py`) | Gamifikasi terpusat dengan tipografi instruksi `100px` (`PERAGAKAN: [ X ]`), *progress bar* tipis `2px` untuk tahan pose `2.0` detik (`confidence >= 0.7`), dan umpan balik `BERHASIL (+10)`. |
| **Thread Kamera & AI** | `CameraThread` (`core_ai/camera.py`) | Pemrosesan kamera `OpenCV` + ekstraksi 21 titik *landmark* `MediaPipe Hands` (63 fitur ternormalisasi) + inferensi `scikit-learn` di dalam `QThread` terpisah via sinyal `prediction_ready(object, str, float)`. |

---

## Teknologi & Arsitektur

- **Bahasa Pemrograman:** Python 3.12+
- **GUI Framework:** `PyQt6` (`QMainWindow`, `QStackedWidget`, `QThread`, `pyqtSignal`, Global `QSS`)
- **Desain Sistem:** **SABLE Editorial** (`BONE_COLOR = "#EFEDE8"`, `INK_COLOR = "#101010"`, `0px` *border-radius*, `1px solid #101010`)
- **Computer Vision:** `OpenCV` (`opencv-python`) & `MediaPipe Hands` (21 titik koordinat 3D $x, y, z$)
- **Machine Learning:** `scikit-learn` (`RandomForestClassifier`, disimpan & dimuat melalui `ModelStore` / `pickle`)
- **Penyimpanan Data:** `JSON` (`data/users.json`), `CSV` (`dataset/asl_landmarks.csv`), `PKL` (`models/model_asl.pkl`)

---

## Struktur Direktori

```text
RuangIsyarat/
├── main.py                     # Entry point utama (QMainWindow, Sticky Header, QStackedWidget)
├── config.py                   # Global Design Tokens (BONE_COLOR, INK_COLOR, SABLE_STYLESHEET)
├── requirements.txt            # Daftar dependensi paket Python
├── design.md                   # Spesifikasi UI/UX & arsitektur SABLE Editorial
├── prd_ruangisyarat.md         # Product Requirements Document
├── sdd_ruangisyarat.md         # Spec-Driven Development Document
├── aturan_anti_slop.md         # Standar kualitas rekayasa kode
│
├── data/
│   └── users.json              # Database kredensial pengguna lokal (SHA-256)
│
├── dataset/
│   └── asl_landmarks.csv       # Dataset 63 fitur landmark hasil ekstraksi
│
├── models/
│   └── model_asl.pkl           # Model RandomForest terlatih
│
├── assets/                     # Aset referensi visual kamus (ASL, SIBI, BISINDO)
│
├── modules/
│   ├── __init__.py
│   ├── auth.py                 # Logika autentikasi & manajemen users.json
│   ├── ui_login.py             # Antarmuka Login & Registrasi
│   ├── ui_dashboard.py         # Antarmuka Dashboard (3 kartu rasio 3:4)
│   ├── ui_kamus.py             # Antarmuka Kamus (Grid 4 kolom A-Z)
│   ├── ui_deteksi.py           # Antarmuka Deteksi AI Real-Time (Kamera Berwarna)
│   └── ui_kuis.py              # Antarmuka Kuis Evaluasi Gestur (Kamera Berwarna)
│
├── core_ai/
│   ├── __init__.py
│   ├── camera.py               # QThread kamera + MediaPipe + prediksi ML (prediction_ready)
│   ├── model_store.py          # Singleton cache & lazy-loader model .pkl
│   ├── pipeline.py             # Utilitas pipeline inferensi & smoothing gestur
│   └── data_collector.py       # Tool CLI mandiri perekam dataset CSV via webcam
│
└── scripts/
    ├── download_dataset.py     # Skrip pengunduh dataset ASL
    ├── extract_landmarks.py    # Ekstraksi paralel landmark gambar ke CSV (63 fitur)
    └── train_model.py          # Pelatihan RandomForestClassifier ke models/model_asl.pkl
```

---

## Panduan Instalasi & Menjalankan Aplikasi

### 1. Persiapan Virtual Environment
```powershell
cd D:\python\RuangIsyarat
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instalasi Dependensi
```powershell
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi Utama
```powershell
python main.py
```

---

## Pipeline Pelatihan Model & Perekaman Data

### A. Melatih Model dari Dataset Gambar ASL
Jika ingin membangun ulang model `models/model_asl.pkl`:
```powershell
# 1. Unduh dataset gambar ASL
python scripts\download_dataset.py

# 2. Ekstrak 21 titik koordinat tangan (63 fitur ternormalisasi) ke CSV
python scripts\extract_landmarks.py

# 3. Latih model RandomForest dan simpan ke models/model_asl.pkl
python scripts\train_model.py
```

### B. Merekam Dataset Baru melalui Webcam (Developer Tool)
```powershell
python core_ai\data_collector.py
```
- Arahkan tangan ke webcam, lalu tekan tombol huruf **`A–Z`** pada keyboard untuk menyimpan koordinat *landmark* ke `dataset_sibi.csv`.
- Tekan **`ESC`** atau **`Q`** untuk keluar.
