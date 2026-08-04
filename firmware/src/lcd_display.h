#ifndef LCD_DISPLAY_H
#define LCD_DISPLAY_H
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

class LCDDisplay {
  private:
    LiquidCrystal_I2C* lcd;
  public:
    bool begin(byte addr, byte cols, byte rows);
    void showIdle(const String& time);
    void showCard(const String& name, const String& status);
    void showError(const String& msg);
    void showOffline();
};

#endif
