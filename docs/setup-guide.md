# 📖 Panduan Penggunaan & Instalasi Sistem Presensi RFID

Buku panduan ini disusun untuk dua kelompok pengguna:
- 👨‍💻 **Panduan Pengembang & Teknisi (Developer Setup)**: Untuk instalasi kode sumber, *flashing* mikrokontroler, dan konfigurasi server backend.
- 🏢 **Panduan Pengguna & HR (Operational Manual)**: Untuk operasional harian, pendaftaran pegawai, proses presensi, dan rekapitulasi data ke format Excel.

---

## 📑 Daftar Isi
1. [Panduan Pengembang (Developer Setup)](#1-panduan-pengembang-developer-setup)
   - [A. Persiapan Lingkungan Pengembangan](#a-persiapan-lingkungan-pengembangan)
   - [B. Flashing Firmware ESP32-S3 (PlatformIO)](#b-flashing-firmware-esp32-s3-platformio)
   - [C. Menjalankan Server Backend (FastAPI)](#c-menjalankan-server-backend-fastapi)
2. [Panduan Pengguna & HR (Operational Manual)](#2-panduan-pengguna--hr-operational-manual)
   - [A. Menghidupkan Alat & Setup WiFi Pertama Kali](#a-menghidupkan-alat--setup-wifi-pertama-kali)
   - [B. Mendaftarkan Kartu Karyawan Baru](#b-mendaftarkan-kartu-karyawan-baru)
   - [C. Pelaksanaan Presensi Harian](#c-pelaksanaan-presensi-harian)
   - [D. Ekspor Laporan Presensi ke Excel](#d-ekspor-laporan-presensi-ke-excel)
3. [Matriks Penanganan Masalah (Troubleshooting Guide)](#3-matriks-penanganan-masalah-troubleshooting-guide)

---

## 1. Panduan Pengembang (Developer Setup)

### A. Persiapan Lingkungan Pengembangan
Pastikan komputer pengembang telah terpasang:
- **VS Code** dengan ekstensi **PlatformIO IDE** (atau PlatformIO CLI).
- **Python 3.12** atau versi yang lebih baru.
- Driver USB UART (CP210x atau CH340 sesuai chip bridge board ESP32 Anda).

### B. Flashing Firmware ESP32-S3 (PlatformIO)
1. Hubungkan board **ESP32-S3 DevKitC-1** ke komputer menggunakan kabel data USB-C.
2. Buka terminal proyek dan masuk ke direktori `firmware`:
   ```bash
   cd firmware
   ```
3. Periksa konfigurasi pin di `firmware/src/config.h` apakah sudah sesuai dengan hardware Anda.
4. Lakukan kompilasi dan unggah firmware:
   ```bash
   pio run -t upload
   ```
5. Buka Serial Monitor untuk melihat log inisialisasi:
   ```bash
   pio device monitor --baud 115200
   ```

### C. Menjalankan Server Backend (FastAPI)
1. Buka jendela terminal baru dan masuk ke direktori `pc-app`:
   ```bash
   cd pc-app
   ```
2. Buat dan aktifkan lingkungan virtual Python (*virtual environment*):
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Pasang semua dependensi pustaka:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan server backend menggunakan Uvicorn:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   > 💡 **Catatan Jaringan:** Menggunakan flag `--host 0.0.0.0` memastikan server dapat diakses oleh ESP32 dari seluruh perangkat dalam satu jaringan WiFi/LAN.

5. Pastikan layanan mDNS aktif. Komputer Anda kini dapat diakses oleh ESP32 melalui nama host: `http://absensi-pc.local:8000`.

---

## 2. Panduan Pengguna & HR (Operational Manual)

### A. Menghidupkan Alat & Setup WiFi Pertama Kali
1. Tancapkan kabel daya USB-C ke adaptor 5V (charger HP / port USB PC).
2. Layar LCD 16x2 akan menyala dan menampilkan pesan:
   ```text
   RFID Attendance
   System Ready
   ```
3. Jika alat belum pernah terhubung ke WiFi kantor:
   - Ambil ponsel pintar (HP) atau laptop Anda.
   - Buka pengaturan WiFi dan hubungkan ke hotspot bernama: **`Absensi-XXXX`** (tanpa kata sandi).
   - Halaman portal konfigurasi (*Captive Portal*) akan otomatis terbuka di browser Anda.
   - Pilih nama WiFi kantor Anda, masukkan kata sandi WiFi, lalu klik **Save / Connect**.
   - ESP32 akan restart dan otomatis terhubung ke jaringan kantor.

---

### B. Mendaftarkan Kartu Karyawan Baru
1. Buka browser di komputer kantor dan buka alamat:
   👉 **`http://absensi-pc.local:8000`** (atau `http://localhost:8000`).
2. Masuk ke menu **"Kelola Kartu"** atau klik tombol **"Tambah Kartu Baru"**.
3. Ketikkan nama karyawan (misalnya: *Budi Santoso*) dan jabatan/divisi.
4. Klik tombol **"Aktifkan Mode Tap Pendaftaran"**.
5. Minta karyawan menempelkan kartu barunya ke reader RFID di alat.
6. Layar LCD alat akan berbunyi *bip* dua kali dan menampilkan:
   ```text
   Budi Santoso
   TERDAFTAR!
   ```
7. Data kartu langsung tersimpan di sistem dan kartu tersebut siap digunakan untuk absensi harian.

---

### C. Pelaksanaan Presensi Harian
1. Karyawan cukup mendekatkan kartu RFID ke area pembaca (*reader*) dengan jarak 1–3 cm.
2. **Skenario Masuk (Clock IN)**:
   - LCD: `Budi Santoso` (Baris 1) dan `MASUK - 08:01` (Baris 2).
   - Buzzer berbunyi 1x nada pendek, LED Hijau menyala.
3. **Skenario Pulang (Clock OUT)**:
   - Saat karyawan menempelkan kartu kembali di sore hari, sistem secara otomatis mengubah status menjadi `KELUAR - 17:05`.
4. **Proteksi Double-Tap**:
   - Jika karyawan tanpa sengaja menempelkan kartu dua kali berturut-turut dalam rentang waktu < 10 detik, sistem tidak akan menggandakan catatan kehadiran.

---

### D. Ekspor Laporan Presensi ke Excel
1. Masuk ke halaman **Dashboard** di browser.
2. Tentukan rentang tanggal laporan yang diinginkan (Hari Ini, Minggu Ini, atau Bulan Ini).
3. Klik tombol hijau berlabel **"Export to Excel (.xlsx)"**.
4. Berkas spreadsheet akan otomatis terunduh berisi:
   - Nomor ID Karyawan & Nama Lengkap.
   - Jam Masuk & Jam Pulang.
   - Total Durasi Kerja (Jam).
   - Status Keterlambatan / Tepat Waktu.

---

## 3. Matriks Penanganan Masalah (Troubleshooting Guide)

| Gejala Masalah | Kemungkinan Penyebab | Solusi Perbaikan |
|---|---|---|
| **Layar LCD Blank / Tidak Ada Teks** | Kontras belum diatur atau alamat I2C tidak tepat. | 1. Putar potensiometer kecil (biru) di belakang modul I2C backpack untuk mengatur kontras.<br>2. Periksa apakah alamat I2C adalah `0x27` atau `0x3F`. |
| **Kartu RFID Tidak Merespon Sama Sekali** | Kabel SPI kendor atau tegangan kurang. | 1. Pastikan modul MFRC522 terhubung ke pin **3.3V** (bukan 5V).<br>2. Periksa urutan pin SPI (MOSI=11, MISO=13, SCK=12, SDA=10). |
| **LCD Menampilkan Pesan "Offline Mode"** | Server PC belum dinyalakan atau WiFi terputus. | 1. Pastikan server FastAPI di komputer telah berjalan (`uvicorn`).<br>2. Pastikan PC dan ESP32 berada dalam jaringan WiFi/SSID yang sama.<br>*(Tenang: Data tetap tersimpan di memori offline ESP32 dan akan tersinkronisasi otomatis saat PC hidup)*. |
| **mDNS `absensi-pc.local` Tidak Terdeteksi** | Layanan Bonjour/mDNS diblokir firewall Windows. | 1. Izinkan port 5353 (UDP) dan port 8000 pada Windows Defender Firewall.<br>2. Pastikan pustaka `python-zeroconf` terpasang di komputer server. |
| **Pendaftaran Kartu Baru Gagal** | Waktu *timeout* pendaftaran habis. | Klik kembali tombol "Aktifkan Mode Pendaftaran" di web dashboard sebelum menempelkan kartu baru. |
