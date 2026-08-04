#include "lcd_display.h"
#include "config.h"
#include <Wire.h>

bool LCDDisplay::begin(byte addr, byte cols, byte rows) {
    Wire.begin(LCD_SDA, LCD_SCL);
    delay(100);

    byte foundAddr = addr;
    Serial.println("I2C: Scanning bus (SDA=" + String(LCD_SDA) + ", SCL=" + String(LCD_SCL) + ")...");
    for (byte i = 8; i < 120; i++) {
        Wire.beginTransmission(i);
        if (Wire.endTransmission() == 0) {
            Serial.println("I2C: Found device at 0x" + String(i, HEX));
            foundAddr = i;
            break;
        }
    }

    lcd = new LiquidCrystal_I2C(foundAddr, cols, rows);
    lcd->init();
    lcd->backlight();
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("RFID Attendance");
    lcd->setCursor(0, 1);
    lcd->print("System Ready...");
    Serial.println("LCD: Initialized at 0x" + String(foundAddr, HEX));
    return true;
}

void LCDDisplay::showIdle(const String& timeStr) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("Siap Absen");
    lcd->setCursor(0, 1);
    lcd->print(timeStr);
}

void LCDDisplay::showCard(const String& name, const String& status) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print(name.substring(0, LCD_COLS));
    lcd->setCursor(0, 1);
    if (status == "IN") {
        lcd->print(">> MASUK");
    } else if (status == "TERDAFTAR" || status == "REGISTERED") {
        lcd->print(">> TERDAFTAR");
    } else {
        lcd->print("<< KELUAR");
    }
}

void LCDDisplay::showError(const String& msg) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("ERROR");
    lcd->setCursor(0, 1);
    lcd->print(msg.substring(0, LCD_COLS));
}

void LCDDisplay::showOffline() {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("Mode Offline");
    lcd->setCursor(0, 1);
    lcd->print("Data tersimpan");
}
