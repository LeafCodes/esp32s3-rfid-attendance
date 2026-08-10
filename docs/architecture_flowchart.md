# Arsitektur & Flowchart Sistem Absensi RFID

Dokumen ini memuat diagram alir (*flowchart*) yang mendeskripsikan cara kerja dari dua komponen utama sistem kita: **Firmware (ESP32)** dan **PC-App (FastAPI Backend)**.

## 1. Flowchart Firmware (ESP32)
Flowchart di bawah ini menjelaskan alur program dari saat perangkat dinyalakan (*boot*) hingga ia membaca kartu (Online maupun Offline).

```mermaid
flowchart TD
    Start([Mulai / Boot]) --> Init[Inisialisasi LCD, Buzzer, RFID, EEPROM]
    Init --> WiFi{Koneksi WiFi?}
    
    WiFi -- Sukses --> NTP[Sinkronisasi Waktu NTP]
    WiFi -- Gagal --> Portal[Buka WiFi Captive Portal]
    Portal --> WiFi
    
    NTP --> mDNS[Cari PC Server via mDNS]
    mDNS --> Idle((Mode IDLE))
    
    %% Proses Loop
    Idle --> SyncTimer{Waktu Sync?}
    SyncTimer -- Ya --> FetchCards[Tarik Daftar Kartu dari Server]
    FetchCards --> UpdateEEPROM[Simpan ke EEPROM]
    UpdateEEPROM --> Idle
    
    Idle --> BufferTimer{Ada Data Offline & Online?}
    BufferTimer -- Ya --> SendBuffer[Kirim Data Buffer ke Server]
    SendBuffer --> HapusBuffer[Hapus dari Buffer Lokal]
    HapusBuffer --> Idle
    
    Idle --> CardTap{Kartu Ditempel?}
    CardTap -- Tidak --> Idle
    
    %% Proses Tap Kartu
    CardTap -- Ya --> ReadUID[Baca UID Kartu]
    ReadUID --> ServerCheck{Server Online?}
    
    %% Alur Online
    ServerCheck -- Ya --> PostAPI[Kirim POST /api/attendance]
    PostAPI --> APIRes{Respon Server}
    APIRes -- 200 OK --> ShowLCD1[Tampilkan Nama & IN/OUT]
    APIRes -- 404 Not Found --> ErrorLCD1[LCD: Unknown Card]
    APIRes -- 200 (Mode Daftar) --> DaftarLCD[LCD: TERDAFTAR]
    
    ShowLCD1 --> BuzzerOK[Buzzer Sukses]
    ErrorLCD1 --> BuzzerErr[Buzzer Error]
    DaftarLCD --> BuzzerOK
    
    %% Alur Offline
    ServerCheck -- Tidak --> LocalCheck{Kartu Terdaftar di EEPROM?}
    LocalCheck -- Ya --> ShowLCD2[LCD: Nama & IN]
    LocalCheck -- Tidak --> ErrorLCD2[LCD: Unknown Card]
    
    ShowLCD2 --> SaveBuffer[Simpan ke Memori Offline Buffer]
    SaveBuffer --> BuzzerOK2[Buzzer Sukses]
    ErrorLCD2 --> BuzzerErr2[Buzzer Error]
    
    BuzzerOK --> Delay[Tunggu 2 Detik]
    BuzzerErr --> Delay
    BuzzerOK2 --> Delay
    BuzzerErr2 --> Delay
    
    Delay --> Idle
```

---

## 2. Flowchart PC-App (FastAPI Backend)
Flowchart ini mendeskripsikan logika yang berjalan di *Server* (Komputer PC Anda) saat menerima kiriman data tap kartu dari ESP32 (API Endpoint: `POST /api/attendance`).

```mermaid
flowchart TD
    API_Start([Terima POST /api/attendance]) --> CekDB[Cari UID di Database SQLite]
    
    CekDB --> ModeDaftar{Mode Enrollment Aktif?}
    
    %% Alur Pendaftaran Kartu
    ModeDaftar -- Ya --> CekKartuBaru{Kartu Sudah Terdaftar?}
    CekKartuBaru -- Ya --> DaftarLama[Update Nama, set Active]
    CekKartuBaru -- Tidak --> DaftarBaru[Insert Kartu Baru ke DB]
    DaftarLama --> MatikanMode[Matikan Mode Enrollment]
    DaftarBaru --> MatikanMode
    MatikanMode --> ReturnDaftar([Return: 200 OK, Status: TERDAFTAR])
    
    %% Alur Absensi Biasa
    ModeDaftar -- Tidak --> ValidasiKartu{Kartu Ditemukan di DB?}
    ValidasiKartu -- Tidak --> Return404([Return: 404 Card Not Found])
    
    ValidasiKartu -- Ya --> CekCooldown[Ambil Absensi Terakhir Kartu Ini]
    CekCooldown --> AdaAbsen{Ada Riwayat?}
    
    AdaAbsen -- Ya --> HitungWaktu[Selisih Waktu < 10 Detik?]
    HitungWaktu -- Ya (Double Tap) --> ReturnCooldown([Return: 200 OK, Status Dipertahankan])
    
    %% Pencatatan Normal
    HitungWaktu -- Tidak --> BalikStatus[Tentukan Status: IN / OUT]
    AdaAbsen -- Tidak (Absen Pertama) --> SetIN[Tentukan Status: IN]
    
    BalikStatus --> InsertLog[Insert Data Kehadiran ke DB]
    SetIN --> InsertLog
    
    InsertLog --> ReturnSukses([Return: 200 OK, Nama & Status IN/OUT])
```

## Kesimpulan Logika Inti:
1. **Pemisahan Tanggung Jawab:** ESP32 bertindak sebagai *client* pengumpul data dan penampil status, sementara PC-App menanggung beban logika utama (Double-Tap, Penentuan IN/OUT, Pendaftaran Kartu).
2. **Offline-Safe:** ESP32 dapat berdiri sendiri saat WiFi atau PC-App mati berkat adanya penyalinan data UID ke *EEPROM* dan penyimpanan catatan absen di memori lokal (*Offline Buffer*).
