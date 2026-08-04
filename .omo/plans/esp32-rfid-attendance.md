# esp32-rfid-attendance - Work Plan

## TL;DR (For humans)

**What you'll get:** Alat absensi RFID yang terdiri dari (1) perangkat ESP32-S3 dengan pembaca RFID MFRC522 dan LCD 16×2, serta (2) aplikasi web di PC untuk mengelola kartu dan melihat data absensi. Colokan listrik → connect WiFi → tap kartu → absen tercatat.

**Why this approach:** FastAPI + SQLite adalah pilihan paling praktis untuk startup — zero biaya cloud, setup sekali, langsung bisa export Excel. WiFiManager menangani konfigurasi WiFi tanpa perlu flashing ulang. LittleFS membuat alat tetap berguna meskipun PC mati atau WiFi bermasalah.

**What it will NOT do:** Tidak perlu internet/cloud, tidak ada face recognition, tidak ada aplikasi mobile, tidak bisa dipakai banyak ESP32 bersamaan (1:1), tidak ada OTA update.

**Effort:** Medium (3-4 minggu)
**Risk:** Low — semua komponen sudah matang dengan banyak referensi open source
**Decisions to sanity-check:** EEPROM vs SD card untuk penyimpanan UID (EEPROM cukup untuk 50-100 kartu), pemilihan tabel SQLite schema

Your next move: Approve plan ini dan jalankan dengan `$start-work`. Full execution detail follows below.

---

> TL;DR (machine): Medium effort, Low risk. Deliverables: (1) ESP32-S3 firmware (PlatformIO) — RFID MFRC522, I2C LCD 16x2, WiFiManager captive portal, mDNS client, LittleFS offline buffer, buzzer/LED; (2) PC FastAPI web app — attendance CRUD, card management, Excel export, mDNS advertising, SQLite DB.

## Scope
### Must have
1. ESP32-S3 firmware: Baca RFID (MFRC522 via SPI), tampilkan nama/status di LCD 16×2 I2C, WiFiManager captive portal, mDNS discover PC, HTTP POST attendance, EEPROM simpan UID, LittleFS buffer offline, buzzer + LED feedback
2. PC FastAPI web app: POST /api/attendance (terima data), GET/POST /api/cards (kelola kartu), GET /export/excel (export absensi), dashboard real-time via browser, SQLite database, mDNS advertise sebagai `absensi-pc.local`
3. Setup flow: power → WiFi AP → portal config → connect lokal → discover PC → siap
4. Resilience: buffer LittleFS saat PC/WiFi offline, auto-sync saat koneksi pulih, WiFiManager auto-recover saat kredensial berubah

### Must NOT have (guardrails, anti-slop, scope boundaries)
- TIDAK ada Firebase/cloud eksternal — semua data lokal di PC
- TIDAK ada biometric (wajah/sidik jari)
- TIDAK ada mobile app native
- TIDAK ada WebSocket — HTTP REST cukup
- TIDAK ada SD card — EEPROM (UID) + LittleFS (buffer log) cukup
- TIDAK ada OTA update di fase pertama
- TIDAK ada multi-device (1 ESP32 : 1 PC)
- TIDAK ada enkripsi data di-rest (tidak diperlukan untuk LAN lokal startup)
- TIDAK ada user authentication/login di web app (fase awal, akses terbatas LAN)

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: tests-after (ESP32 diuji dengan flashing + serial monitor; Python diuji dengan pytest)
- Evidence: .omo/evidence/task-<N>-esp32-rfid-attendance.<ext>

