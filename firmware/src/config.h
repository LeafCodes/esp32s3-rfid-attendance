#ifndef CONFIG_H
#define CONFIG_H

// RFID MFRC522 pin (SPI - ESP32-S3)
#define SPI_SCK   12
#define SPI_MISO  13
#define SPI_MOSI  11
#define RFID_SS   10
#define RFID_RST  14

// I2C LCD (ESP32-S3)
#define LCD_SDA   8
#define LCD_SCL   9
#define LCD_ADDR  0x3F
#define LCD_COLS  16
#define LCD_ROWS  2

// Buzzer & LED (ESP32-S3)
#define BUZZER_PIN  15
#define LED_GREEN   16
#define LED_RED     17

// NTP
#define NTP_SERVER     "pool.ntp.org"
#define GMT_OFFSET     7  // WIB (UTC+7)

// PC Server
#define PC_PORT        8000
#define MDNS_SERVICE   "attendance"
#define API_KEY        "absensi_secret_key_2026"

// EEPROM
#define EEPROM_SIZE    4096
#define MAX_CARDS      90

// LittleFS
#define BUFFER_DIR     "/buffer"
#define INDEX_FILE     "/buffer/index.json"

// Debounce
#define SCAN_COOLDOWN  3000  // ms

#endif
