#include <Arduino.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

#include "config.h"
#include "wifi_manager.h"
#include "rfid_handler.h"
#include "card_storage.h"
#include "lcd_display.h"
#include "led_buzzer.h"
#include "mdns_client.h"
#include "pc_client.h"
#include "offline_buffer.h"
#include "attendance_state.h"

// Global objects
WiFiManagerHandler wifiManager;
RFIDHandler rfidHandler;
CardStorage cardStorage;
LCDDisplay lcdDisplay;
Feedback feedback;
MDNSClient mdnsClient;
PCClient pcClient;
OfflineBuffer offlineBuffer;
AttendanceState state;

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, NTP_SERVER, GMT_OFFSET * 3600, 60000);

unsigned long lastMdnsAttempt = 0;
unsigned long lastHealthCheck = 0;
unsigned long lastNtpSync = 0;
unsigned long lastDisplayUpdate = 0;
unsigned long lastOfflineSync = 0;

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n\n=== ESP32-S3 RFID Attendance System ===");

    // Initialize components
    state.setState(STATE_INIT);
    lcdDisplay.begin(LCD_ADDR, LCD_COLS, LCD_ROWS);
    feedback.begin(BUZZER_PIN, LED_GREEN, LED_RED);
    cardStorage.begin();
    offlineBuffer.begin();
    rfidHandler.begin(RFID_SS, RFID_RST);

    // Connect WiFi
    state.setState(STATE_WIFI_CONNECT);
    lcdDisplay.showIdle("WiFi...");
    
    if (wifiManager.begin()) {
        state.setState(STATE_IDLE);
        timeClient.begin();
        timeClient.update();
        feedback.success();
    } else {
        state.setState(STATE_WIFI_PORTAL);
        lcdDisplay.showError("WiFi Portal");
    }

    Serial.println("=== System Ready ===\n");
}

void loop() {
    unsigned long now = millis();

    // === WiFi Portal Mode ===
    if (state.getState() == STATE_WIFI_PORTAL) {
        if (wifiManager.isConnected()) {
            state.setState(STATE_IDLE);
            timeClient.begin();
            timeClient.update();
            feedback.success();
        }
        delay(100);
        return;
    }

    // === NTP Sync ===
    timeClient.update();

    // === mDNS Discovery (every 30s if no PC) ===
    if (!pcClient.isOnline() && now - lastMdnsAttempt > 30000) {
        lastMdnsAttempt = now;
        state.setState(STATE_DISCOVER_PC);
        String pcIp;
        int pcPort;
        if (mdnsClient.discoverPC(pcIp, pcPort)) {
            pcClient.setServer(pcIp, pcPort);
            pcClient.setOnline(true);
            Serial.println("PC found: " + pcIp + ":" + String(pcPort));
            pcClient.syncCards(cardStorage);
            feedback.success();
        }
        state.setState(STATE_IDLE);
    }

    // === Sync Cards & Health Check every 10s when online ===
    if (pcClient.isOnline() && now - lastHealthCheck > 10000) {
        lastHealthCheck = now;
        pcClient.syncCards(cardStorage);
    }

    // === Idle Display ===
    if (state.getState() == STATE_IDLE && now - lastDisplayUpdate > 1000) {
        lastDisplayUpdate = now;
        String timeStr = timeClient.isTimeSet() ? timeClient.getFormattedTime() : timeClient.getFormattedTime();
        lcdDisplay.showIdle(timeStr);
    }

    // === Offline Buffer Sync (every 5s when online) ===
    if (offlineBuffer.hasPending() && pcClient.isOnline() && now - lastOfflineSync > 5000) {
        lastOfflineSync = now;
        String path, payload;
        if (offlineBuffer.getNext(path, payload)) {
            JsonDocument doc;
            DeserializationError err = deserializeJson(doc, payload);
            if (!err) {
                String uid = doc["uid"].as<String>();
                String name = doc["name"].as<String>();
                String status = doc["status"].as<String>();
                String timestamp = doc["timestamp"].as<String>();

                if (pcClient.sendAttendance(uid, name, status, timestamp)) {
                    offlineBuffer.removeFile(path);
                    Serial.println("Buffer: Synced offline record " + path + " (Remaining: " + String(offlineBuffer.getPendingCount()) + ")");
                }
            } else {
                offlineBuffer.removeFile(path);
            }
        }
    }

    // === RFID Card Detection ===
    if (state.getState() == STATE_IDLE && rfidHandler.isCardPresent()) {
        String uid = rfidHandler.readUID();
        Serial.println("Card Scanned UID: " + uid);

        if (!state.canScanCard()) {
            return;
        }
        state.markCardScanned(uid);

        state.setState(STATE_CARD_DETECTED);
        String name = cardStorage.isRegistered(uid) ? cardStorage.getCardName(uid) : "Pengguna";
        String timestamp = timeClient.isTimeSet() ? timeClient.getFormattedTime() : "";

        if (pcClient.isOnline()) {
            state.setState(STATE_SENDING);
            String realStatus = "IN";
            String serverName = name;
            if (pcClient.sendAttendance(uid, name, "AUTO", timestamp, realStatus, serverName)) {
                // Success! Server recognized card or auto-enrolled it in Enrollment mode
                pcClient.syncCards(cardStorage);
                lcdDisplay.showCard(serverName, realStatus);
                feedback.success();
                Serial.println("Attendance/Enrollment sent: " + serverName + " -> " + realStatus);
            } else {
                // Card is unknown and not in enrollment mode
                lcdDisplay.showError("Unknown Card");
                feedback.error();
            }
        } else {
            // Offline mode
            if (cardStorage.isRegistered(uid)) {
                lcdDisplay.showCard(name, "IN");
                offlineBuffer.saveAttendance(uid, name, "IN", timestamp);
                lcdDisplay.showOffline();
                feedback.success();
            } else {
                lcdDisplay.showError("Unknown Card");
                feedback.error();
            }
        }

        state.setState(STATE_IDLE);
        delay(2000);
    }

    delay(50);
}