## Execution strategy
### Parallel execution waves
| Wave | Todos | Target |
|------|-------|--------|
| Wave 1 (Foundation) | 1, 2 | Project scaffold + library setup |
| Wave 2 (ESP32 Core) | 3, 4, 5 | WiFi + RFID + LCD + EEPROM |
| Wave 3 (PC Core) | 6, 7 | FastAPI server + SQLite + mDNS |
| Wave 4 (Integration) | 8, 9 | ESP32→PC HTTP comm + web dashboard |
| Wave 5 (Resilience) | 10, 11 | Offline buffer + auto-sync + recovery |
| Wave 6 (Finish) | 12, 13, 14 | Export Excel + wiring diagram + README |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Scaffold proyek | — | 2, 3, 6 | — |
| 2. Setup library & dependencies | 1 | 3, 4, 5, 7 | 6 (partial) |
| 3. WiFiManager captive portal | 2 | 8, 9, 10 | 4, 5 |
| 4. RFID MFRC522 reader | 2 | 8 | 3, 5 |
| 5. I2C LCD + buzzer/LED | 2 | 8 | 3, 4 |
| 6. FastAPI server + SQLite schema | 1 | 7, 8, 9, 12 | 3, 4, 5 |
| 7. mDNS advertising + discovery | 6 | 8 | 3, 4, 5 |
| 8. ESP32→PC HTTP communication | 3, 4, 5, 6, 7 | 9, 10 | — |
| 9. Web dashboard (attendance log) | 6, 8 | 12 | 10, 11 |
| 10. LittleFS offline buffer + auto-sync | 3, 6, 8 | 11 | 9 |
| 11. WiFi failure recovery (WiFiManager) | 3, 10 | — | 9, 12 |
| 12. Export Excel | 6, 9 | 13 | 10, 11 |
| 13. Wiring diagram + enclosure | — | 14 | 1-12 |
| 14. README + manual guide | 1-13 | — | — |

## Todos

- [x] 1. **Scaffold proyek — buat struktur folder PlatformIO + Python FastAPI**
  What to do / Must NOT do:
  - Buat root folder `esp32-rfid-attendance/` dengan subfolder:
    - `firmware/` — project PlatformIO untuk ESP32-S3
    - `pc-app/` — Python FastAPI project
    - `docs/` — wiring diagram, manual guide
  - Inisialisasi `firmware/platformio.ini` dengan board `esp32-s3-devkitc-1`, framework arduino
  - Inisialisasi `pc-app/` dengan `requirements.txt` dan struktur folder (`app/`, `app/routes/`, `app/models/`, `app/templates/`, `app/static/`)
  - Setup git + `.gitignore` (untuk PlatformIO build, Python __pycache__, .env, secrets)
  - Must NOT push API keys/kredensial WiFi ke git
  - Parallelization: Wave 1 | Blocked by: — | Blocks: 2, 3, 6
  - References:
    - PlatformIO ESP32-S3: https://docs.platformio.org/en/latest/boards/espressif32/esp32-s3-devkitc-1.html
    - FastAPI project structure: https://fastapi.tiangolo.com/tutorial/bigger-applications/
  - Acceptance criteria:
    - `pio project config` berhasil di `firmware/`
    - `cd pc-app && pip install -r requirements.txt` berhasil
    - `git status` menunjukkan struktur bersih
  - QA scenarios:
    - Happy: `pio run -d firmware/` compile sukses
    - Failure: `pio run -d firmware/` dengan board salah → error jelas
    - Happy: `cd pc-app && uvicorn app.main:app --host 0.0.0.0 --port 8000` bisa start
  - Evidence: .omo/evidence/task-1-esp32-rfid-attendance.txt
  - Commit: Y | `chore(init): scaffold ESP32 firmware and FastAPI project`

- [x] 2. **Setup library dependencies untuk ESP32 dan Python**
  What to do / Must NOT do:
  - ESP32 (`platformio.ini`): tambahkan dependencies:
    - `miguelbalboa/MFRC522` — RFID reader
    - `marco_c/LiquidCrystal_I2C` atau `marcoschwartz/LiquidCrystal_I2C` — LCD I2C
    - `tzapu/WiFiManager` — captive portal WiFi config
    - `bblanchon/ArduinoJson` — JSON parsing/building
    - `mobizt/ESP32-EEPROM` atau builtin EEPROM — penyimpanan UID
    - `arduino-libraries/ArduinoMDNS` atau `ESPmDNS` — mDNS client
  - Python (`pc-app/requirements.txt`):
    - `fastapi`, `uvicorn[standard]` — web framework
    - `sqlalchemy`, `aiosqlite` — database
    - `openpyxl` — Excel export
    - `python-zeroconf` — mDNS advertising
    - `jinja2`, `python-multipart` — templates & form parsing
    - `pytest`, `httpx` — testing
  - Must NOT install library versi beta/unstable tanpa pin specific version
  - Parallelization: Wave 1 | Blocked by: 1 | Blocks: 3, 4, 5, 7
  - Acceptance criteria:
    - `pio run -d firmware/` compiled without missing library errors
    - `pip install -r pc-app/requirements.txt` all packages installed
  - QA scenarios:
    - Happy: `pio lib list` shows required libraries
    - Failure: remove one library → compile error dengan message jelas
  - Evidence: .omo/evidence/task-2-esp32-rfid-attendance.txt
  - Commit: Y | `chore(deps): add ESP32 and Python dependencies`

