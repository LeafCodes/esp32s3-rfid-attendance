# Setup Guide — RFID Attendance System

## Untuk Pengguna (Non-Teknis)

### Persiapan Hardware
1. ESP32-S3 board
2. MFRC522 RFID reader module
3. RFID cards/tags (MIFARE Classic 1K)
4. I2C LCD 16x2
5. Buzzer + 2x LED (hijau, merah) + resistor 220Ω
6. Kabel jumper
7. Power supply 5V USB

### Langkah Penggunaan

#### 1. Colok Power
- Hubungkan ESP32-S3 ke power via kabel USB atau adapter 5V
- LCD akan menyala dan menampilkan "RFID Attendance System"

#### 2. Setup WiFi
- Cari jaringan WiFi "Absensi-XXXX" di HP/laptop Anda
- Connect ke jaringan tersebut (password: tidak ada)
- Setelah connect, akan muncul halaman login otomatis
- Pilih WiFi kantor Anda dan masukkan password
- ESP32 akan connect ke WiFi kantor

#### 3. Jalankan Aplikasi PC
- Buka terminal/command prompt di PC
- Jalankan: `cd pc-app && uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Buka browser: http://absensi-pc.local:8000 atau http://localhost:8000

#### 4. Tambah Kartu RFID
- Di halaman web, klik "Kelola Kartu"
- Tempelkan kartu RFID ke reader
- Masukkan UID yang muncul di Serial Monitor
- Isi nama karyawan
- Klik "Tambah Kartu"

#### 5. Absensi
- Karyawan cukup menempelkan kartu ke reader
- LCD akan menampilkan nama dan status (MASUK/KELUAR)
- Data otomatis terkirim ke PC

#### 6. Export Excel
- Klik tombol "Export Excel" di halaman Dashboard
- File akan terdownload dalam format .xlsx

### Troubleshooting

| Masalah | Solusi |
|---------|--------|
| LCD blank | Cek kabel I2C, coba address 0x3F |
| Kartu tidak terbaca | Pastikan jarak <5cm, cek kabel SPI |
| ESP32 tidak connect WiFi | Reset alat, akan muncul portal lagi |
| Data tidak sampai ke PC | Cek apakah PC app berjalan |
| WiFi error | Alat auto-buka portal, config ulang |
