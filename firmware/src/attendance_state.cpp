#include "attendance_state.h"
#include "config.h"

AttendanceState::AttendanceState() {
    state = STATE_INIT;
    lastCardScan = 0;
    lastUID = "";
}

void AttendanceState::setState(DeviceState s) {
    state = s;
    Serial.println("State: " + getStateName());
}

DeviceState AttendanceState::getState() {
    return state;
}

String AttendanceState::getStateName() {
    switch (state) {
        case STATE_INIT: return "INIT";
        case STATE_WIFI_CONNECT: return "WIFI_CONNECT";
        case STATE_WIFI_PORTAL: return "WIFI_PORTAL";
        case STATE_DISCOVER_PC: return "DISCOVER_PC";
        case STATE_IDLE: return "IDLE";
        case STATE_CARD_DETECTED: return "CARD_DETECTED";
        case STATE_SENDING: return "SENDING";
        case STATE_OFFLINE_BUFFER: return "OFFLINE_BUFFER";
        case STATE_ERROR: return "ERROR";
        default: return "UNKNOWN";
    }
}

bool AttendanceState::canScanCard() {
    if (state != STATE_IDLE) return false;
    if (millis() - lastCardScan < SCAN_COOLDOWN) return false;
    return true;
}

void AttendanceState::markCardScanned(const String& uid) {
    lastCardScan = millis();
    lastUID = uid;
}

String AttendanceState::getLastUID() {
    return lastUID;
}
