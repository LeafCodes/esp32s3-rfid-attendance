# 🔌 Panduan Pengkabelan & Pinout Perangkat Keras (Hardware Wiring Guide)

Dokumen ini memuat detail koneksi elektrik antara modul mikrokontroler **ESP32-S3 DevKitC-1**, pembaca kartu **RFID MFRC522**, layar penampil **LCD 16x2 I2C**, serta indikator **Buzzer & Dual LED**.

---

## 📑 Daftar Isi
1. [Tabel Pemetaan Pin Lengkap (Pinout Matrix)](#1-tabel-pemetaan-pin-lengkap-pinout-matrix)
2. [Diagram Skematik Koneksi Antar Modul](#2-diagram-skematik-koneksi-antar-modul)
3. [Perhatian Khusus Tegangan & Kelistrikan (Safety Warnings)](#3-perhatian-khusus-tegangan--kelistrikan-safety-warnings)
4. [Cara Kustomisasi Pin pada Firmware](#4-cara-kustomisasi-pin-pada-firmware)
5. [Tips Prototyping & Kestabilan Sinyal](#5-tips-prototyping--kestabilan-sinyal)

---

## 1. Tabel Pemetaan Pin Lengkap (Pinout Matrix)

### A. Modul RFID MFRC522 (Jalur Bus SPI)
Modul pembaca RFID beroperasi menggunakan komunikasi serial SPI berkecepatan tinggi:

| Pin MFRC522 | Pin ESP32-S3 | Tipe Sinyal | Keterangan Fungsi |
|---|---|---|---|
| **SDA / SS** | **GPIO 10** | Output ESP32 | *Chip Select (Slave Select)* SPI |
| **SCK** | **GPIO 12** | Output ESP32 | *Serial Clock* SPI |
| **MOSI** | **GPIO 11** | Output ESP32 | *Master Out Slave In* (Kirim data ke reader) |
| **MISO** | **GPIO 13** | Input ESP32 | *Master In Slave Out* (Terima data dari reader) |
| **IRQ** | *Tidak Dihubungkan* | - | Interupsi perangkat keras (tidak digunakan) |
| **RST** | **GPIO 14** | Output ESP32 | *Hardware Reset* modul RFID |
| **3.3V** | **3V3** | Power | **Wajib 3.3V DC** (Jangan gunakan pin 5V!) |
| **GND** | **GND** | Ground | Ground bersama (*Common Ground*) |

---

### B. Modul Display LCD 16x2 (Jalur Bus I2C)
Layar menggunakan modul konverter I2C backpack (PCF8574) sehingga hanya membutuhkan 2 pin data:

| Pin Modul I2C LCD | Pin ESP32-S3 | Tipe Sinyal | Keterangan Fungsi |
|---|---|---|---|
| **SDA** | **GPIO 8** | Bidirectional | *Serial Data Line* I2C |
| **SCL** | **GPIO 9** | Output ESP32 | *Serial Clock Line* I2C |
| **VCC** | **5V / VIN** | Power | Suplai daya 5V agar lampu backlight & teks kontras |
| **GND** | **GND** | Ground | Ground bersama |

> ℹ️ **Alamat I2C Default:** `0x27` (modul chip PCF8574T) atau `0x3F` (modul chip PCF8574AT).

---

### C. Modul Audio-Visual (Buzzer & LED)

| Komponen | Pin ESP32-S3 | Komponen Pendukung | Indikasi Status |
|---|---|---|---|
| **Active Buzzer 5V** | **GPIO 15** | Resistor 220Ω / Transistor Driver | Bip pendek = Sukses, Bip panjang = Ditolak |
| **LED Indikator Hijau** | **GPIO 16** | Resistor 220Ω (seri ke Anoda) | Menyala saat presensi berhasil diproses |
| **LED Indikator Merah** | **GPIO 17** | Resistor 220Ω (seri ke Anoda) | Menyala saat kartu tidak dikenal / error |

---

## 2. Diagram Skematik Koneksi Antar Modul

```text
                               ┌──────────────────────────┐
                               │   ESP32-S3 DevKitC-1     │
                               │                          │
        ┌──────────────┐       │                          │
        │   MFRC522    │       │                          │
        │  RFID Module │       │                          │
        │              │       │                          │
        │          SDA ├───────┤ GPIO 10                  │
        │          SCK ├───────┤ GPIO 12                  │
        │         MOSI ├───────┤ GPIO 11                  │
        │         MISO ├───────┤ GPIO 13                  │
        │          RST ├───────┤ GPIO 14                  │
        │         3.3V ├───────┤ 3V3 (3.3V Rail)          │
        │          GND ├───────┤ GND                      │
        └──────────────┘       │                          │
                               │                          │
        ┌──────────────┐       │                          │
        │   LCD 16x2   │       │                          │
        │ I2C Backpack │       │                          │
        │              │       │                          │
        │          SDA ├───────┤ GPIO 8                   │
        │          SCL ├───────┤ GPIO 9                   │
        │          VCC ├───────┤ 5V (VIN / VBUS Rail)     │
        │          GND ├───────┤ GND                      │
        └──────────────┘       │                          │
                               │                          │
        ┌──────────────┐       │                          │
        │ Buzzer & LED │       │                          │
        │              │       │                          │
        │   Active Buzz├───────┤ GPIO 15                  │
        │    LED Hijau ├───────┤ GPIO 16 (via Resistor)   │
        │    LED Merah ├───────┤ GPIO 17 (via Resistor)   │
        │          GND ├───────┤ GND                      │
        └──────────────┘       │                          │
                               │                          │
                               │ USB-C ──── [Power In 5V] │
                               └──────────────────────────┘
```

---

## 3. Perhatian Khusus Tegangan & Kelistrikan (Safety Warnings)

> [!CAUTION]
> **BAHAYA TEGANGAN TINGGI PADA MFRC522:**  
> Chip NXP MFRC522 **TIDAK toleran terhadap tegangan 5V**. Selalu hubungkan pin VCC MFRC522 ke pin **3.3V** ESP32. Menghubungkan VCC MFRC522 ke pin 5V akan merusak chip RFID reader secara permanen.

> [!NOTE]
> **TEGANGAN OPTIMAL UNTUK LCD I2C BACKPACK:**  
> Sebagian besar layar LCD 16x2 HD44780 membutuhkan suplai **5V (VIN)** agar karakter tulisan terlihat jelas dan kontras. Meskipun ESP32 beroperasi pada level logika 3.3V, jalur I2C pada GPIO 8 & 9 tetap aman digunakan karena pin I2C bersifat *open-drain* dengan pull-up internal.

> [!TIP]
> **STABILISASI DAYA & DECOUPLING CAPACITOR:**  
> Modul RF (seperti WiFi pada ESP32 dan medan elektromagnetik pada MFRC522) dapat menarik lonjakan arus sesaat (*transient peak*) hingga 400–500mA. Pasanglah kapasitor elektrolit **100µF (16V)** paralel antara jalur 3.3V dan GND dekat header RFID untuk mencegah mikrokontroler mendadak restart (*brownout reset*).

---

## 4. Cara Kustomisasi Pin pada Firmware

Semua konfigurasi pemetaan pin telah diisolasi dalam satu berkas konfigurasi di:  
👉 **`firmware/src/config.h`**

Jika Anda menggunakan jenis papan pengembangan lain (misalnya ESP32 WROOM-32 standar) atau ingin memindahkan pin karena kebutuhan layout PCB yang berbeda, Anda cukup menyunting baris berikut:

```cpp
// Jalur SPI untuk RFID MFRC522
#define RFID_SS_PIN    10
#define RFID_RST_PIN   14
#define SPI_SCK_PIN    12
#define SPI_MOSI_PIN   11
#define SPI_MISO_PIN   13

// Jalur I2C untuk LCD 16x2
#define LCD_SDA_PIN    8
#define LCD_SCL_PIN    9
#define LCD_I2C_ADDR   0x27

// Indikator Buzzer & LED
#define BUZZER_PIN     15
#define LED_GREEN_PIN  16
#define LED_RED_PIN    17
```

---

## 5. Tips Prototyping & Kestabilan Sinyal

1. **Jarak Kabel SPI:** Usahakan kabel jumper jalur SPI (MISO, MOSI, SCK, SS) berukuran tidak lebih dari 15 cm untuk mencegah *noise* dan penurunan kualitas sinyal frekuensi tinggi.
2. **Resistor Pembatas Arus LED:** Wajib memasang resistor 220Ω secara seri pada pin Anoda (+) LED Merah dan Hijau agar tidak membebani pin GPIO ESP32 secara berlebihan.
3. **Penyolderan Header:** Pastikan seluruh pin header pada modul MFRC522 disolder dengan timah yang rapi dan tidak saling bersentuhan (*short circuit*).
