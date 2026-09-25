#!/usr/bin/env python3
"""
Active Traffic Generator & CSI UDP Listener Test.
Pings the ESP32 node continuously to generate active Wi-Fi unicast traffic,
driving the ESP32 CSI engine and capturing UDP CSI packets on port 5005.
"""

import socket
import subprocess
import threading
import time
import struct
import sys

esp32_ips = ["192.168.2.175"]

def pinger():
    while True:
        for ip in esp32_ips:
            try:
                subprocess.run(["ping", "-n", "2", "-w", "500", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        time.sleep(0.1)

def main():
    # Start traffic pinger in background thread
    t = threading.Thread(target=pinger, daemon=True)
    t.start()
    print("Started background traffic generator (pinging ESP32 node at 192.168.2.175)...", flush=True)

    host = "0.0.0.0"
    port = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((host, port))
    except Exception as e:
        print(f"Error binding UDP port {port}: {e}")
        sys.exit(1)

    print(f"==================================================")
    print(f" Listening for UDP CSI packets on port {port}...")
    print(f"==================================================")

    magic_names = {
        0xC5110001: "Raw CSI (ADR-018)",
        0xC5110002: "Vitals",
        0xC5110003: "Feature Vector",
        0xC5110004: "Fused Vitals",
        0xC5110005: "Compressed CSI",
        0xC5110006: "Feature State",
        0xC5110007: "WASM Output",
        0xC511A110: "Sync Packet (ADR-110)",
        0xC5118100: "Mesh Frame",
    }

    start = time.time()
    packet_count = 0
    raw_csi_count = 0

    sock.settimeout(2.0)
    try:
        while True:
            try:
                data, addr = sock.recvfrom(2048)
                packet_count += 1
                magic_str = "Unknown"
                if len(data) >= 4:
                    magic = struct.unpack("<I", data[:4])[0]
                    magic_str = magic_names.get(magic, f"0x{magic:08X}")
                    if magic == 0xC5110001:
                        raw_csi_count += 1

                now = time.time()
                elapsed = now - start
                pps = packet_count / elapsed if elapsed > 0 else 0
                csi_pps = raw_csi_count / elapsed if elapsed > 0 else 0
                print(f"[{time.strftime('%H:%M:%S')}] PACKET RECEIVED from {addr[0]}:{addr[1]} | Len={len(data)}B | Type={magic_str} | Total={packet_count} (Raw CSI={raw_csi_count}, pps={pps:.1f})", flush=True)

            except socket.timeout:
                print("[Wait] Listening for active UDP CSI frames...", flush=True)
    except KeyboardInterrupt:
        print("\nStopped test.")

if __name__ == "__main__":
    main()
