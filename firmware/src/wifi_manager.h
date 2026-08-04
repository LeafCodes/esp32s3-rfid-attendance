#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H
#include <Arduino.h>
#include <WiFiManager.h>

class WiFiManagerHandler {
  private:
    WiFiManager wm;
  public:
    bool begin();
    bool isConnected();
    void resetSettings();
    String getSSID();
};

#endif
