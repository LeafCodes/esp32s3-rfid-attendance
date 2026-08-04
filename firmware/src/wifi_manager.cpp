#include "wifi_manager.h"
#include "config.h"

bool WiFiManagerHandler::begin() {
    wm.setDebugOutput(true);
    wm.setConnectTimeout(30);
    wm.setConfigPortalTimeout(180);
    wm.setWiFiAutoReconnect(true);
    wm.setCaptivePortalEnable(true);

    String apName = "Absensi-" + String((uint32_t)ESP.getEfuseMac(), HEX).substring(0, 4);
    apName.toUpperCase();

    Serial.println("WiFiManager: Starting with AP " + apName);
    bool connected = wm.autoConnect(apName.c_str());

    if (connected) {
        Serial.println("WiFiManager: Connected to " + WiFi.SSID());
        Serial.println("WiFiManager: IP " + WiFi.localIP().toString());
    } else {
        Serial.println("WiFiManager: Failed to connect, portal active");
    }

    return connected;
}

bool WiFiManagerHandler::isConnected() {
    return WiFi.status() == WL_CONNECTED;
}

void WiFiManagerHandler::resetSettings() {
    wm.resetSettings();
    Serial.println("WiFiManager: Settings reset");
}

String WiFiManagerHandler::getSSID() {
    return WiFi.SSID();
}