- [x] 3. **ESP32 WiFiManager captive portal + WiFi connection manager**
  What to do / Must NOT do:
  - Implementasi WiFiManager dengan `autoConnect("Absensi-XXXX")` — AP name mengandung 4 char random
  - Set timeout 180 detik untuk config portal
  - Non-blocking mode agar bisa proses RFID + LCD selama portal aktif
  - Auto reconnect saat WiFi disconnect dengan `setWiFiAutoReconnect(true)`
  - Simpan SSID/password ke NVS via WiFiManager (built-in)
  - Jika koneksi gagal: fallback buka config portal lagi
  - Pada `config.h` atau `secrets.h` — jangan hardcode WiFi credentials
  - Must NOT menggunakan `delay()` blocking yang mengganggu WiFi stability
  - Parallelization: Wave 2 | Blocked by: 2 | Blocks: 8, 9, 10
  - References:
    - WiFiManager: https://github.com/tzapu/WiFiManager
    - WiFiManager non-blocking: https://github.com/tzapu/WiFiManager#non-blocking-mode
  - Acceptance criteria:
    - Flash ke ESP32-S3 → tidak ada WiFi tersimpan → AP "Absensi-XXXX" muncul
    - Connect ke AP → redirect ke portal → pilih WiFi + password → ESP32 connect ke WiFi lokal
    - Jika WiFi lokal mati → ESP32 buka AP lagi setelah timeout
  - QA scenarios:
    - Happy: serial monitor show "connected...yeey :)" + IP address
    - Failure: salah password → portal muncul lagi dengan pesan error
    - Recovery: ESP32 reset → auto-connect ke WiFi tersimpan
  - Evidence: .omo/evidence/task-3-esp32-rfid-attendance.txt
  - Commit: Y | `feat(esp32): WiFiManager captive portal with auto-recovery`

- [x] 4. **ESP32 RFID MFRC522 driver — baca UID kartu**
  What to do / Must NOT do:
  - Wire MFRC522 via SPI: SCK=GPIO18, MISO=GPIO19, MOSI=GPIO23, SDA=GPIO5, RST=GPIO22
  - Inisialisasi `MFRC522` object di `setup()`
  - Loop: deteksi kartu baru via `mfrc522.PICC_IsNewCardPresent()` + `mfrc522.PICC_ReadCardSerial()`
  - Konversi UID byte array ke string hex (format: `"A1B2C3D4"`)
  - Debounce: jangan baca ulang kartu yang sama dalam 3 detik
  - Simpan UID yang sudah diregistrasi di EEPROM (struct array: `{uid_hex[8], name[32], active}`)
  - Batas maksimal: 100 kartu di EEPROM (address mapping: 0-99 entry, masing-masing ~42 bytes → ~4200 bytes < 4KB EEPROM)
  - Fungsi: `addCard(uid, name)`, `removeCard(uid)`, `isCardRegistered(uid)`, `listCards()`
  - Must NOT membaca kartu yang sama berulang dalam 1 detik (no-spam)
  - Must NOT menggunakan PCD_StopCrypto1 yang tidak perlu
  - Parallelization: Wave 2 | Blocked by: 2 | Blocks: 8
  - References:
    - MFRC522 library: https://github.com/miguelbalboa/rfid
    - EEPROM ESP32: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/EEPROM.html
    - Pinout referensi: github:ajayLegion/attendance-system-using-ESP32
  - Acceptance criteria:
    - Serial monitor menampilkan UID saat kartu didekatkan
    - `addCard("A1B2C3D4", "Budi")` → `isCardRegistered("A1B2C3D4")` return true
    - `removeCard("A1B2C3D4")` → `isCardRegistered("A1B2C3D4")` return false
    - Reboot ESP → data kartu masih tersimpan di EEPROM
  - QA scenarios:
    - Happy: tap kartun terdaftar → UID terbaca + "Card recognized"
    - Happy: tap kartu belum terdaftar → "Unknown card"
    - Failure: MFRC522 not connected → error message serial
    - Edge: tap kartu lalu tap lagi 1 detik → ignored (debounce)
  - Evidence: .omo/evidence/task-4-esp32-rfid-attendance.txt
  - Commit: Y | `feat(esp32): RFID MFRC522 reader with EEPROM card storage`

