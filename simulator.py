import argparse
import requests
import time
import sys
import threading
import random
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def tap_card(uid, silent=False):
    if not silent:
        print(f"[*] Mensimulasikan tap kartu dengan UID: {uid}")
    
    payload = {
        "uid": uid,
        "name": "Simulasi User",
        "status": "AUTO",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/attendance", json=payload)
        if not silent:
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] Status: {data.get('inout')} | Pesan: {data.get('message')}")
            else:
                print(f"[ERROR] {response.status_code} - {response.text}")
        return response.status_code
    except requests.exceptions.ConnectionError:
        if not silent:
            print("[FATAL] Tidak dapat terhubung ke server. Pastikan pc-app sedang berjalan!")
        return 500

def rapid_tap(uid, times):
    print(f"[*] Mensimulasikan tap beruntun ({times} kali) untuk menguji Anti-Double Tap...")
    for i in range(times):
        print(f"\n--- Tap ke-{i+1} ---")
        tap_card(uid)
        time.sleep(1) # Jeda 1 detik antar tap

def offline_sync(count):
    print(f"[*] Mensimulasikan sinkronisasi {count} data offline secara beruntun...")
    success_count = 0
    for i in range(count):
        uid = f"OFFLINE{i:03d}"
        payload = {
            "uid": uid,
            "name": f"Offline User {i}",
            "status": "IN",
            "timestamp": datetime.now().isoformat()
        }
        try:
            response = requests.post(f"{BASE_URL}/attendance", json=payload)
            if response.status_code == 200:
                success_count += 1
            else:
                print(f"[ERROR] UID {uid}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[ERROR] Exception pada UID {uid}: {e}")
    print(f"[DONE] {success_count}/{count} data offline berhasil disinkronkan.")

def stress_test(users, devices):
    print(f"[*] Memulai Stress Test: {users} request dari {devices} perangkat bersamaan...")
    
    def device_thread(device_id, req_count):
        for i in range(req_count):
            uid = f"USER{random.randint(100, 999)}"
            tap_card(uid, silent=True)
            
    threads = []
    reqs_per_device = users // devices
    
    start_time = time.time()
    for d in range(devices):
        t = threading.Thread(target=device_thread, args=(d, reqs_per_device))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    end_time = time.time()
    print(f"[DONE] Stress Test Selesai. Waktu Eksekusi: {end_time - start_time:.2f} detik")

def sync_cards():
    print(f"[*] Mensimulasikan ESP32 mengambil daftar kartu (polling)...")
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/cards")
        end_time = time.time()
        if response.status_code == 200:
            data = response.json()
            cards = data.get("cards", [])
            print(f"[SUCCESS] Berhasil mengambil {len(cards)} kartu.")
            print(f"[*] Response Time: {end_time - start_time:.3f} detik")
            print(f"[*] Payload Size: {len(response.text)} bytes")
        else:
            print(f"[ERROR] {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("[FATAL] Tidak dapat terhubung ke server.")

def corrupt_tap():
    print(f"[*] Mensimulasikan Negative Testing (Payload Rusak)...")
    payloads = [
        {"invalid_key": "12345"},           # Struktur salah
        {"uid": ""},                        # UID Kosong
        {"uid": "A" * 256},                 # UID sangat panjang (Overflow)
        {"uid": "'; DROP TABLE cards; --"}  # SQL Injection attempt
    ]
    
    for i, payload in enumerate(payloads):
        print(f"\n--- Skenario {i+1}: {payload} ---")
        try:
            response = requests.post(f"{BASE_URL}/attendance", json=payload)
            print(f"Response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Gagal memproses request: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RFID Advanced Hardware Simulator")
    subparsers = parser.add_subparsers(dest="command")

    # Command: tap
    tap_parser = subparsers.add_parser("tap", help="Simulasi satu kali tap kartu")
    tap_parser.add_argument("uid", help="UID Kartu (contoh: A1B2C3D4)")

    # Command: rapid
    rapid_parser = subparsers.add_parser("rapid", help="Simulasi tap beruntun untuk tes cooldown")
    rapid_parser.add_argument("uid", help="UID Kartu (contoh: A1B2C3D4)")
    rapid_parser.add_argument("--times", type=int, default=3, help="Jumlah tap")

    # Command: offline-sync
    offline_parser = subparsers.add_parser("offline-sync", help="Simulasi pengiriman data tertunda dari buffer offline")
    offline_parser.add_argument("--count", type=int, default=10, help="Jumlah data tertunda")

    # Command: stress
    stress_parser = subparsers.add_parser("stress", help="Simulasi ratusan tap untuk uji beban server")
    stress_parser.add_argument("--users", type=int, default=50, help="Jumlah total request")
    stress_parser.add_argument("--devices", type=int, default=3, help="Jumlah alat/thread yang digunakan")

    # Command: sync-cards
    sync_parser = subparsers.add_parser("sync-cards", help="Simulasi ESP32 mengambil daftar kartu (polling)")

    # Command: corrupt
    corrupt_parser = subparsers.add_parser("corrupt", help="Mengirim payload yang salah untuk menguji validasi server")

    args = parser.parse_args()

    if args.command == "tap":
        tap_card(args.uid)
    elif args.command == "rapid":
        rapid_tap(args.uid, args.times)
    elif args.command == "offline-sync":
        offline_sync(args.count)
    elif args.command == "stress":
        stress_test(args.users, args.devices)
    elif args.command == "sync-cards":
        sync_cards()
    elif args.command == "corrupt":
        corrupt_tap()
    else:
        parser.print_help()
