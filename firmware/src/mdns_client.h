#ifndef MDNS_CLIENT_H
#define MDNS_CLIENT_H
#include <Arduino.h>
#include <ESPmDNS.h>

class MDNSClient {
  public:
    bool discoverPC(String& outIp, int& outPort, int timeoutSec = 10);
};

#endif