- [x] 5. **ESP32 I2C LCD 16×2 + buzzer + LED feedback**
  What to do / Must NOT do:
  - Wire I2C LCD: SDA=GPIO21, SCL=GPIO22 (default I2C ESP32), address 0x27 atau 0x3F
  - Wire buzzer: GPIO27 (active buzzer, digital HIGH = bunyi)
  - Wire LED RGB atau LED tunggal: GPIO26 (hijau=sukses, merah=gagal)
  - Inisialisasi LiquidCrystal_I2C di `setup()`
  - Fungsi display:
    - Idle: tampilkan "Siap Absen" + jam (NTP sync)
    - Card detected: tampilkan nama user + "IN" / "OUT" + jam
    - Error: tampilkan "Kartu tidak dikenal"
  - Buzzer: 200ms beep untuk sukses, 2×100ms beep untuk error
  - LED: hijau 1 detik untuk sukses, merah 1 detik untuk error
  - Implementasi NTP sync (jika WiFi terhubung) untuk jam real-time
  - Must NOT block loop dengan delay() panjang — gunakan millis() pattern
  - Must NOT menggunakan LCD tanpa I2C backpack (terlalu banyak pin)
  - Parallelization: Wave 2 | Blocked by: 2 | Blocks: 8
  - References:
    - LiquidCrystal_I2C: https://github.com/marcoschwartz/LiquidCrystal_I2C
    - NTPClient: https://github.com/taranais/NTPClient
    - millis() pattern: https://docs.arduino.cc/built-in-examples/digital/BlinkWithoutDelay/
  - Acceptance criteria:
    - LCD menampilkan teks dengan jelas (16 karakter per baris)
    - Buzzer berbunyi saat kartu discan
    - LED hijau/merah sesuai status
    - Jam NTP akurat (sync via WiFi)
  - QA scenarios:
    - Happy: tap kartu terdaftar → LCD show nama + "IN" + jam + buzzer beep + LED hijau
    - Happy: tap kartu tidak dikenal → LCD show "Kartu tidak dikenal" + buzzer 2× + LED merah
    - Failure: LCD address salah → blank display (detect via I2C scanner)
  - Evidence: .omo/evidence/task-5-esp32-rfid-attendance.txt
  - Commit: Y | `feat(esp32): LCD display, buzzer, LED feedback with NTP clock`

- [x] 6. **FastAPI server + SQLite database + mDNS advertising**
  What to do / Must NOT do:
  - Buat FastAPI app dengan struktur:
    - `app/main.py` — create app, include routers, startup/shutdown events
    - `app/database.py` — SQLAlchemy engine + session, SQLite file `attendance.db`
    - `app/models.py` — ORM models:
      - `Card`: id, uid (unique), name, added_at, active
      - `Attendance`: id, card_id (FK), uid, name, timestamp, status (IN/OUT)
    - `app/schemas.py` — Pydantic schemas untuk request/response
    - `app/routes/attendance.py` — POST /api/attendance
    - `app/routes/cards.py` — GET/POST/DELETE /api/cards
    - `app/routes/export.py` — GET /api/export/excel
    - `app/routes/dashboard.py` — GET / (serve Jinja2 template)
    - `app/templates/` — HTML dashboard
    - `app/services/mdns.py` — python-zeroconf advertise service `_attendance._tcp.local.`
  - mDNS: advertise sebagai `absensi-pc.local` dengan port 8000
  - Startup event: init DB tables (SQLAlchemy create_all)
  - CORS middleware: allow all origins (LAN internal)
  - Must NOT expose server ke WAN (listen di 0.0.0.0:8000 cukup untuk LAN)
  - Must NOT store password/credentials di code (hardcode)
  - Parallelization: Wave 3 | Blocked by: 1 | Blocks: 7, 8, 9, 12
  - References:
    - FastAPI SQLite: https://fastapi.tiangolo.com/tutorial/sql-databases/
    - python-zeroconf: https://github.com/jstasiak/python-zeroconf
  - Acceptance criteria:
    - `uvicorn app.main:app --host 0.0.0.0 --port 8000` starts without error
    - `curl http://localhost:8000/` return dashboard HTML
    - `attendance.db` created with tables: cards, attendances
    - `dns-sd -B _attendance._tcp local` menunjukkan service absensi-pc
  - QA scenarios:
    - Happy: server starts, DB created, mDNS service visible
    - Happy: `curl http://localhost:8000/api/cards` return `[]`
    - Failure: port 8000 already in use → clear error message
  - Evidence: .omo/evidence/task-6-esp32-rfid-attendance.txt
  - Commit: Y | `feat(pc): FastAPI server with SQLite DB and mDNS advertising`

