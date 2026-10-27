# 🏛️ Arsitektur & Diagram Alur Sistem (Architecture & Flowchart)

Dokumen ini menguraikan secara mendalam bagaimana **ESP32-S3 RFID Attendance System** bekerja. Sistem ini menerapkan pola **Local-First Architecture** dengan pemisahan tanggung jawab (*Separation of Concerns*) yang jelas antara perangkat keras mikrokontroler (*edge device*) dan server komputer lokal (*backend server*).

---

## 📑 Daftar Isi
1. [Prinsip Desain & Arsitektur Sistem](#1-prinsip-desain--arsitektur-sistem)
2. [Diagram Interaksi Komunikasi (Sequence Diagram)](#2-diagram-interaksi-komunikasi-sequence-diagram)
   - [A. Skenario Normal (Online Tap)](#a-skenario-normal-online-tap)
   - [B. Skenario Putus Jaringan (Offline Buffering)](#b-skenario-putus-jaringan-offline-buffering)
   - [C. Skenario Pemulihan Koneksi (Auto-Sync)](#c-skenario-pemulihan-koneksi-auto-sync)
   - [D. Skenario Pendaftaran Kartu Baru (Enrollment Mode)](#d-skenario-pendaftaran-kartu-baru-enrollment-mode)
3. [Flowchart Logika Firmware (ESP32-S3)](#3-flowchart-logika-firmware-esp32-s3)
4. [Flowchart Logika Server Backend (FastAPI)](#4-flowchart-logika-server-backend-fastapi)
5. [Spesifikasi Kontrak REST API](#5-spesifikasi-kontrak-rest-api)

---

## 1. Prinsip Desain & Arsitektur Sistem

Sistem ini dirancang untuk mengatasi kelemahan mendasar dari sistem presensi IoT konvensional yang sering lumpuh saat koneksi jaringan terputus.

| Aspek Desain | Pendekatan Sistem Ini | Manfaat Rekayasa |
|---|---|---|
| **Ketergantungan Jaringan** | *Local-First with Offline Fallback* | Karyawan tetap bisa melakukan tap kartu meskipun PC server atau router WiFi mati. |
| **Pencarian Alamat Server** | *Zero-Config Discovery* via mDNS | ESP32 mendeteksi IP server secara dinamis melalui nama host `absensi-pc.local`, tanpa perlu IP statis. |
| **Manajemen Konfigurasi WiFi** | *Captive Portal On-Demand* (WiFiManager) | Mengganti SSID/Password tanpa harus memprogram ulang (*reflashing*) mikrokontroler. |
| **Pencegahan Data Dobel** | *Cooldown Debounce Algorithm* (< 10 detik) | Mencegah terbuatnya log ganda akibat kartu tertempel dua kali secara tidak sengaja. |
| **Penyimpanan Transaksi** | Dual-Tier (EEPROM Cache + SQLite Server) | Transaksi dijamin tersimpan aman di server dengan integritas ACID SQLite. |

---

## 2. Diagram Interaksi Komunikasi (Sequence Diagram)

### A. Skenario Normal (Online Tap)
Saat ESP32 dan PC Server terhubung ke jaringan LAN yang sama:

```mermaid
sequenceDiagram
    autonumber
    actor Karyawan
    participant RFID as MFRC522 (Reader)
    participant ESP as ESP32-S3 (Client)
    participant PC as FastAPI Server
    participant DB as SQLite DB
    participant LCD as LCD 16x2 / Buzzer

    Karyawan->>RFID: Tempelkan Kartu RFID
    RFID->>ESP: Baca UID Kartu (misal: "A1B2C3D4")
    ESP->>PC: POST /api/attendance { "uid": "A1B2C3D4" }
    PC->>DB: Query kartu berdasarkan UID
    DB-->>PC: Kartu ditemukan (Nama: "Budi Santoso", Status Sebelumnya: "OUT")
    PC->>PC: Validasi Cooldown (>10 detik) & Toggle status -> "IN"
    PC->>DB: Insert log presensi baru (IN, Timestamp)
    PC-->>ESP: HTTP 200 OK { status: "success", name: "Budi Santoso", attendance: "IN" }
    ESP->>LCD: Tampilkan "Budi Santoso" & "MASUK (IN)"
    ESP->>LCD: Bunyikan Buzzer 1x (Bip Pendek) + LED Hijau Nyala
```

---

### B. Skenario Putus Jaringan (Offline Buffering)
Saat router WiFi atau server PC mati, ESP32 beralih ke mode mandiri (*offline-safe*):

```mermaid
sequenceDiagram
    autonumber
    actor Karyawan
    participant RFID as MFRC522 (Reader)
    participant ESP as ESP32-S3 (Client)
    participant Flash as EEPROM / LittleFS
    participant LCD as LCD 16x2 / Buzzer

    Karyawan->>RFID: Tempelkan Kartu RFID
    RFID->>ESP: Baca UID Kartu ("A1B2C3D4")
    ESP->>ESP: Coba hubungi PC Server (Gagal / Timeout)
    ESP->>Flash: Periksa cache UID kartu di EEPROM
    alt UID Ada di Cache Lokal
        Flash-->>ESP: Valid (Kartu Terdaftar)
        ESP->>Flash: Simpan transaksi ke LittleFS Buffer {"uid": "A1B2C3D4", "time": timestamp}
        ESP->>LCD: Tampilkan "Budi Santoso" & "OFFLINE SAVED"
        ESP->>LCD: Buzzer Bip 2x + LED Hijau Berkedip
    else UID Tidak Ada di Cache
        ESP->>LCD: Tampilkan "KARTU DITOLAK / TIDAK DIKENAL"
        ESP->>LCD: Buzzer Panjang + LED Merah Nyala
    end
```

---

### C. Skenario Pemulihan Koneksi (Auto-Sync)
Setelah server PC kembali hidup, ESP32 otomatis mengalirkan data antrean luring:

```mermaid
sequenceDiagram
    autonumber
    participant Timer as Loop Timer ESP32
    participant ESP as ESP32-S3
    participant Flash as LittleFS Offline Buffer
    participant PC as FastAPI Server
    participant DB as SQLite DB

    Timer->>ESP: Trigger Sinkronisasi Berkala (Setiap N Detik)
    ESP->>PC: Ping Heartbeat /api/ping
    PC-->>ESP: HTTP 200 OK (Server Online)
    ESP->>Flash: Periksa apakah ada antrean rekaman offline?
    Flash-->>ESP: Ada 5 log absensi tersimpan
    loop Untuk Setiap Log Offline
        ESP->>PC: POST /api/attendance/offline-sync { "uid": "...", "timestamp": "..." }
        PC->>DB: Insert log presensi dengan timestamp asli
        PC-->>ESP: HTTP 200 OK (Data Diterima)
    end
    ESP->>Flash: Hapus log yang berhasil terkirim dari Buffer
```

---

### D. Skenario Pendaftaran Kartu Baru (Enrollment Mode)
Admin mengaktifkan tombol pendaftaran kartu di web dashboard:

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    actor PemilikKartu
    participant Web as Web Dashboard
    participant PC as FastAPI Server
    participant ESP as ESP32-S3
    participant LCD as LCD 16x2

    Admin->>Web: Aktifkan "Mode Tambah Kartu" (Isi Nama: "Siti Rahma")
    Web->>PC: POST /api/cards/enroll-mode { "active": true, "name": "Siti Rahma" }
    PC->>PC: Set state backend: ENROLLMENT_ACTIVE
    PemilikKartu->>ESP: Tempelkan kartu RFID baru
    ESP->>PC: POST /api/attendance { "uid": "E5F6G7H8" }
    PC->>PC: Deteksi ENROLLMENT_ACTIVE = True
    PC->>PC: Daftarkan UID baru "E5F6G7H8" dengan Nama "Siti Rahma"
    PC->>PC: Nonaktifkan ENROLLMENT_ACTIVE
    PC-->>ESP: HTTP 200 OK { status: "enrolled", name: "Siti Rahma" }
    ESP->>LCD: Tampilkan "Siti Rahma" & "TERDAFTAR!"
    ESP->>LCD: Buzzer Bip Panjang Sukses
```

---

## 3. Flowchart Logika Firmware (ESP32-S3)

Diagram berikut menjelaskan siklus hidup (*lifecycle*) program firmware mulai dari proses booting hingga penanganan pembacaan kartu di `main.ino`:

```mermaid
flowchart TD
    Start(["Mulai / Power On"]) --> InitHW["Inisialisasi I/O:\nLCD, SPI MFRC522, I2C, Buzzer, EEPROM"]
    InitHW --> CheckWiFi{"Apakah Kredensial\nWiFi Tersimpan?"}
    
    CheckWiFi -->|"Tidak Ada / Gagal"| StartAP["Aktifkan WiFi Captive Portal\nSSID: Absensi-Setup"]
    StartAP --> UserConfig["Pengguna Mengatur SSID & Password via Web"]
    UserConfig --> ConnectWiFi["Sambungkan ke Router WiFi"]
    CheckWiFi -->|"Ada"| ConnectWiFi
    
    ConnectWiFi --> SyncNTP["Sinkronisasi Jam Internal via NTP Client"]
    SyncNTP --> ResolveMDNS["Resolusi Server via mDNS:\nCari absensi-pc.local"]
    ResolveMDNS --> SyncCardCache["Tarik Daftar UID Kartu Terbaru\nSimpan ke EEPROM / LittleFS"]
    SyncCardCache --> LoopIdle(("Mode Siaga / IDLE"))
    
    %% Siklus Loop Siaga
    LoopIdle --> CheckCard{"Ada Kartu RFID\nDitempel?"}
    CheckCard -->|"Tidak"| CheckTimers{"Cek Timer Berkala:\nSync Buffer / Cache?"}
    CheckTimers -->|"Ada Jadwal"| RunSync["Sinkronisasi Buffer Luring ke Server"]
    RunSync --> LoopIdle
    CheckTimers -->|"Belum Waktunya"| LoopIdle
    
    %% Alur Pembacaan Kartu
    CheckCard -->|"Ya"| ReadUID["Baca UID Kartu via SPI MFRC522"]
    ReadUID --> IsServerOnline{"Server PC\nDapat Dijangkau?"}
    
    %% Jalur Daring (Online)
    IsServerOnline -->|"Ya"| PostServer["Kirim POST /api/attendance\nPayload: UID + Timestamp"]
    PostServer --> CheckResponse{"Hasil Respon Server"}
    CheckResponse -->|"200 OK (Presensi)"| LCD_OK["LCD: Nama Pegawai & Status IN/OUT\nBuzzer: Bip 1x + LED Hijau ON"]
    CheckResponse -->|"200 OK (Enroll)"| LCD_Enroll["LCD: Nama Pegawai & KARTU TERDAFTAR\nBuzzer: Bip 2x + LED Hijau ON"]
    CheckResponse -->|"404 (Tidak Dikenal)"| LCD_Unknown["LCD: KARTU TIDAK TERDAFTAR\nBuzzer: Bip Panjang + LED Merah ON"]
    
    %% Jalur Luring (Offline)
    IsServerOnline -->|"Tidak"| CheckEEPROM{"Apakah UID Ada\ndi Cache EEPROM?"}
    CheckEEPROM -->|"Ada"| SaveLocalBuffer["Simpan Log ke LittleFS Buffer\nFormat: UID + Waktu Lokal"]
    SaveLocalBuffer --> LCD_OfflineOK["LCD: Nama Pegawai & OFFLINE SAVED\nBuzzer: Bip 2x + LED Hijau ON"]
    CheckEEPROM -->|"Tidak Ada"| LCD_Unknown
    
    %% Akhir Transaksi
    LCD_OK --> HoldDelay["Tahan Tampilan Selama 2 Detik"]
    LCD_Enroll --> HoldDelay
    LCD_Unknown --> HoldDelay
    LCD_OfflineOK --> HoldDelay
    HoldDelay --> LoopIdle
```

---

## 4. Flowchart Logika Server Backend (FastAPI)

Diagram berikut memetakan keputusan logika di sisi backend komputer saat menerima data dari endpoint `POST /api/attendance`:

```mermaid
flowchart TD
    API_Start(["Menerima Request:\nPOST /api/attendance"]) --> QueryDB["Cari Record Kartu di SQLite berdasarkan UID"]
    
    QueryDB --> CheckEnrollMode{"Apakah Mode Pendaftaran\n(Enrollment) Aktif?"}
    
    %% Cabang Pendaftaran
    CheckEnrollMode -->|"Ya"| CardExistsEnroll{"Kartu Sudah\nPernah Terdaftar?"}
    CardExistsEnroll -->|"Ya"| UpdateCard["Perbarui Nama / Aktifkan Kembali Status Kartu"]
    CardExistsEnroll -->|"Tidak"| InsertCard["Insert Kartu Baru ke Database"]
    UpdateCard --> DeactivateEnroll["Matikan Status Enrollment Mode"]
    InsertCard --> DeactivateEnroll
    DeactivateEnroll --> ReturnEnroll(["Kirim HTTP 200: Status 'enrolled'"])
    
    %% Cabang Presensi Normal
    CheckEnrollMode -->|"Tidak"| IsCardRegistered{"Kartu Ditemukan\n& Berstatus Aktif?"}
    IsCardRegistered -->|"Tidak"| Return404(["Kirim HTTP 404: Kartu Tidak Dikenal"])
    
    IsCardRegistered -->|"Ya"| GetLastLog["Ambil Log Kehadiran Terakhir Kartu Ini Hari Ini"]
    GetLastLog --> HasHistory{"Pernah Tap Hari Ini?"}
    
    HasHistory -->|"Ya"| CalcCooldown["Hitung Selisih Waktu:\nSekarang - Waktu Tap Terakhir"]
    CalcCooldown --> IsDebounce{"Selisih Waktu < 10 Detik?"}
    
    %% Penanganan Double-Tap
    IsDebounce -->|"Ya"| ReturnDebounce(["Kirim HTTP 200: Double-Tap Terdeteksi\nStatus Tetap & Jangan Gandakan Data"])
    
    %% Penentuan Status IN / OUT
    IsDebounce -->|"Tidak"| ToggleStatus["Jika Status Terakhir IN -> Jadikan OUT\nJika Status Terakhir OUT -> Jadikan IN"]
    HasHistory -->|"Tidak (Pertama Kali)"| SetStatusIn["Set Status Menjadi IN (Masuk)"]
    
    ToggleStatus --> SaveLog["Insert Rekaman Log Baru ke Tabel attendance_logs"]
    SetStatusIn --> SaveLog
    
    SaveLog --> ReturnSuccess(["Kirim HTTP 200: Nama Karyawan & Status Terbaru"])
```

---

## 5. Spesifikasi Kontrak REST API

Server PC mengekspos endpoint API berbasis JSON dengan standar status kode HTTP:

### `POST /api/attendance`
Dipanggil oleh ESP32 saat mendeteksi tap kartu.
- **Request Body**:
  ```json
  {
    "uid": "4A12B890"
  }
  ```
- **Response (200 OK - Presensi Berhasil)**:
  ```json
  {
    "status": "success",
    "name": "Budi Santoso",
    "attendance_type": "IN",
    "timestamp": "2026-09-12T08:00:15"
  }
  ```
- **Response (404 Not Found - Kartu Tidak Dikenal)**:
  ```json
  {
    "status": "error",
    "message": "Card UID 4A12B890 is not registered"
  }
  ```

### `GET /api/cards`
Mengambil seluruh daftar kartu aktif untuk disinkronisasikan ke memori lokal ESP32.
- **Response (200 OK)**:
  ```json
  [
    { "uid": "4A12B890", "name": "Budi Santoso", "is_active": true },
    { "uid": "E5F6G7H8", "name": "Siti Rahma", "is_active": true }
  ]
  ```

### `POST /api/attendance/offline-sync`
Mengunggah data transaksi yang tersimpan di buffer lokal ESP32 saat luring.
- **Request Body**:
  ```json
  {
    "uid": "4A12B890",
    "recorded_at": "2026-09-12T08:05:00"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "synced",
    "uid": "4A12B890"
  }
  ```
