#include "card_storage.h"
#include "config.h"

#define EEPROM_MAGIC 0x43415244  // "CARD"

static int getAddr(int index) {
    return 4 + index * sizeof(CardEntry);
}

bool CardStorage::begin() {
    if (!EEPROM.begin(EEPROM_SIZE)) {
        Serial.println("EEPROM: Init failed");
        return false;
    }

    uint32_t magic = 0;
    EEPROM.get(0, magic);

    if (magic != EEPROM_MAGIC) {
        Serial.println("EEPROM: Formatting uninitialized storage...");
        for (int i = 0; i < EEPROM_SIZE; i++) {
            EEPROM.write(i, 0);
        }
        magic = EEPROM_MAGIC;
        EEPROM.put(0, magic);
        EEPROM.commit();
        Serial.println("EEPROM: Formatting complete!");
    }

    Serial.println("EEPROM: Initialized, " + String(getCount()) + " cards loaded");
    return true;
}

bool CardStorage::addCard(const String& uid, const String& name) {
    if (isRegistered(uid)) return false;

    for (int i = 0; i < MAX_CARDS; i++) {
        CardEntry entry;
        int addr = getAddr(i);
        EEPROM.get(addr, entry);

        if (!entry.active) {
            memset(&entry, 0, sizeof(CardEntry));
            uid.toCharArray(entry.uid, 9);
            name.toCharArray(entry.name, 32);
            entry.active = true;
            EEPROM.put(addr, entry);
            EEPROM.commit();
            Serial.println("EEPROM: Added card " + uid + " - " + name);
            return true;
        }
    }
    Serial.println("EEPROM: Storage full, cannot add " + uid);
    return false;
}

bool CardStorage::removeCard(const String& uid) {
    for (int i = 0; i < MAX_CARDS; i++) {
        CardEntry entry;
        int addr = getAddr(i);
        EEPROM.get(addr, entry);

        if (entry.active && uid.equalsIgnoreCase(String(entry.uid))) {
            entry.active = false;
            EEPROM.put(addr, entry);
            EEPROM.commit();
            Serial.println("EEPROM: Removed card " + uid);
            return true;
        }
    }
    return false;
}

bool CardStorage::isRegistered(const String& uid) {
    for (int i = 0; i < MAX_CARDS; i++) {
        CardEntry entry;
        EEPROM.get(getAddr(i), entry);
        if (entry.active && uid.equalsIgnoreCase(String(entry.uid))) {
            return true;
        }
    }
    return false;
}

String CardStorage::getCardName(const String& uid) {
    for (int i = 0; i < MAX_CARDS; i++) {
        CardEntry entry;
        EEPROM.get(getAddr(i), entry);
        if (entry.active && uid.equalsIgnoreCase(String(entry.uid))) {
            return String(entry.name);
        }
    }
    return "";
}

int CardStorage::getCount() {
    int count = 0;
    for (int i = 0; i < MAX_CARDS; i++) {
        CardEntry entry;
        EEPROM.get(getAddr(i), entry);
        if (entry.active) count++;
    }
    return count;
}

void CardStorage::clearAll() {
    for (int i = 0; i < MAX_CARDS; i++) {
        CardEntry entry;
        int addr = getAddr(i);
        EEPROM.get(addr, entry);
        if (entry.active) {
            entry.active = false;
            EEPROM.put(addr, entry);
        }
    }
    EEPROM.commit();
}

void CardStorage::listAll() {
    Serial.println("=== Registered Cards (" + String(getCount()) + ") ===");
    for (int i = 0; i < MAX_CARDS; i++) {
        CardEntry entry;
        EEPROM.get(getAddr(i), entry);
        if (entry.active) {
            Serial.println("  [" + String(i) + "] " + String(entry.uid) + " - " + String(entry.name));
        }
    }
}