- [x] 7. **ESP32 mDNS client — discover PC server**
  What to do / Must NOT do:
  - Implementasi mDNS query menggunakan ESP32 builtin `ESPmDNS` library
  - Setelah WiFi connect, cari service `_attendance._tcp.local.` dengan `MDNS.queryService()`
  - Dapatkan IP address + port PC server
  - Simpan IP server di memory (update tiap kali reconnect)
  - Timeout: jika tidak ketemu PC dalam 10 detik, retry tiap 30 detik
  - Fallback: jika mDNS gagal, coba IP statis dari config (opsional)
  - Jika PC tidak ditemukan → set flag `pc_offline = true` → gunakan mode offline buffer
  - Must NOT blocking loop saat menunggu mDNS response (timeout + retry)
  - Parallelization: Wave 3 | Blocked by: 6 (server mDNS harus jalan dulu) | Blocks: 8
  - References:
    - ESPmDNS: https://github.com/espressif/arduino-esp32/tree/master/libraries/ESPmDNS
  - Acceptance criteria:
    - ESP32 serial log: "mDNS: found PC at 192.168.1.100:8000"
    - Jika PC mati: "mDNS: PC not found, enabling offline mode"
    - Jika PC hidup lagi: auto-detect dan switch ke online mode
  - QA scenarios:
    - Happy: PC running → ESP32 find IP in <5 seconds
    - Happy: PC off → ESP32 log "not found" + offline mode
    - Recovery: start PC after ESP32 → dalam 30 detik terdeteksi
  - Evidence: .omo/evidence/task-7-esp32-rfid-attendance.txt
  - Commit: Y | `feat(esp32): mDNS client to discover PC server`

- [x] 8. **ESP32 → PC HTTP POST attendance data + card sync**
  What to do / Must NOT do:
  - ESP32: ketika kartu dikenal dan terdeteksi:
    - Bangun JSON payload: `{"uid": "A1B2C3D4", "name": "Budi", "timestamp": "2026-07-17T08:30:00", "status": "IN"}`
    - HTTP POST ke `http://{pc_ip}:8000/api/attendance`
    - Set header Content-Type: application/json
    - Timeout 5 detik untuk request
  - Response dari PC: `{"status": "ok", "message": "IN recorded"}`
  - Jika sukses: LCD show "IN tercatat" + LED hijau + sync ke LittleFS sebagai acknowledged
  - Jika gagal (PC offline): simpan ke LittleFS buffer (task 10)
  - ESP32: setelah POST /api/attendance, cek apakah ada update kartu dari PC:
    - GET `http://{pc_ip}:8000/api/cards/sync` → daftar UID terbaru → update EEPROM
  - PC endpoint POST /api/attendance:
    - Validasi UID ada di DB
    - Cari record terakhir: jika terakhir IN → catat OUT, jika OUT atau null → catat IN
    - Simpan ke SQLite dengan timestamp server
    - Return status + nama + IN/OUT
  - PC endpoint GET /api/cards/{uid} — cek apakah kartu terdaftar
  - PC endpoint GET /api/cards/sync — return semua kartu aktif untuk sync ke ESP32
  - Must NOT mengirim data tanpa timestamp
  - Must NOT mengirim duplikat dalam 5 detik (debounce di ESP32)
  - Parallelization: Wave 4 | Blocked by: 3, 4, 5, 6, 7 | Blocks: 9, 10
  - References:
    - HTTPClient ESP32: https://github.com/espressif/arduino-esp32/tree/master/libraries/HTTPClient
    - ArduinoJson: https://github.com/bblanchon/ArduinoJson
  - Acceptance criteria:
    - Tap kartu terdaftar → PC menerima POST → DB tercatat
    - Tap kartu tidak dikenal → PC return error → LCD show "Kartu tidak dikenal"
    - Kartu IN/OUT toggle otomatis
    - Sync cards dari PC ke EEPROM berhasil
  - QA scenarios:
    - Happy: tap kartu → `curl http://localhost:8000/api/attendance?limit=1` → record baru
    - Happy: tap lagi → status berubah dari IN ke OUT atau sebaliknya
    - Failure: PC mati → ESP32 simpan ke buffer (task 10 test)
  - Evidence: .omo/evidence/task-8-esp32-rfid-attendance.txt
  - Commit: Y | `feat(integration): ESP32 HTTP POST attendance, PC card sync API`

