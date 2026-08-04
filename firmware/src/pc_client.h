#ifndef PC_CLIENT_H
#define PC_CLIENT_H
#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "card_storage.h"

class PCClient {
  private:
    String serverUrl;
    bool online;
  public:
    void setServer(const String& ip, int port);
    bool sendAttendance(const String& uid, const String& name, const String& status, const String& timestamp, String& outRealStatus, String& outServerName);
    bool sendAttendance(const String& uid, const String& name, const String& status, const String& timestamp, String& outRealStatus);
    bool sendAttendance(const String& uid, const String& name, const String& status, const String& timestamp);
    bool syncCards(CardStorage& cardStorage);
    bool checkEnrollment(String& outEnrollName);
    bool isOnline();
    void setOnline(bool status);
};

#endif
