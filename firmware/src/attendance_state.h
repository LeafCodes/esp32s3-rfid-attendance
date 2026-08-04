#ifndef ATTENDANCE_STATE_H
#define ATTENDANCE_STATE_H
#include <Arduino.h>

enum DeviceState {
  STATE_INIT,
  STATE_WIFI_CONNECT,
  STATE_WIFI_PORTAL,
  STATE_DISCOVER_PC,
  STATE_IDLE,
  STATE_CARD_DETECTED,
  STATE_SENDING,
  STATE_OFFLINE_BUFFER,
  STATE_ERROR
};

class AttendanceState {
  private:
    DeviceState state;
    unsigned long lastCardScan;
    String lastUID;
  public:
    AttendanceState();
    void setState(DeviceState s);
    DeviceState getState();
    String getStateName();
    bool canScanCard();
    void markCardScanned(const String& uid);
    String getLastUID();
};

#endif
