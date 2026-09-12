# 🛠️ Desain Perangkat Keras & Panduan Manufaktur PCB

Direktori ini berisi seluruh berkas desain perangkat keras (*hardware design files*) sistem presensi RFID berbasis mikrokontroler **ESP32-S3** yang dirancang menggunakan perangkat lunak **KiCad 8.0**.

---

## 📑 Daftar Isi
1. [Struktur & Deskripsi Berkas](#1-struktur--deskripsi-berkas)
2. [Spesifikasi Teknis Papan PCB](#2-spesifikasi-teknis-papan-pcb)
3. [Daftar Komponen Lengkap (Bill of Materials / BOM)](#3-daftar-komponen-lengkap-bill-of-materials--bom)
4. [Opsi Fabrikasi Papan PCB](#4-opsi-fabrikasi-papan-pcb)
   - [Opsi A: Fabrikasi Profesional Industri (JLCPCB / PCBWay)](#opsi-a-fabrikasi-profesional-industri-jlcpcb--pcbway)
   - [Opsi B: Pembuatan Mandiri / DIY (Metode Toner Transfer & Etsa)](#opsi-b-pembuatan-mandiri--diy-metode-toner-transfer--etsa)
5. [Prinsip Desain & Rekayasa Sirkuit (Design Considerations)](#5-prinsip-desain--rekayasa-sirkuit-design-considerations)

---

## 1. Struktur & Deskripsi Berkas

| Berkas | Jenis / Format | Deskripsi & Kegunaan |
|---|---|---|
| `rfid-attendance.kicad_pro` | Project KiCad | Berkas utama proyek KiCad 8.0 |
| `rfid-attendance.kicad_sch` | Skematik Elektronika | Diagram skema rangkaian terpadu sistem |
| `rfid-attendance.kicad_pcb` | Layout Jalur PCB | Penataan komponen dan jalur tembaga (*routing*) |
| `rfid-attendance-schematic.svg` | Gambar Vektor SVG | **Skematik siap cetak** — buka langsung di browser, tekan `Ctrl + P` |
| `rfid-attendance-pcb.svg` | Gambar Vektor SVG | **Jalur PCB skala 1:1 siap cetak** untuk etsa mandiri |
| `sym-lib-table` & `fp-lib-table` | Tabel Library | Konfigurasi pustaka simbol dan footprint KiCad |

---

## 2. Spesifikasi Teknis Papan PCB

Papan dirancang sesuai standar fabrikasi industri 2-layer (*double-sided*) yang ekonomis dan mudah diproduksi massal:

| Parameter Desain | Nilai Spesifikasi | Keterangan |
|---|---|---|
| **Dimensi Fisik** | 100 mm × 80 mm | Pas dengan ukuran box casing 3D print |
| **Jumlah Lapisan (*Layers*)** | 2 Layer (Top & Bottom) | Distribusi sinyal di Top, Ground plane di Bottom |
| **Material Substrat** | FR-4 Standard | Tahan panas dan memiliki isolasi tinggi |
| **Ketebalan Papan** | 1.6 mm | Standar ketebalan mekanikal yang kokoh |
| **Ketebalan Tembaga (*Copper*)** | 1 oz (35 µm) | Kapasitas arus memadai untuk modul RF |
| **Solder Mask** | Hijau / Matte Black | Melindungi jalur tembaga dari oksidasi |
| **Silkscreen** | Putih (White) | Label teks indikasi pin dan orientasi komponen |
| **Lebar Jalur Sinyal (*Trace*)** | Min. 0.25 mm (10 mil) | Untuk jalur komunikasi SPI dan I2C |
| **Lebar Jalur Daya (*Power*)** | Min. 0.60 mm – 1.0 mm | Menjamin drop tegangan minimal pada jalur 5V/3.3V |
| **Jarak Antar Jalur (*Clearance*)** | Min. 0.20 mm (8 mil) | Menghindari risiko korsleting pada proses etsa |
| **Lubang Baut (*Mounting Hole*)** | 4× Lubang M3 (Ø 3.2 mm) | Di keempat sudut untuk penguncian ke enclosure |

---

## 3. Daftar Komponen Lengkap (Bill of Materials / BOM)

Komponen dirancang dominan menggunakan tipe **Through-Hole Technology (THT)** agar sangat mudah disolder secara manual oleh teknisi, mahasiswa, maupun hobiis:

| No | Nama Komponen | Referensi Skematik | Qty | Tipe Paket (Package) | Keterangan Tambahan |
|---|---|---|---|---|---|
| 1 | **ESP32-S3 DevKitC-1** | U1 | 1 | Modul Soket 2×15 Pin (2.54mm) | Disarankan menggunakan female header |
| 2 | **Modul RFID MFRC522** | U2 | 1 | Modul Soket 1×8 Pin (2.54mm) | Dipasang tegak/sejajar pembaca kartu |
| 3 | **Modul LCD 16x2 I2C** | LCD1 | 1 | Header 1×4 Pin (2.54mm) | Koneksi VCC, GND, SDA, SCL |
| 4 | **Buzzer Aktif 5V** | BZ1 | 1 | THT Pitch 7.6mm | Indikator suara |
| 5 | **LED Indikator Hijau (5mm)** | D1 | 1 | Radial THT 5mm | Status Berhasil / Masuk |
| 6 | **LED Indikator Merah (5mm)** | D2 | 1 | Radial THT 5mm | Status Gagal / Error |
| 7 | **Resistor 220Ω 1/4W** | R1, R2, R3 | 3 | Aksial THT | Pembatas arus LED & Buzzer |
| 8 | **Resistor 4.7kΩ 1/4W** | R4, R5 | 2 | Aksial THT | Resistor Pull-up eksternal I2C (Opsional) |
| 9 | **Kapasitor Elektrolit 100µF 16V** | C1, C2 | 2 | Radial THT | Decoupling filter pada rel 5V dan 3.3V |
| 10 | **Pin Header Male/Female 2.54mm** | J1 - J4 | 4 | Strip Header | Konektor modular |

---

## 4. Opsi Fabrikasi Papan PCB

### Opsi A: Fabrikasi Profesional Industri (JLCPCB / PCBWay)
Metode ini menghasilkan papan dengan kualitas pabrikan lengkap dengan *through-hole plating*, *solder mask*, dan *silkscreen*:

1. Buka berkas `rfid-attendance.kicad_pcb` di **KiCad PCB Editor**.
2. Masuk ke menu **File → Plot**.
3. Centang layer yang diperlukan:
   - `F.Cu` (Top Copper)
   - `B.Cu` (Bottom Copper)
   - `F.Paste` & `B.Paste` (Jika menggunakan SMD stencil)
   - `F.Silkscreen` & `B.Silkscreen`
   - `F.Mask` & `B.Mask`
   - `Edge.Cuts` (Garis batas tepi papan PCB)
4. Klik tombol **Generate Drill Files (.drl)**.
5. Kumpulkan semua berkas `.gbr` dan `.drl` ke dalam satu berkas `.zip`.
6. Unggah berkas `.zip` ke layanan fabrikasi (misalnya [JLCPCB](https://jlcpcb.com) atau [PCBWay](https://www.pcbway.com)).
7. Pilih spesifikasi: `2 Layers`, `100x80mm`, `Thickness 1.6mm`, warna solder mask sesuai selera.

---

### Opsi B: Pembuatan Mandiri / DIY (Metode Toner Transfer & Etsa)
Jika Anda ingin mencetak PCB sendiri di laboratorium atau bengkel kerja:

1. Buka berkas **`rfid-attendance-pcb.svg`** menggunakan browser web modern (Google Chrome / Mozilla Firefox / MS Edge).
2. Tekan kombinasi tombol **`Ctrl + P`** untuk membuka dialog pencetakan.
3. Atur konfigurasi printer:
   - **Ukuran Kertas**: A4
   - **Skala (*Scale*)**: Wajib **100% (Actual Size)** — *Jangan pilih "Fit to Page" agar dimensi kaki IC tidak meleset*.
4. Cetak ke kertas kalkir / kertas transfer (*glossy paper*) menggunakan **Printer Laser (Toner Hitam)**.
5. Tempelkan toner ke papan tembaga polos menggunakan setrika panas (*heat transfer*), lalu larutkan tembaga berlebih menggunakan cairan ferric chloride ($FeCl_3$) atau H2O2 + HCl.
6. Bor lubang pin komponen menggunakan mata bor mini berukuran 0.8 mm dan 1.0 mm.

---

## 5. Prinsip Desain & Rekayasa Sirkuit (Design Considerations)

1. **Modularitas Komponen (Soket Female Header):**  
   Papan dirancang menggunakan header modular sehingga modul mikrokontroler ESP32-S3 dan MFRC522 dapat dilepas-pasang dengan mudah tanpa perlu menyolder ulang saat proses servis atau pergantian komponen.
2. **Ground Plane (Copper Pour):**  
   Seluruh area kosong pada lapisan bawah (*Bottom Layer*) dihubungkan ke sinyal GND (*Ground Pour*). Hal ini berfungsi sebagai pelindung interferensi elektromagnetik (*EMI shielding*) serta meminimalkan impedansi jalur balik arus daya.
3. **Peredaman Lonjakan Arus (Decoupling Capacitor):**  
   Kapasitor 100µF diposisikan sedekat mungkin dengan pin input daya modul RFID untuk menjaga kestabilan voltase saat medan antena 13.56 MHz memancarkan daya ke kartu transponder.
