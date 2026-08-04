#include "offline_buffer.h"
#include "config.h"

bool OfflineBuffer::begin() {
    if (!LittleFS.begin()) {
        Serial.println("LittleFS: Mount failed, formatting...");
        LittleFS.format();
        if (!LittleFS.begin()) {
            Serial.println("LittleFS: Fatal error");
            return false;
        }
    }

    // Ensure buffer directory exists
    if (!LittleFS.exists(BUFFER_DIR)) {
        LittleFS.mkdir(BUFFER_DIR);
    }

    Serial.println("LittleFS: Initialized, pending offline records: " + String(getPendingCount()));
    return true;
}

bool OfflineBuffer::saveAttendance(const String& uid, const String& name, const String& status, const String& timestamp) {
    char path[64];
    snprintf(path, sizeof(path), "%s/att_%lu_%s.json", BUFFER_DIR, millis(), uid.c_str());

    JsonDocument doc;
    doc["uid"] = uid;
    doc["name"] = name;
    doc["status"] = status;
    doc["timestamp"] = timestamp;

    File file = LittleFS.open(path, "w");
    if (!file) return false;

    serializeJson(doc, file);
    file.close();

    Serial.println("Buffer: Saved offline record " + String(path));
    return true;
}

int OfflineBuffer::getPendingCount() {
    File dir = LittleFS.open(BUFFER_DIR);
    if (!dir) return 0;

    int count = 0;
    File entry = dir.openNextFile();
    while (entry) {
        if (!entry.isDirectory()) count++;
        entry.close();
        entry = dir.openNextFile();
    }
    dir.close();

    return count;
}

bool OfflineBuffer::hasPending() {
    return getPendingCount() > 0;
}

bool OfflineBuffer::getNext(String& outPath, String& outPayload) {
    File dir = LittleFS.open(BUFFER_DIR);
    if (!dir) return false;

    File entry = dir.openNextFile();
    while (entry) {
        if (!entry.isDirectory()) {
            outPath = String(entry.path());
            if (outPath.length() == 0) {
                outPath = String(BUFFER_DIR) + "/" + String(entry.name());
            }
            outPayload = entry.readString();
            entry.close();
            dir.close();
            return true;
        }
        entry.close();
        entry = dir.openNextFile();
    }

    dir.close();
    return false;
}

bool OfflineBuffer::removeFile(const String& path) {
    return LittleFS.remove(path);
}
