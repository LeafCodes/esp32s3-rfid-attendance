#ifndef RFID_HANDLER_H
#define RFID_HANDLER_H
#include <Arduino.h>
#include <MFRC522.h>
#include <SPI.h>

class RFIDHandler {
  private:
    MFRC522* mfrc522;
  public:
    bool begin(byte ssPin, byte rstPin);
    bool isCardPresent();
    String readUID();
    void halt();
};

#endif
