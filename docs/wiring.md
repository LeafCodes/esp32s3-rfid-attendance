# Wiring Diagram — ESP32-S3 RFID Attendance System

## Pin Mapping

### ESP32-S3 to MFRC522 (SPI)
| MFRC522 Pin | ESP32-S3 Pin | Keterangan |
|------------|-------------|------------|
| SDA (SS)   | GPIO 10      | SPI Chip Select |
| SCK        | GPIO 12     | SPI Clock |
| MOSI       | GPIO 11     | SPI Data Out |
| MISO       | GPIO 13     | SPI Data In |
| RST        | GPIO 14     | Reset |
| 3.3V       | 3.3V        | Power |
| GND        | GND         | Ground |

### ESP32-S3 to I2C LCD 16x2
| LCD Pin | ESP32-S3 Pin | Keterangan |
|---------|-------------|------------|
| SDA     | GPIO 8     | I2C Data |
| SCL     | GPIO 9     | I2C Clock |
| VCC     | 5V / VIN    | Power (5V) |
| GND     | GND         | Ground |

### ESP32-S3 to Buzzer & LED
| Komponen | Pin | Keterangan |
|----------|-----|------------|
| Buzzer   | GPIO 15 | Active buzzer (HIGH = bunyi) |
| LED Hijau | GPIO 16 | Sukses / IN |
| LED Merah | GPIO 17 | Error / kartu tidak dikenal |

## Diagram Visual

```
                    ┌─────────────────────┐
                    │    ESP32-S3         │
                    │                     │
                    │ GPIO10 ─── SDA (SS) │──┐
                    │ GPIO12 ─── SCK      │  │
                    │ GPIO11 ─── MOSI     │  ├── MFRC522 RFID
                    │ GPIO13 ─── MISO     │  │
                    │ GPIO14 ─── RST      │  │
                    │ 3.3V ───── VCC      │──┘
                    │ GND ────── GND      │
                    │                     │
                    │ GPIO8 ──── SDA      │──┐
                    │ GPIO9 ──── SCL      │  ├── LCD 16x2 I2C
                    │ 5V ─────── VCC      │  │
                    │ GND ────── GND      │──┘
                    │                     │
                    │ GPIO15 ─── Buzzer   │── Buzzer
                    │ GPIO16 ─── LED Hijau│── LED Hijau
                    │ GPIO17 ─── LED Merah│── LED Merah
                    │                     │
                    │ USB ─── Power 5V    │── Power Supply
                    └─────────────────────┘
```

## Power Requirements
- **Input**: 5V DC via USB-C atau adapter eksternal
- **Current**: ~500mA (ESP32-S3 + RFID + LCD + buzzer)
- Jangan gunakan pin 3.3V ESP32 untuk power MFRC522 saat LCD juga menyala — gunakan regulator eksternal jika perlu

## I2C Address
- LCD: 0x27 (default) atau 0x3F (alternatif)
- Gunakan I2C scanner untuk deteksi address jika LCD tidak muncul

## Tips
1. Pastikan MFRC522 terhubung ke 3.3V (bukan 5V) — modul ini 3.3V tolerant
2. LCD I2C backpack bisa pakai 5V (VIN) agar lebih terang
3. Gunakan kabel jumper female-to-female untuk prototyping
4. Tambahkan kapasitor 100uF antara VCC dan GND untuk stabilisasi power
