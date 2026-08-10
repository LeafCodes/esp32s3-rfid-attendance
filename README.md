# ESP32-S3 RFID Attendance System

Sistem absensi RFID berbasis ESP32-S3 dengan PC web app untuk startup.

## Fitur

- 📇 **RFID Scanning** — Baca kartu RFID MFRC522, deteksi IN/OUT otomatis
- 📶 **WiFi Manager** — Setup WiFi via captive portal (tanpa flashing ulang)
- 🖥️ **LCD 16x2** — Tampilkan nama, status, jam real-time
- 💻 **PC Web App** — Dashboard absensi, kelola kartu, export Excel
- 📱 **mDNS Discovery** — ESP32 auto-detect PC di jaringan
- 🔄 **Offline Buffer** — Data tetap aman meski PC/WiFi mati
- 📊 **Export Excel** — Download laporan absensi dengan format rapi

## Hardware Requirements

| Komponen | Spesifikasi |
|----------|-------------|
| ESP32-S3 DevKitC-1 | Microcontroller dengan WiFi |
| MFRC522 | RFID reader (13.56MHz, SPI) |
| LCD 16x2 I2C | Display (address 0x27/0x3F) |
| Buzzer + LED | Feedback suara/cahaya |
| RFID Cards | MIFARE Classic 1K |
| Power 5V | USB-C atau adapter |

## Konfigurasi Pin Hardware
Pemetaan pin (*pinout*) pada proyek ini dirancang untuk **ESP32-S3**, namun Anda bebas mengubahnya.

### Pin Bawaan (Default)
**1. Modul RFID MFRC522 (Jalur SPI)**
- **SCK**  : Pin 12
- **MISO** : Pin 13
- **MOSI** : Pin 11
- **SS (SDA)**: Pin 10
- **RST**  : Pin 14

**2. LCD 16x2 I2C (Jalur I2C)**
- **SDA** : Pin 8
- **SCL** : Pin 9

**3. Output Tambahan**
- **Buzzer** : Pin 15
- **LED Hijau**: Pin 16
- **LED Merah**: Pin 17

### Cara Mengubah Pin
Semua definisi pin dipusatkan pada satu file konfigurasi. Jika Anda menggunakan board ESP32 jenis lain (misal ESP32 WROOM-32 biasa) atau ingin memindahkan pin, silakan ubah pada file:
👉 **`firmware/src/config.h`**

```cpp
// Contoh bagian yang bisa diedit di config.h
#define SPI_SCK   12
#define LCD_SDA   8
```

### Syarat Pemilihan Pin (Penting!)
Jika Anda ingin mengubah pin, patuhi aturan dasar berikut agar ESP32 tidak *crash*:
1. **Hindari Strapping Pins:** Jangan gunakan pin seperti GPIO 0, 46, 45, 3 (pada ESP32-S3) atau GPIO 0, 2, 5, 12, 15 (pada ESP32 WROOM biasa) untuk komponen eksternal kecuali Anda paham dampaknya, karena pin ini digunakan untuk proses *booting*.
2. **Jalur I2C (LCD):** Secara teori semua GPIO bisa digunakan untuk I2C pada ESP32, namun pastikan pin tersebut mendukung mode *Input/Output*. Jangan lupa modul LCD I2C membutuhkan daya 5V, bukan 3.3V.
3. **Jalur SPI (RFID):** Meskipun ESP32 mendukung matrix *hardware/software SPI* ke hampir semua pin, lebih stabil jika menggunakan pin SPI bawaan bawaan dari *board* Anda (VSPI / HSPI).
4. **Input Only Pins:** Pada ESP32 biasa, pin 34, 35, 36, 39 hanya bisa digunakan sebagai *input*. Jangan gunakan pin ini untuk Buzzer atau LED (Output).

## Software Requirements

### ESP32 Firmware
- PlatformIO
- Arduino framework for ESP32-S3
- Libraries: WiFiManager, MFRC522, LiquidCrystal_I2C, ArduinoJson, NTPClient, ESPmDNS, LittleFS

### PC App
- Python 3.12+
- FastAPI + Uvicorn
- SQLAlchemy + SQLite
- openpyxl
- python-zeroconf

## Quick Start

### 1. Flashing ESP32
```bash
cd firmware
pio run -t upload
pio device monitor
```

### 2. Running PC App
```bash
cd pc-app
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Buka Browser
```
http://absensi-pc.local:8000
http://localhost:8000
```

## Project Structure
```
├── firmware/           # ESP32-S3 PlatformIO project
│   ├── src/           # Source code
│   ├── include/       # Headers
│   └── platformio.ini
├── pc-app/            # Python FastAPI web app
│   ├── app/           # Application code
│   │   ├── routes/    # API endpoints
│   │   ├── services/  # mDNS, etc.
│   │   ├── templates/ # HTML templates
│   │   └── static/    # CSS
│   ├── tests/         # Pytest tests
│   └── requirements.txt
└── docs/              # Documentation
```

## Wiring
Lihat [docs/wiring.md](docs/wiring.md) untuk diagram koneksi hardware lengkap.

## Setup Guide
Lihat [docs/setup-guide.md](docs/setup-guide.md) untuk panduan penggunaan.

## License
MIT
