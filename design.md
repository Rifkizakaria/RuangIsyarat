# RUANGISYARAT: SABLE EDITORIAL EDITION
## UI/UX & Architecture Specification Document (design.md)

### 1. PROJECT OVERVIEW
- **App Name:** RuangIsyarat
- **Stack:** Python 3.12, PyQt6, OpenCV, MediaPipe, scikit-learn.
- **Design Philosophy:** Minimalist, high-end editorial fashion e-commerce (SABLE-inspired). 
- **Core Aesthetic:** Monochrome, rigid grid systems, sharp edges (0px border-radius), high-contrast grayscale imagery, typography-driven layouts.

### 2. GLOBAL DESIGN TOKENS (QSS)
Gunakan variabel berikut sebagai dasar global `QSS` (Qt Style Sheets) di `main.py`. Dilarang menggunakan *inline styling* kecuali untuk animasi dinamis.

- **Colors:**
  - `--bone`: `#EFEDE8` (Global Background)
  - `--ink`: `#101010` (Text, Borders, Accents)
- **Typography:**
  - Font Family: `Archivo`, `Segoe UI`, `system-ui`.
  - Anti-aliasing wajib diaktifkan.
  - Heading 1 (Hero Title): `48px`, `font-weight: 800`, `letter-spacing: -2px`, `uppercase`.
  - Body: `16px`, `font-weight: 400`, `line-height: 1.5`.
- **UI Elements (Strict Rules):**
  - **Buttons:** `background: transparent; border: 1px solid #101010; color: #101010; padding: 16px 32px; font-weight: 600; text-transform: uppercase; border-radius: 0px;`
  - **Button Hover:** `background: #101010; color: #EFEDE8;`
  - **Inputs (QLineEdit):** `background: transparent; border: none; border-bottom: 2px solid #101010; padding: 12px 0px; font-size: 18px; border-radius: 0px;`
  - **Input Focus:** `border-bottom: 3px solid #101010;`
  - **Borders:** Semua frame pemisah harus setipis `1px solid #101010`.

### 3. ARCHITECTURE & ROUTING
- **Window:** Fixed size `1280x720` atau `fullscreen`, tanpa *native window frame* bawaan OS (FramelessWindowHint opsional jika custom title bar diimplementasi).
- **Routing:** Gunakan `QStackedWidget` di `main.py` untuk mengontrol pergantian halaman tanpa membuka jendela baru.
- **State Management:** Simpan session state (username) di *singleton class* atau dictionary global yang dapat diakses semua modul UI.

### 4. VIEW SPECIFICATIONS

#### 4.1. Header / Navigation (Sticky Top)
- **Layout:** Flex row (QHBoxLayout). Kiri: "SABLE / RUANG ISYARAT" (Logo teks). Kanan: Navigasi modul (Kamus, Deteksi, Kuis) dan tombol Logout.
- **Behavior:** Sembunyikan elemen navigasi saat di halaman Login.

#### 4.2. View: Login (`modules/ui_login.py`)
- **Layout:** Sentralisasi konten di tengah layar (VBox & HBox margin dinamis).
- **Komponen:**
  - Title: "IDENTIFIKASI PENGGUNA"
  - Input: `QLineEdit` untuk Nickname dan Password (mengikuti QSS Global).
  - Error Label: Tersembunyi secara default, warna teks `--ink` namun dengan background kotak peringatan bergaris tebal jika muncul.
  - Submit Button: "MASUK" (Full width dari container input).

#### 4.3. View: Dashboard (`modules/ui_dashboard.py`)
- **Grid System:** Gunakan `QGridLayout` meniru *section #cats* (3 Kolom desktop).
- **Card Design:**
  - Aspek rasio 3:4.
  - Border: `1px solid #101010`.
  - Elemen dalam Card: Nomor indeks ("01") di pojok kiri atas. Judul ("KAMUS") di tengah-bawah, sub-teks di bawah judul.
  - Hover Effect: Teks "BUKA MODUL" muncul dari bawah (translasi Y / `.setVisible(True)`).

#### 4.4. View: Kamus (`modules/ui_kamus.py`)
- **Grid System:** 4-Kolom grid meniru *section #shop*.
- **Image Constraint:** Semua *placeholder* gambar atau foto isyarat wajib diproses melalui OpenCV/Pixmap menjadi `grayscale` dengan *contrast boost* `1.06`. Tidak boleh ada gambar berwarna.
- **Interaksi:** Filter bahasa (Dropdown/ComboBox berdesain flat border-bottom) di kiri atas grid.

#### 4.5. View: Deteksi AI Real-Time (`modules/ui_deteksi.py`)
- **Split Layout:** 2-Kolom asimetris (Kiri: Metadata, Kanan: Video Feed), meniru *section #cloth*.
- **Left Panel (Metadata):** 
  - Huruf terdeteksi ditampilkan dengan ukuran masif (Hero Text, misal `font-size: 120px`).
  - Progress bar *confidence level* menggunakan garis `1px solid #101010` yang terisi dengan balok `#101010`.
- **Right Panel (Video Feed):**
  - **CRITICAL CV2 RULE:** Pisahkan *inference frame* dan *display frame*. 
  - AI (`pipeline.py`) membaca *frame* RGB normal. 
  - UI menampilkan `display_frame` yang telah diubah: `cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)`, ditambah *contrast alpha=1.06*, lalu dikonversi kembali ke format QPixmap BGR/RGB untuk QT.
  - Landmark MediaPipe digambar menggunakan garis tipis (`thickness=1`) berwarna *hitam* (`#101010`) atau *putih* (`#EFEDE8`), DILARANG menggunakan warna merah/hijau bawaan MediaPipe.

#### 4.6. View: Kuis (`modules/ui_kuis.py`)
- **Layout:** Elemen berpusat di tengah layar. Instruksi tipografi besar: "PERAGAKAN: [HURUF]".
- **Timer/Progress:** Progress bar tipis di bawah instruksi. Jika kondisi terpenuhi (confidence > 0.7 & huruf benar), balok indikator bergerak mengisi bar (membutuhkan 2 detik).
- **Feedback:** "BERHASIL" muncul secara absolut di atas video feed (seperti notifikasi "Added to Bag" di SABLE, durasi 1300ms).

### 5. THREADING & PERFORMANCE (ANTI-LAG)
- Kamera dan Inference MediaPipe **WAJIB** berjalan di `QThread` terpisah (`core_ai/camera.py`).
- Gunakan `pyqtSignal(np.ndarray, str, float)` untuk mengirim *frame* yang sudah difilter SABLE-style, label kelas, dan skor confidence dari `QThread` ke Main GUI Thread.
- UI diperbarui melalui *slot* yang terhubung ke sinyal QThread, bukan di-loop menggunakan `time.sleep()`.

### 6. DIRECTIVES UNTUK ANTIGRAVITY AI
1. Jangan membuat file terpisah untuk hal yang bisa digabungkan, kecuali arsitektur memintanya.
2. Outputkan kode Python yang *ready-to-run* dan bersih dari sisa-sisa komentar tutorial.
3. Fokus pada penulisan struktur kelas PyQt6 yang rapi dan mematuhi QSS yang ditetapkan di config.
4. Jangan menambahkan komponen *rounded* (radius). Setia pada estetika editorial yang bersudut tajam.