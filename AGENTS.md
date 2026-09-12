# Memory

## Project Overview
ESP32-S3 RFID Attendance System — Sistem Presensi RFID Terdistribusi berbasis IoT & Local-First Architecture.
Menggabungkan custom PCB (KiCad), embedded C++ firmware (ESP32-S3 PlatformIO), dan web backend (Python 3.12+ FastAPI & SQLite).

Lihat [README.md](README.md) untuk ikhtisar portofolio dan solusi sistem.
Lihat [docs/architecture_flowchart.md](docs/architecture_flowchart.md) untuk detail alur data, offline buffering, dan state machine.
Lihat [docs/setup-guide.md](docs/setup-guide.md) untuk panduan instalasi dan operasional.
Lihat [docs/wiring.md](docs/wiring.md) untuk diagram pinout dan proteksi kelistrikan.
Lihat [pcb/rfid-attendance/README.md](pcb/rfid-attendance/README.md) untuk spesifikasi PCB dan BOM.

## Code Style Guidelines
- Use descriptive variable and function names.
- Follow existing modular architecture in `firmware/src/` (separation of concerns: wifi, rfid, lcd, led, pc_client, offline_buffer).
- In Python backend (`pc-app/app/`), follow PEP 8 and FastAPI best practices (type annotations, Pydantic schemas, dependency injection for DB sessions).
- Extract complex conditions into meaningful boolean variables.

## Architecture Notes
- **Local-First / Offline-First**: ESP32 saves card UIDs locally and queues attendance logs in internal flash if the PC server is unreachable.
- **mDNS Auto-Discovery**: ESP32 discovers server via `absensi-pc.local` instead of hardcoded IP addresses.
- **Debounce Cooldown**: Backend rejects duplicate taps within 10 seconds.
- **Hardware Protection**: MFRC522 must strictly use 3.3V rail; LCD 16x2 I2C backpack runs on 5V.

## Common Workflows & Commands
- **Firmware compile & upload**:
  ```bash
  cd firmware && pio run -t upload && pio device monitor
  ```
- **Run PC backend**:
  ```bash
  cd pc-app && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```
- **Run backend tests**:
  ```bash
  cd pc-app && pytest
  ```
