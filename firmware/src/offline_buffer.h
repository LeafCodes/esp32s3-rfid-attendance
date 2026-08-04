#ifndef OFFLINE_BUFFER_H
#define OFFLINE_BUFFER_H
#include <Arduino.h>
#include <LittleFS.h>
#include <ArduinoJson.h>

class OfflineBuffer {
  public:
    bool begin();
    bool saveAttendance(const String& uid, const String& name, const String& status, const String& timestamp);
    int getPendingCount();
    bool getNext(String& outPath, String& outPayload);
    bool removeFile(const String& path);
    bool hasPending();
};

#endif
