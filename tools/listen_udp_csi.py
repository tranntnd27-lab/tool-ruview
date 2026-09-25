#!/usr/bin/env python3
"""
UDP CSI Packet Receiver & Rate Monitor for RuView ESP32 Nodes.
Listens on UDP port 5005 and prints packet statistics & magic headers.
"""

import socket
import struct
import time
import sys

def main():
    host = "0.0.0.0"
    port = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((host, port))
    except Exception as e:
        print(f"Error binding socket on {host}:{port}: {e}")
        sys.exit(1)

    print(f"==================================================")
    print(f" Listening for UDP CSI packets on port {port}...")
    print(f" Press Ctrl+C to stop.")
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

    start_time = time.time()
    packet_count = 0
    raw_csi_count = 0
    bytes_count = 0
    last_stat_time = time.time()

    sock.settimeout(2.0)

    try:
        while True:
            try:
                data, addr = sock.recvfrom(2048)
            except socket.timeout:
                print(f"[Wait] No UDP packets received in the last 2 seconds from ESP32...", flush=True)
                continue

            packet_count += 1
            bytes_count += len(data)

            magic_str = "Unknown"
            if len(data) >= 4:
                magic = struct.unpack("<I", data[:4])[0]
                magic_str = magic_names.get(magic, f"0x{magic:08X}")
                if magic == 0xC5110001:
                    raw_csi_count += 1

            now = time.time()
            if packet_count <= 5 or (now - last_stat_time) >= 3.0:
                elapsed = now - start_time
                pps = packet_count / elapsed if elapsed > 0 else 0
                csi_pps = raw_csi_count / elapsed if elapsed > 0 else 0
                print(f"[{time.strftime('%H:%M:%S')}] From {addr[0]}:{addr[1]} | Len={len(data)}B | Type={magic_str} | Total={packet_count} (Raw CSI pps={csi_pps:.2f}, Total pps={pps:.2f})", flush=True)
                last_stat_time = now

    except KeyboardInterrupt:
        print("\nStopped UDP receiver.")

if __name__ == "__main__":
    main()
