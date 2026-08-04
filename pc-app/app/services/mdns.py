import socket
from zeroconf import Zeroconf, ServiceInfo

mdns_service = None
zeroconf_instance = None


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = socket.gethostbyname(socket.gethostname())
    finally:
        s.close()
    return ip


def start_mdns():
    global zeroconf_instance, mdns_service
    try:
        local_ip = get_local_ip()

        zeroconf_instance = Zeroconf()

        mdns_service = ServiceInfo(
            type_="_attendance._tcp.local.",
            name="absensi-pc._attendance._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=8000,
            properties={"version": "1.0"},
        )

        zeroconf_instance.register_service(mdns_service)
        print(f"mDNS: absensi-pc.local -> {local_ip}:8000")
    except Exception as e:
        print(f"mDNS error: {e}")


def stop_mdns():
    global zeroconf_instance, mdns_service
    if zeroconf_instance:
        if mdns_service:
            zeroconf_instance.unregister_service(mdns_service)
        zeroconf_instance.close()
        print("mDNS: stopped")
