# Product Requirements Document (PRD) - RuangIsyarat

## 1. Visi & Informasi Produk
*   **Nama Aplikasi:** RuangIsyarat
*   **Platform:** Desktop Application (Windows, macOS, Linux)
*   **Tujuan:** Aplikasi edukasi dan deteksi bahasa isyarat *real-time* yang inklusif, ringan, dan ramah disabilitas.
*   **Target Pengguna:** Individu Tuli, penyandang disabilitas, dan masyarakat umum yang belajar bahasa isyarat.

## 2. Spesifikasi UI/UX & Aksesibilitas (A11y)
AI Agent **wajib** mematuhi aturan desain berikut di seluruh halaman:
*   **Tema (Theme):** Harus mendukung *High Contrast* (misal: Latar belakang abu-abu sangat gelap `#1E1E1E` dengan teks putih atau kuning `#FFD700`).
*   **Tipografi:** Wajib menggunakan font *Sans-Serif* (seperti Helvetica, Arial, atau Roboto). Ukuran font teks biasa minimal `14px`, judul minimal `24px`. Semua font harus tebal (*Bold* atau *Semi-Bold*).
*   **Tombol (Buttons):** Ukuran tombol harus ekstra besar (minimal *padding* `Y=15`, `X=20`). Berikan warna *hover* yang sangat kontras (misal: biru terang saat *idle*, putih saat di-*hover*).
*   **Warna Peringatan:** Hindari merah dan hijau murni. Gunakan warna pastel atau tambahkan ikon visual pendukung (contoh: ⚠️ untuk *error*, ✅ untuk sukses).

## 3. Rincian Modul & Alur Pengguna (User Flow)

### Modul 1: Autentikasi (Login & Register)
**Deskripsi:** Pintu masuk pengguna berbasis *database* JSON lokal.
*   **UI Elements:**
    *   Logo/Judul Aplikasi yang besar.
    *   Input Field: "Nickname" dan "Password" (wajib tersembunyi/ditampilkan dengan `*`).
    *   Tombol: "Masuk" dan "Daftar Baru".
    *   Label Notifikasi: Untuk menampilkan pesan *error* atau sukses.
*   **Alur (Flow) & Validasi:**
    *   *Input Kosong:* Jika pengguna klik Masuk/Daftar tapi ada kolom kosong, munculkan teks peringatan "Kolom tidak boleh kosong!".
    *   *Daftar:* Sistem mengecek apakah Nickname sudah ada di `users.json`. Jika ada, tolak dengan pesan "Nickname sudah dipakai". Jika belum, simpan data dan munculkan pesan sukses.
    *   *Masuk:* Sistem mencocokkan kredensial. Jika salah, pesan "Nickname atau password salah". Jika benar, hancurkan (*destroy*) layar *login* dan muat *Dashboard*.

### Modul 2: Dashboard (Navigasi Utama)
**Deskripsi:** Pusat kendali aplikasi.
*   **UI Elements:**
    *   Teks sapaan dinamis: "Selamat Datang, [Nickname]!".
    *   Deskripsi singkat cara pakai aplikasi (maksimal 3 baris).
    *   Panel grid berisi 3 tombol besar: "Kamus Isyarat", "Mulai Deteksi", "Mode Kuis".
    *   Tombol "Keluar" (Logout) di pojok kanan atas atau bawah.

### Modul 3: Kamus Isyarat (Edukasi)
**Deskripsi:** Menampilkan referensi gambar statis abjad/kata.
*   **UI Elements:**
    *   Tombol "Kembali" ke Dashboard.
    *   *Dropdown* / *Combobox* pilihan standar: "ASL", "SIBI", "BISINDO".
    *   Frame kanvas/gambar untuk memuat aset visual (misal `aset_sibi_a.png`).
*   **Alur (Flow):**
    *   Saat pengguna mengubah opsi di *dropdown*, gambar referensi di bawahnya otomatis berganti menyesuaikan folder/standar yang dipilih.

### Modul 4: Deteksi AI (Pemindai Kamera)
**Deskripsi:** Fitur utama berbasis *real-time computer vision*.
*   **UI Elements:**
    *   Tombol "Kembali" (PENTING: Harus mematikan kamera saat ditekan).
    *   *Dropdown* standar AI: "ASL", "SIBI", "BISINDO".
    *   Label Status: Menampilkan pesan jika kamera gagal dimuat.
    *   **Video Frame:** Kotak khusus (misal ukuran `640x480`) yang menampilkan *feed* kamera.
    *   **Teks Hasil:** Label berukuran SANGAT BESAR di bawah *video frame* yang menampilkan huruf/kata hasil deteksi (misal: "A").
*   **Alur & Validasi:**
    *   Jika laptop tidak ada kamera/sedang dipakai, jangan *crash*. Tampilkan teks: "Kamera tidak terdeteksi ⚠️".
    *   Model AI memprediksi gestur dari titik *landmark* tangan (MediaPipe).
    *   Prediksi otomatis berubah jika *dropdown* bahasa diganti (me-*load* model `.pkl` yang berbeda).

### Modul 5: Mode Kuis (Gamifikasi)
**Deskripsi:** Evaluasi dengan mendeteksi kamera.
*   **UI Elements:**
    *   Teks Instruksi besar: "Peragakan: [HURUF]" (misal HURUF diacak dari A-Z).
    *   Label Skor: "Skor: X".
    *   Video Frame (seperti Modul 4).
*   **Alur (Flow):**
    *   Sistem meminta 1 huruf secara acak.
    *   Sistem memonitor hasil deteksi AI. Jika AI menebak benar sesuai instruksi, mulai *timer* tersembunyi.
    *   Jika pengguna menahan pose tersebut **selama 2 detik tanpa putus**, tambahkan skor +10, tampilkan notifikasi "Benar!", lalu ubah instruksi ke huruf baru secara acak.

### Modul 6: Developer Tool (Data Collection)
**Deskripsi:** Modul tersembunyi (bisa berupa skrip CLI terpisah dari UI).
*   **Fungsi:** Mengaktifkan *webcam*, pengguna memperagakan gestur, menekan tombol keyboard (misal 'A'), lalu sistem menyimpan 21 titik koordinat MediaPipe ke file `dataset.csv` dengan label 'A'. (Digunakan untuk melatih model SIBI/BISINDO sendiri).