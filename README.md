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