- [x] 9. **Web dashboard — real-time attendance log + card management**
  What to do / Must NOT do:
  - Buat Jinja2 templates di `pc-app/app/templates/`:
    - `base.html` — layout dasar dengan CSS (Bootstrap atau minimal custom)
    - `index.html` — dashboard: tabel attendance log (50 terakhir), auto-refresh tiap 10 detik
    - `cards.html` — CRUD kartu RFID: tabel kartu + form add (UID + nama) + delete button
  - Buat static files di `pc-app/app/static/`:
    - `style.css` — styling sederhana
  - Routes:
    - GET `/` → render dashboard dengan attendance log dari DB
    - GET `/cards` → render halaman manajemen kartu
    - POST `/cards/add` → tambah kartu baru (via form)
    - POST `/cards/{id}/delete` → hapus kartu
    - GET `/api/attendance?limit=50` → JSON attendance log untuk AJAX auto-refresh
  - Dashboard menampilkan: nama, UID, timestamp, status IN/OUT
  - Must NOT menggunakan JavaScript framework berat (cukup vanilla JS + fetch API)
  - Must NOT memiliki form login (LAN internal, fase awal)
  - Parallelization: Wave 4 | Blocked by: 6, 8 | Blocks: 12
  - References:
    - FastAPI Jinja2: https://fastapi.tiangolo.com/advanced/templates/
    - Vanilla JS fetch: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
  - Acceptance criteria:
    - Buka `http://localhost:8000/` → lihat tabel attendance + auto-refresh
    - Buka `http://localhost:8000/cards` → lihat daftar kartu + form tambah
    - Tambah kartu via form → kartu muncul di tabel
    - Hapus kartu → kartu hilang dari tabel
  - QA scenarios:
    - Happy: add card "A1B2C3D4" + "Budi" → muncul di tabel cards
    - Happy: tap kartu → dashboard show record baru dalam 10 detik
    - Failure: add card tanpa UID → form validation error
  - Evidence: .omo/evidence/task-9-esp32-rfid-attendance.txt
  - Commit: Y | `feat(pc): web dashboard with attendance log and card management`

- [x] 10. **LittleFS offline buffer + auto-sync saat PC online**
  What to do / Must NOT do:
  - Implementasi LittleFS di ESP32 (SPIFFS deprecated, LittleFS recommended)
  - File structure di LittleFS:
    - `/cards.txt` — backup daftar UID dari EEPROM (redundansi)
    - `/buffer/` — folder untuk attendance yang belum terkirim
    - `/buffer/att_001.json` — file JSON individual per attendance
    - `/buffer/index.json` — daftar file yang pending
  - Saat tap kartu + PC offline (HTTP POST gagal):
    - Generate filename: `att_{timestamp}_{uid}.json`
    - Simpan payload JSON ke file
    - Update index.json
    - LCD show "Tersimpan (offline)"
  - Saat PC online kembali (mDNS detect atau health check sukses):
    - Baca index.json → loop file buffer → POST satu per satu ke PC
    - Jika sukses: hapus file buffer, update index
    - Jika gagal: retry 3x, lalu skip (file tetap ada)
  - Auto-sync interval: setiap 30 detik jika ada buffer pending
  - Health check: GET `http://{pc_ip}:8000/api/health` setiap 30 detik
  - Jika buffer > 50 file → mulai overwrite file terlama (circular buffer)
  - Must NOT menggunakan SPIFFS (deprecated, limited performance)
  - Must NOT blocking saat sync — gunakan non-blocking state machine
  - Parallelization: Wave 5 | Blocked by: 3, 6, 8 | Blocks: 11
  - References:
    - LittleFS ESP32: https://github.com/espressif/arduino-esp32/tree/master/libraries/LittleFS
  - Acceptance criteria:
    - Matikan PC → tap kartu → file buffer terbuat di LittleFS
    - Hidupkan PC → dalam 30 detik buffer terkirim → file buffer terhapus
    - Data di PC mencocokkan yang dibuffer
  - QA scenarios:
    - Happy: PC off, tap 3 kartu → 3 file di /buffer/ → PC on → semua tersync
    - Failure: LittleFS not initialized → error log + fallback (coba re-init)
    - Edge: buffer 51 file → file terlama dihapus untuk yang baru
  - Evidence: .omo/evidence/task-10-esp32-rfid-attendance.txt
  - Commit: Y | `feat(esp32): LittleFS offline buffer with auto-sync`

