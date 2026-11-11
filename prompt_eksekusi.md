# Daftar Prompt Vibe Coding - RuangIsyarat

*Kirimkan prompt ini secara bertahap kepada AI setelah memberikan file PRD, SDD, dan antislop.md.*

### Fase 1: Konfigurasi & Login (Sistem Dasar)
> Baca kembali aturan ketat di `antislop.md`. Kita mulai mengerjakan aplikasi 'RuangIsyarat' dengan Python dan CustomTkinter. 
> Untuk Fase 1, buatkan 3 file berikut:
> 1. `config.py`: Isinya definisi variabel/konstanta untuk warna kontras tinggi (Background Gelap, Teks Terang) dan font ukuran besar. Ini wajib untuk aturan aksesibilitas (R-25).
> 2. `modules/auth.py`: Modul untuk menangani Register dan Login. Data harus disimpan dan dibaca dari file lokal `data/users.json`. Validasi agar nickname tidak boleh duplikat saat register.
> 3. `main.py`: File utama yang menjalankan `customtkinter.CTk()`. Saat pertama kali jalan, tampilkan Halaman Login/Register (gunakan tema dari `config.py`). Jika login berhasil, hancurkan (*destroy*) frame login tersebut dan tampilkan sebuah teks raksasa "HALAMAN DASHBOARD" sebagai *placeholder* (R-38) untuk pengerjaan Fase 2.
>
> Patuhi C-2: Jangan membuat tombol tanpa fungsi (*command* nyata).

### Fase 2: Dashboard & Navigasi Utama
> Lanjut ke Fase 2. Jangan ada basa-basi di balasanmu, langsung ke kode! 
> 1. Buat `modules/ui_dashboard.py`: Rancang UI yang memiliki teks "Selamat Datang, [Nickname]" dan 3 tombol raksasa (Kamus, Deteksi, Kuis) beserta tombol Logout. (Ingat aturan C-2).
> 2. Buat `modules/ui_kamus.py`: Rancang halaman Kamus. Harus ada *Combobox* (Pilihan: ASL, SIBI, BISINDO). Jika diganti, sebuah frame kotak besar di bawahnya akan mengganti label teks (misal: "ASSET GAMBAR SIBI - TBD") (Aturan Placeholder Jujur R-38). Sediakan tombol 'Kembali' untuk merouting ulang ke Dashboard.
> 3. Perbarui `main.py` agar mengimpor UI Dashboard dan UI Kamus. Buat logika *routing* antar halamannya berjalan mulus (Login -> Dashboard -> Kamus -> Dashboard). 

### Fase 3: Tool Perekam Dataset
> Lanjut Fase 3. Buat alat khusus Developer untuk merekam koordinat tangan, bukan bagian dari aplikasi utama CustomTkinter. 
> Buat file mandiri `core_ai/data_collector.py`. Logika skrip ini:
> 1. Membuka `cv2.VideoCapture(0)`.
> 2. Menggunakan `mediapipe.solutions.hands` untuk menggambar kerangka tangan di layar OpenCV.
> 3. Menunggu input tombol keyboard (`cv2.waitKey()`). Jika saya menekan huruf (A-Z) dan tangan terdeteksi dengan jelas, ekstrak 21 pasang koordinat (x,y,z), lalu simpan ke dalam file `dataset_sibi.csv` dengan huruf tersebut sebagai target/label di kolom pertama.
> 4. `print()` pesan konfirmasi di terminal setiap kali satu baris data direkam.
>
> Tidak perlu UI CustomTkinter di sini. Hanya kode OpenCV dan MediaPipe murni!

### Fase 4: Core AI & Threading Kamera (Kritis!)
> Masuk Fase 4 (Sangat Kritis!). UI tidak boleh macet saat kamera menyala. Patuhi aturan C-4.
> 1. Buat `core_ai/vision_thread.py`: Buat sebuah Class/Fungsi yang membungkus OpenCV dan MediaPipe di dalam **Threading** (wajib `threading.Thread` atau `queue.Queue`). Thread ini membaca kamera secara terus-menerus, mengekstrak kordinat, lalu melempar gambar (*frame*) dan prediksi teksnya (untuk sekarang pakai dummy string "Huruf X") ke *Queue*.
> 2. Buat `modules/ui_deteksi.py`: Rancang halaman CustomTkinter. Gunakan `.after()` loop untuk menarik frame dari *Queue* dan menampilkannya sebagai gambar di dalam sebuah `CTkLabel`. Tampilkan prediksi teks di label raksasa di bawahnya. 
> 3. Harus ada tombol 'Berhenti/Kembali' yang merouting ke Dashboard, merilis `cv2.VideoCapture`, dan membunuh Thread secara aman agar memori tidak bocor.
> 4. Perbarui routing di `main.py` untuk membuka halaman ini.

### Fase 5: Mode Kuis (Evaluasi)
> Ini Fase terakhir (Fase 5). Jangan basa-basi.
> 1. Buat `modules/ui_kuis.py`: UI ini mirip dengan Deteksi (impor thread kamera dari `core_ai/vision_thread.py`).
> 2. Tambahkan variabel game: `Skor` (dimulai dari 0) dan Instruksi ("Peragakan: [Huruf Acak]").
> 3. Logika: Di dalam loop `.after()`, cocokkan huruf acak dengan output prediksi dari Thread kamera. Jika cocok selama 20 *frame* berturut-turut (sekitar 2 detik), tambahkan skor +10, tampilkan notifikasi "BENAR!", dan ganti huruf acak ke huruf baru.
> 4. Perbarui `main.py` untuk mengintegrasikan fitur Kuis ini. Pastikan *error handling* kameranya sempurna (R-27). 
> 
> Lakukan inspeksi mandiri (Delivery Gate) sebelum memberikan kodenya.