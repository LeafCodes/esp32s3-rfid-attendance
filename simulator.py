import argparse
import requests
import time
import sys
import threading
import random
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_header(title):
    print(f"\n{'='*45}")
    print(f" {title}")
    print(f"{'='*45}")

def tap_card(uid, silent=False):
    if not silent:
        print(f"[*] Mengirim data kehadiran untuk UID: '{uid}'...")
    
    payload = {
        "uid": uid,
        "name": "Simulasi User",
        "status": "AUTO",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/attendance", json=payload)
        elapsed = (time.time() - start) * 1000
        
        if not silent:
            if response.status_code == 200:
                data = response.json()
                print(f"  [√] SUKSES ({elapsed:.0f}ms)")
                print(f"  [-] Status Absen : {data.get('inout')}")
                print(f"  [-] Pesan Server : {data.get('message')}")
            else:
                print(f"  [X] GAGAL (HTTP {response.status_code})")
                print(f"  [-] Detail Error : {response.text}")
        return response.status_code
    except requests.exceptions.ConnectionError:
        if not silent:
            print("  [!] FATAL: Tidak dapat terhubung ke server (Server Offline?)")
        return 500

def rapid_tap(uid, times):
    print_header("SIMULASI RAPID TAP (COOLDOWN TEST)")
    print(f"[*] Menguji {times} tap beruntun untuk UID: '{uid}' dengan jeda 1 detik...")
    
    success = 0
    errors = 0
    
    for i in range(times):
        print(f"\n--- Percobaan {i+1}/{times} ---")
        code = tap_card(uid)
        if code == 200:
            success += 1
        else:
            errors += 1
        time.sleep(1)
        
    print(f"\n--- KESIMPULAN RAPID TAP ---")
    print(f"Total Percobaan : {times}")
    print(f"Berhasil (200)  : {success}")
    print(f"Gagal / Error   : {errors}")
    print("Catatan: Jika fitur cooldown berfungsi, tap kedua dst harus memiliki status sesuai tap pertama.")
    print(f"{'-'*45}")

def offline_sync(count):
    print_header("SIMULASI OFFLINE SYNC (BULK)")
    print(f"[*] Mensimulasikan ESP32 mengirim {count} data absensi sekaligus...")
    success_count = 0
    errors = {}
    
    start = time.time()
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
                errors[response.status_code] = errors.get(response.status_code, 0) + 1
        except Exception as e:
            errors["Exception"] = errors.get("Exception", 0) + 1
            
    elapsed = time.time() - start
    print(f"\n--- HASIL OFFLINE SYNC ---")
    print(f"Total Data      : {count}")
    print(f"Berhasil (200)  : {success_count}")
    print(f"Gagal           : {count - success_count}")
    if errors:
        print("Rincian Gagal   :")
        for code, c in errors.items():
            print(f"  - Error {code} : {c} kali")
    print(f"Waktu Eksekusi  : {elapsed:.2f} detik")
    print(f"{'-'*45}")

def stress_test(users, devices):
    print_header("STRESS TEST (LOAD TESTING)")
    print(f"[*] Mensimulasikan {users} request dari {devices} mesin...")
    
    results = {"success": 0, "failed": 0, "errors": {}}
    lock = threading.Lock()
    
    def device_thread(device_id, req_count):
        for i in range(req_count):
            uid = f"USER{random.randint(100, 999)}"
            payload = {
                "uid": uid,
                "name": f"Stress User {uid}",
                "status": "AUTO",
                "timestamp": datetime.now().isoformat()
            }
            try:
                response = requests.post(f"{BASE_URL}/attendance", json=payload)
                with lock:
                    if response.status_code == 200:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        code = response.status_code
                        results["errors"][code] = results["errors"].get(code, 0) + 1
            except Exception as e:
                with lock:
                    results["failed"] += 1
                    results["errors"]["Exception"] = results["errors"].get("Exception", 0) + 1
            
    threads = []
    reqs_per_device = users // devices
    actual_users = reqs_per_device * devices
    
    start_time = time.time()
    for d in range(devices):
        t = threading.Thread(target=device_thread, args=(d, reqs_per_device))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n--- HASIL STRESS TEST ---")
    print(f"Total Request   : {actual_users}")
    print(f"Berhasil (200)  : {results['success']}")
    print(f"Gagal           : {results['failed']}")
    if results["errors"]:
        print("Rincian Gagal   :")
        for code, count in results["errors"].items():
            print(f"  - Error {code}: {count} kali")
    print(f"Waktu Eksekusi  : {elapsed:.2f} detik")
    print(f"Kecepatan       : {actual_users / elapsed:.2f} request/detik")
    print(f"{'-'*45}")

def sync_cards():
    print_header("SIMULASI POLLING KARTU (CARD SYNC)")
    print(f"[*] Mensimulasikan ESP32 mengunduh daftar kartu dari server...")
    try:
        start = time.time()
        # ESP32 uses /api/cards/sync
        response = requests.get(f"{BASE_URL}/cards/sync", headers={"X-API-Key": "ESP32-SECRET-KEY"})
        elapsed = time.time() - start
        
        print(f"\n--- HASIL SYNC CARDS ---")
        if response.status_code == 200:
            data = response.json()
            item_count = len(data) if isinstance(data, list) else len(data.get("cards", []))
            size_kb = len(response.text) / 1024
            
            print(f"Status          : [√] SUKSES (HTTP 200)")
            print(f"Jumlah Kartu    : {item_count} item terdaftar")
            print(f"Ukuran Payload  : {size_kb:.2f} KB")
            print(f"Waktu Respon    : {elapsed:.3f} detik")
            
            if size_kb > 15:
                print("  [!] PERINGATAN: Ukuran JSON mulai besar, berpotensi membuat ESP32 kehabisan RAM/Memory.")
        else:
            print(f"Status          : [X] GAGAL (HTTP {response.status_code})")
            print(f"Pesan Server    : {response.text}")
    except requests.exceptions.ConnectionError:
        print("  [!] FATAL: Tidak dapat terhubung ke server.")
    print(f"{'-'*45}")

def corrupt_tap():
    print_header("NEGATIVE TESTING (PAYLOAD RUSAK)")
    print(f"[*] Menguji validasi server terhadap input tidak wajar/berbahaya...")
    
    payloads = [
        ("Tanpa field nama/status", {"uid": "123"}),
        ("UID Kosong", {"uid": "", "name": "Hack", "status": "IN", "timestamp": "2023-01-01"}),
        ("UID Sangat Panjang (Buffer Overflow)", {"uid": "A" * 500, "name": "Hack", "status": "IN", "timestamp": "2023-01-01"}),
        ("SQL Injection Attempt", {"uid": "'; DROP TABLE cards; --", "name": "Hack", "status": "IN", "timestamp": "2023-01-01"})
    ]
    
    passed = 0
    for i, (desc, payload) in enumerate(payloads):
        print(f"\n--- Skenario {i+1}: {desc} ---")
        try:
            start = time.time()
            response = requests.post(f"{BASE_URL}/attendance", json=payload)
            elapsed = (time.time() - start) * 1000
            
            # Kita berekspektasi server menolaknya secara normal (HTTP 4xx atau 404), BUKAN crash (500)
            if response.status_code >= 400 and response.status_code < 500:
                print(f"  [√] AMAN : Server menolak dengan baik (HTTP {response.status_code} | {elapsed:.0f}ms)")
                passed += 1
            elif response.status_code == 500:
                print(f"  [X] BAHAYA : Server Crash / Error 500! (Cek terminal Uvicorn)")
            else:
                print(f"  [!] ANEH : Server menerima payload rusak (HTTP {response.status_code})")
        except Exception as e:
            print(f"  [!] KONEKSI ERROR: {e}")
            
    print(f"\n--- HASIL NEGATIVE TESTING ---")
    print(f"Skor Keamanan   : {passed}/{len(payloads)} Lulus Uji Validasi")
    print(f"{'-'*45}")

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
        print_header("SIMULASI SINGLE TAP")
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