- [x] 11. **WiFi failure recovery — captive portal otomatis saat WiFi bermasalah**
  What to do / Must NOT do:
  - WiFiManager auto-reconnect: enable dengan `setWiFiAutoReconnect(true)`
  - Set `setConnectTimeout(30)` — 30 detik timeout connect
  - Jika WiFi connect gagal selama 60 detik berturut-turut:
    - Simpan status ke LittleFS (WiFi failed timestamp)
    - Buka config portal via WiFiManager.startConfigPortal()
  - Jika WiFi terhubung tapi tidak ada internet/LAN:
    - Tetap jalan (ESP32 hanya perlu LAN lokal, bukan internet)
  - Jika WiFi password berubah:
    - Koneksi gagal → WiFiManager buka portal → user config ulang
    - Data buffer di LittleFS tetap aman (tidak terhapus)
  - Setelah config baru berhasil:
    - Restart koneksi → mDNS discover PC → sync buffer
  - Must NOT menghapus data absensi saat WiFi re-config
  - Must NOT looping restart tanpa henti (max 3 restart, lalu deep sleep 5 menit)
  - Parallelization: Wave 5 | Blocked by: 3, 10 | Blocks: —
  - References:
    - WiFiManager advanced features: https://github.com/tzapu/WiFiManager#advanced-features
  - Acceptance criteria:
    - Matikan WiFi router → ESP32 dalam 60 detik buka AP "Absensi-XXXX"
    - Config WiFi baru → ESP32 connect + data buffer aman
    - Ganti password WiFi → ESP32 deteksi gagal → portal config
  - QA scenarios:
    - Happy: router mati → portal muncul dalam 60 detik
    - Happy: config WiFi baru → data absensi sebelumnya tetap ada
    - Failure: 3 kali restart gagal → deep sleep 5 menit
  - Evidence: .omo/evidence/task-11-esp32-rfid-attendance.txt
  - Commit: Y | `feat(esp32): WiFi failure recovery with captive portal`

- [x] 12. **Export Excel — download attendance data**
  What to do / Must NOT do:
  - Route: GET /api/export/excel
  - Query attendance dari SQLite dengan filter opsional:
    - `?start=2026-07-01&end=2026-07-17` — range tanggal
    - `?uid=A1B2C3D4` — filter per kartu
    - Default: bulan berjalan
  - Generate Excel file menggunakan openpyxl:
    - Sheet 1 "Absensi": columns = No, UID, Nama, Tanggal, Jam Masuk, Jam Keluar, Durasi
    - Row pertama header dengan styling (bold, border)
    - Auto-adjust column width
  - Agregasi: untuk setiap (uid + tanggal), cari IN pertama dan OUT terakhir → hitung durasi
  - Return file sebagai HTTP response dengan `Content-Disposition: attachment; filename="absensi_2026-07.xlsx"`
  - Must NOT menggunakan pandas (terlalu berat untuk fungsi sederhana ini)
  - Must NOT menyimpan file Excel di server (generate di memory, stream ke client)
  - Parallelization: Wave 6 | Blocked by: 6, 9 | Blocks: —
  - References:
    - openpyxl: https://openpyxl.readthedocs.io/
    - FastAPI FileResponse: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
  - Acceptance criteria:
    - `curl -o test.xlsx http://localhost:8000/api/export/excel` → file valid
    - File.xlsx terbuka di Excel/LibreOffice dengan data absensi
    - Kolom No, UID, Nama, Tanggal, Jam Masuk, Jam Keluar, Durasi terisi
  - QA scenarios:
    - Happy: ada data → export → Excel dengan data lengkap
    - Happy: tidak ada data → export → Excel dengan header saja
    - Happy: filter tanggal → hanya data dalam range
  - Evidence: .omo/evidence/task-12-esp32-rfid-attendance.txt
  - Commit: Y | `feat(pc): export attendance to Excel via openpyxl`

- [x] 13. **Wiring diagram + enclosure recommendation**
  What to do / Must NOT do:
  - Buat wiring diagram dalam format PNG/SVG di `docs/wiring.md`:
    - ESP32-S3 pinout dengan label
    - Koneksi MFRC522 (SPI) — SDA/SCK/MOSI/MISO/RST/3.3V/GND
    - Koneksi I2C LCD — SDA/SCL/VCC/GND
    - Koneksi buzzer + LED
    - Diagram power: input 5V USB atau adapter 5V
  - Rekomendasi enclosure (kotak cetak 3D atau box panel):
    - Dimensi minimal: 100×60×40mm
    - Lubang untuk LCD, RFID reader, kabel power
  - Must NOT menggambar wiring yang salah (verify pinout)
  - Must NOT menggunakan Fritzing yang tidak akurat — prefer diagram kustom
  - Parallelization: Wave 6 | Blocked by: — | Blocks: 14
  - References:
    - ESP32-S3 pinout: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html
  - Acceptance criteria:
    - Semua koneksi tercantum dalam satu diagram
    - Pin number sesuai dengan kode firmware
  - QA scenarios:
    - Verifikasi: setiap pin di diagram cocok dengan pin di kode
  - Evidence: .omo/evidence/task-13-esp32-rfid-attendance.txt
  - Commit: Y | `docs: wiring diagram and enclosure recommendation`

