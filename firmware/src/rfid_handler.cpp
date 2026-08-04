#include "rfid_handler.h"
#include "config.h"

bool RFIDHandler::begin(byte ssPin, byte rstPin) {
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, ssPin);
    mfrc522 = new MFRC522(ssPin, rstPin);
    mfrc522->PCD_Init();
    delay(50);

    // Print MFRC522 software version
    byte v = mfrc522->PCD_ReadRegister(mfrc522->VersionReg);
    Serial.println("RFID: MFRC522 Version = 0x" + String(v, HEX));

    // Re-init & turn antenna on
    mfrc522->PCD_Init();
    mfrc522->PCD_AntennaOn();

    Serial.println("RFID: Initialized (SS=" + String(ssPin) + ", RST=" + String(rstPin) + ")");
    return true;
}

bool RFIDHandler::isCardPresent() {
    if (!mfrc522->PICC_IsNewCardPresent()) {
        return false;
    }
    return mfrc522->PICC_ReadCardSerial();
}

String RFIDHandler::readUID() {
    String uid = "";
    for (byte i = 0; i < mfrc522->uid.size; i++) {
        if (mfrc522->uid.uidByte[i] < 0x10) uid += "0";
        uid += String(mfrc522->uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    halt();
    return uid;
}

void RFIDHandler::halt() {
    mfrc522->PICC_HaltA();
    mfrc522->PCD_StopCrypto1();
}
