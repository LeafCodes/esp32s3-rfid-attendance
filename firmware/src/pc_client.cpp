#include "pc_client.h"
#include "config.h"

void PCClient::setServer(const String& ip, int port) {
    serverUrl = "http://" + ip + ":" + String(port);
}

bool PCClient::sendAttendance(const String& uid, const String& name, const String& status, const String& timestamp, String& outRealStatus, String& outServerName) {
    if (serverUrl.length() == 0) return false;

    HTTPClient http;
    String url = serverUrl + "/api/attendance";

    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", API_KEY);

    JsonDocument doc;
    doc["uid"] = uid;
    doc["name"] = name;
    doc["status"] = status;
    doc["timestamp"] = timestamp;

    String payload;
    serializeJson(doc, payload);

    int httpCode = http.POST(payload);
    bool success = false;

    if (httpCode == 200) {
        String response = http.getString();
        JsonDocument resDoc;
        if (!deserializeJson(resDoc, response)) {
            if (resDoc["inout"].is<String>()) {
                outRealStatus = resDoc["inout"].as<String>();
            } else {
                outRealStatus = status;
            }
            if (resDoc["name"].is<String>()) {
                outServerName = resDoc["name"].as<String>();
            } else {
                outServerName = name;
            }
        }
        success = true;
    } else {
        outRealStatus = status;
        outServerName = name;
    }

    http.end();
    return success;
}

bool PCClient::sendAttendance(const String& uid, const String& name, const String& status, const String& timestamp, String& outRealStatus) {
    String dummyName;
    return sendAttendance(uid, name, status, timestamp, outRealStatus, dummyName);
}

bool PCClient::sendAttendance(const String& uid, const String& name, const String& status, const String& timestamp) {
    String dummyStatus, dummyName;
    return sendAttendance(uid, name, status, timestamp, dummyStatus, dummyName);
}

bool PCClient::syncCards(CardStorage& cardStorage) {
    if (serverUrl.length() == 0) return false;

    HTTPClient http;
    String url = serverUrl + "/api/cards/sync";

    http.begin(url);
    http.addHeader("X-API-Key", API_KEY);
    int httpCode = http.GET();

    if (httpCode == 200) {
        String response = http.getString();
        http.end();

        // Parse JSON and update EEPROM
        JsonDocument doc;
        DeserializationError error = deserializeJson(doc, response);

        if (!error && doc.is<JsonArray>()) {
            cardStorage.clearAll();
            JsonArray arr = doc.as<JsonArray>();
            int count = 0;
            for (JsonObject c : arr) {
                String uid = c["uid"].as<String>();
                String name = c["name"].as<String>();
                if (cardStorage.addCard(uid, name)) {
                    count++;
                }
            }
            Serial.println("PCClient: Synced " + String(count) + " new cards from PC");
            return true;
        }
    }

    http.end();
    return false;
}

bool PCClient::checkEnrollment(String& outEnrollName) {
    if (serverUrl.length() == 0 || !online) return false;

    HTTPClient http;
    String url = serverUrl + "/api/cards/enroll/status";

    http.begin(url);
    http.addHeader("X-API-Key", API_KEY);
    int httpCode = http.GET();

    bool isEnrolling = false;

    if (httpCode == 200) {
        String response = http.getString();
        JsonDocument doc;
        if (!deserializeJson(doc, response)) {
            if (doc["active"].as<bool>()) {
                isEnrolling = true;
                outEnrollName = doc["name"].as<String>();
            }
        }
    }

    http.end();
    return isEnrolling;
}

bool PCClient::isOnline() {
    return online;
}

void PCClient::setOnline(bool status) {
    online = status;
}
