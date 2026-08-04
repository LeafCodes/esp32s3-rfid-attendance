---
slug: esp32-rfid-attendance
status: awaiting-approval
intent: clear
pending-action: write .omo/plans/esp32-rfid-attendance.md
approach: ESP32-S3 firmware (PlatformIO + Arduino framework) + Python FastAPI web app + SQLite. WiFiManager captive portal for setup, HTTP REST for communication, LittleFS offline buffer, mDNS for PC discovery.
---

# Draft: esp32-rfid-attendance

## Components (topology ledger)
| id | outcome | status | evidence path |
|----|---------|--------|---------------|
| esp32-firmware | ESP32-S3 reads RFID, shows LCD, connects WiFi, sends HTTP | active | github:ajayLegion/attendance-system-using-ESP32 |
| pc-app | FastAPI web app receives attendance, manages cards, exports Excel | active | websearch:ESP32 Flask/FastAPI patterns |
| captive-portal | WiFiManager for initial WiFi config & recovery | active | github:tzapu/WiFiManager |
| offline-buffer | LittleFS stores attendance when PC/WiFi offline | active | github:andrei-vasile-dev/esp32-rfid-attendance-system |
| mDNS-discovery | PC advertises via mDNS, ESP32 finds it | active | arduino-forum:ESP32-PC communication patterns |

## Open assumptions (announced defaults)
| assumption | adopted default | rationale | reversible? |
|-----------|----------------|-----------|-------------|
| Arduino framework over ESP-IDF | Arduino (PlatformIO) | Lebih cepat develop, library support luas untuk RFID/LCD/WiFiManager | Yes |
| HTTP REST over WebSocket/MQTT | HTTP POST JSON | Paling sederhana, reliable, easy to debug | Yes |
| SQLite over MySQL/PostgreSQL | SQLite (via FastAPI) | Startup scale, zero config, file-based | Yes |
| EEPROM for UID list (max ~50 cards) | EEPROM (4KB) | Cukup untuk startup, lebih sederhana dari SD card | Yes |
| mDNS over UDP broadcast | mDNS (zeroconf) | Standar industri, reliable di LAN | Yes |
| PlatformIO over Arduino IDE | PlatformIO | Manajemen library, multi-env, CLI-friendly | Yes |

## Findings (cited - path:lines)
- MFRC522 pinout standar: SCK=GPIO18, MISO=GPIO19, MOSI=GPIO23, SDA=GPIO5/21, RST=GPIO22 (github:ajayLegion/attendance-system-using-ESP32)
- tzapu/WiFiManager library adalah gold standard untuk captive portal ESP32 (github:tzapu/WiFiManager#README)
- Pola komunikasi ESP32→PC yang paling umum: HTTP POST JSON ke Flask/FastAPI server (stackoverflow:76894413, dfrobot:blog-1036)
- Offline buffering dengan LittleFS/SPIFFS sudah dipakai di proyek andrei-vasile-dev/esp32-rfid-attendance-system
- TapTag (github:s-m-quadri/taptag) menggunakan arsitektur ESP32 + Express + MongoDB + Flutter — tapi terlalu berat untuk startup
- Wiattend (github:abobija/wiattend) pakai NodeJS + MySQL + WebSocket — arsitektur mirip tapi beda stack

## Decisions (with rationale)
1. **ESP32-S3** — lebih modern dari ESP32-WROOM, dual-core, lebih banyak RAM. Dipilih user.
2. **I2C LCD 16x2** — untuk menampilkan nama user, status IN/OUT, jam. Dipilih user.
3. **Web App (FastAPI)** — user akses via browser, export Excel, manage cards. Dipilih user.
4. **WiFiManager** untuk captive portal — auto fallback saat WiFi gagal, user configure via browser.
5. **mDNS (python-zeroconf)** — PC advertise sebagai `absensi-pc.local`, ESP32 auto-discover.
6. **LittleFS** untuk offline buffer — data tetap aman meski PC/WiFi mati, sync saat koneksi pulih.

## Scope IN
- ESP32-S3 firmware: RFID scan, LCD display, WiFiManager captive portal, HTTP client, mDNS discovery, offline buffer, buzzer/LED feedback
- PC FastAPI web app: menerima POST attendance, CRUD kartu RFID, dashboard real-time, export Excel, mDNS advertising
- Setup wizard: pertama kali nyala → captive portal → config WiFi → discover PC → siap pakai
- Resilien: PC mati → buffer di ESP32; WiFi berubah → portal lagi; sync otomatis

## Scope OUT (Must NOT have)
- TIDAK pakai cloud Firebase/external — semua lokal di PC
- TIDAK pakai biometric / face recognition
- TIDAK pakai mobile app native
- TIDAK pakai real-time WebSocket (HTTP REST cukup)
- TIDAK pakai SD card (EEPROM + LittleFS cukup)
- TIDAK pakai OTA update (fase pertama)
- TIDAK ada multi-device sync (1 ESP32 : 1 PC)

## Open questions
- [RESOLVED by user] ESP32 model → ESP32-S3
- [RESOLVED by user] Display → I2C LCD 16x2
- [RESOLVED by user] PC App → Web App via FastAPI

## Approval gate
status: awaiting-approval
<!-- When exploration is exhausted and unknowns are answered, set status: awaiting-approval. -->
<!-- That durable record is the loop guard: on a later turn read it and resume at the gate instead of re-running exploration. -->
