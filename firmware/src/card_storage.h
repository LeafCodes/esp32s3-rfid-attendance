#ifndef CARD_STORAGE_H
#define CARD_STORAGE_H
#include <Arduino.h>
#include <EEPROM.h>

struct CardEntry {
  char uid[9];
  char name[32];
  bool active;
};

class CardStorage {
  public:
    bool begin();
    bool addCard(const String& uid, const String& name);
    bool removeCard(const String& uid);
    bool isRegistered(const String& uid);
    String getCardName(const String& uid);
    int getCount();
    void clearAll();
    void listAll();
};

#endif
