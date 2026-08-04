#ifndef LED_BUZZER_H
#define LED_BUZZER_H
#include <Arduino.h>

class Feedback {
  private:
    byte buzzerPin, greenPin, redPin;
  public:
    void begin(byte buzzer, byte green, byte red);
    void success();
    void error();
    void warning();
};

#endif
