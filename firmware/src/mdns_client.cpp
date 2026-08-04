#include "mdns_client.h"
#include "config.h"

bool MDNSClient::discoverPC(String& outIp, int& outPort, int timeoutSec) {
    if (!MDNS.begin("esp32-attendance")) {
        Serial.println("mDNS: Failed to start");
        return false;
    }

    Serial.println("mDNS: Looking for " + String(MDNS_SERVICE) + " ...");

    int numServices = MDNS.queryService(MDNS_SERVICE, "tcp");
    if (numServices == 0) {
        Serial.println("mDNS: No PC found");
        MDNS.end();
        return false;
    }

    for (int i = 0; i < numServices; i++) {
        if (MDNS.hostname(i) == "absensi-pc") {
            outIp = MDNS.IP(i).toString();
            outPort = MDNS.port(i);
            Serial.println("mDNS: Found PC at " + outIp + ":" + String(outPort));
            MDNS.end();
            return true;
        }
    }

    // Fallback: use first found service
    outIp = MDNS.IP(0).toString();
    outPort = MDNS.port(0);
    Serial.println("mDNS: Found service at " + outIp + ":" + String(outPort));
    MDNS.end();
    return true;
}
