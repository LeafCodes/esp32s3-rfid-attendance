import argparse
import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def tap_card(uid):
    print(f"[*] Mensimulasikan tap kartu dengan UID: {uid}")
    try:
        response = requests.post(f"{BASE_URL}/attendance", json={"uid": uid})
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Status: {data.get('inout')} | Pesan: {data.get('message')}")
        else:
            print(f"[ERROR] {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("[FATAL] Tidak dapat terhubung ke server. Pastikan pc-app sedang berjalan!")

def rapid_tap(uid, times):
    print(f"[*] Mensimulasikan tap beruntun ({times} kali) untuk menguji Anti-Double Tap...")
    for i in range(times):
        print(f"\n--- Tap ke-{i+1} ---")
        tap_card(uid)
        time.sleep(1) # Jeda 1 detik antar tap

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RFID Hardware Simulator")
    subparsers = parser.add_subparsers(dest="command")

    # Command: tap
    tap_parser = subparsers.add_parser("tap", help="Simulasi satu kali tap kartu")
    tap_parser.add_argument("uid", help="UID Kartu (contoh: A1B2C3D4)")

    # Command: rapid
    rapid_parser = subparsers.add_parser("rapid", help="Simulasi tap beruntun untuk tes cooldown")
    rapid_parser.add_argument("uid", help="UID Kartu (contoh: A1B2C3D4)")
    rapid_parser.add_argument("--times", type=int, default=3, help="Jumlah tap")

    args = parser.parse_args()

    if args.command == "tap":
        tap_card(args.uid)
    elif args.command == "rapid":
        rapid_tap(args.uid, args.times)
    else:
        parser.print_help()