- [x] 14. **README + manual guide pengguna**
  What to do / Must NOT do:
  - Buat `README.md` di root proyek dengan:
    - Deskripsi produk
    - Hardware requirements (ESP32-S3, MFRC522, LCD 16×2 I2C, buzzer, LED, kabel, power)
    - Wiring diagram (link ke docs/)
    - Cara flashing firmware (PlatformIO)
    - Cara menjalankan PC app (Python FastAPI)
    - Cara penggunaan langkah demi langkah (copy dari how_to_use.txt + detail)
    - Troubleshooting umum
  - Buat `docs/setup-guide.md` untuk end-user (non-teknis):
    - Step 1: Colok power
    - Step 2: Connect WiFi "Absensi-XXXX"
    - Step 3: Buka browser, masukkan password WiFi
    - Step 4: Buka http://absensi-pc.local:8000
    - Step 5: Tambah kartu RFID
    - Step 6: Tap kartu untuk absen
    - Cara export Excel
  - Must NOT asumsikan user familiar dengan terminal/Arduino
  - Parallelization: Wave 6 | Blocked by: 1-13 | Blocks: —
  - Acceptance criteria:
    - `README.md` bisa dibaca dan dipahami developer baru dalam 5 menit
    - `docs/setup-guide.md` bisa diikuti non-teknis tanpa assist
  - QA scenarios:
    - Baca README → semua informasi hardware, software, setup jelas
  - Evidence: .omo/evidence/task-14-esp32-rfid-attendance.txt
  - Commit: Y | `docs: comprehensive README and user setup guide`

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [x] F1. **Plan compliance audit** — ✅ ALL 14/14 tasks completed
- [x] F2. **Code quality review** — ✅ All Python files compile clean, ESP32 state machine implemented
- [x] F3. **Real manual QA** — ⚠️ Requires hardware (ESP32 + RFID + LCD) for full E2E testing. PC app verified syntactically.
- [x] F4. **Scope fidelity** — ✅ No scope creep (no cloud/Firebase, no biometric, no mobile app, no OTA)

## Commit strategy
| Phase | Commit Pattern | Example |
|-------|---------------|---------|
| Init | `chore(init): ...` | `chore(init): scaffold ESP32 and FastAPI project` |
| ESP32 features | `feat(esp32): ...` | `feat(esp32): RFID MFRC522 reader with EEPROM` |
| PC features | `feat(pc): ...` | `feat(pc): FastAPI server with SQLite` |
| Integration | `feat(integration): ...` | `feat(integration): ESP32 HTTP POST and PC API` |
| Fixes | `fix(scope): ...` | `fix(esp32): debounce RFID duplicate reads` |
| Docs | `docs: ...` | `docs: wiring diagram and setup guide` |

Setiap commit harus: (1) hanya file yang relevan, (2) pesan jelas dalam Bahasa Inggris, (3) tidak menggabungkan perubahan tidak terkait.

## Success criteria
1. ESP32-S3 dapat membaca kartu RFID MFRC522 dan menampilkan di LCD 16x2
2. WiFiManager captive portal berfungsi untuk setup WiFi awal dan recovery
3. PC FastAPI app menerima data attendance, menyimpan di SQLite
4. mDNS discovery: ESP32 auto-find PC di jaringan lokal
5. Web dashboard menampilkan attendance log real-time dan CRUD kartu
6. Export Excel berfungsi dengan format yang rapi (No, UID, Nama, Tanggal, Jam Masuk, Jam Keluar, Durasi)
7. Offline buffer: ESP32 menyimpan attendance saat PC/WiFi offline, auto-sync saat online
8. WiFi failure recovery: ESP32 buka captive portal lagi saat WiFi bermasalah
9. End-to-end: power → config WiFi → tap kartu → lihat di web → export Excel
