#!/usr/bin/env python3
"""
RuView CSI Packet Inspector & Verifier
Decodes and visualizes ADR-018 raw CSI packets and ADR-081 feature state packets on UDP port 5005.
"""

import math
import socket
import struct
import sys
import time

MAGIC_NAMES = {
    0xC5110001: "Raw CSI (ADR-018)",
    0xC5110002: "Vitals (ADR-039)",
    0xC5110003: "Feature Vector",
    0xC5110004: "Fused Vitals",
    0xC5110005: "Compressed CSI",
    0xC5110006: "Feature State (ADR-081)",
    0xC5110007: "WASM Output",
    0xC511A110: "Sync Packet (ADR-110)",
    0xC5118100: "Mesh Frame",
}

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    host = "0.0.0.0"
    port = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind((host, port))
    except Exception as e:
        print(f"Loi mở cổng UDP {port}: {e}")
        print("Gợi ý: Hãy tắt các terminal cũ đang chạy listen_udp_csi.py bằng Ctrl+C rồi thử lại.")
        sys.exit(1)

    print("=" * 65)
    print(f"  RUVIEW CSI PACKET INSPECTOR - UDP PORT {port}")
    print("=" * 65)
    print("Đang chờ gói tin từ ESP32... (Bấm Ctrl+C để dừng)\n")

    count = 0
    raw_count = 0

    try:
        while True:
            data, addr = sock.recvfrom(2048)
            count += 1
            now_str = time.strftime("%H:%M:%S")

            if len(data) < 4:
                continue

            magic = struct.unpack("<I", data[:4])[0]
            type_name = MAGIC_NAMES.get(magic, f"Unknown (0x{magic:08X})")

            if magic == 0xC5110001:  # Raw CSI Packet
                raw_count += 1
                if len(data) >= 20:
                    magic_val, node_id, n_ant, n_sub, freq_mhz, seq, rssi, noise = struct.unpack(
                        "<IBBHIIbb", data[:18]
                    )
                    ppdu_type = data[18]
                    flags = data[19]

                    iq_bytes = data[20:]
                    num_subcarriers = len(iq_bytes) // 2

                    # Compute amplitudes for subcarriers
                    amplitudes = []
                    zero_count = 0
                    for i in range(num_subcarriers):
                        i_val = struct.unpack("b", iq_bytes[2*i:2*i+1])[0]
                        q_val = struct.unpack("b", iq_bytes[2*i+1:2*i+2])[0]
                        amp = math.sqrt(i_val**2 + q_val**2)
                        amplitudes.append(amp)
                        if i_val == 0 and q_val == 0:
                            zero_count += 1

                    avg_amp = sum(amplitudes) / len(amplitudes) if amplitudes else 0.0

                    print(f"[{now_str}] 📡 GÓI CSI THẬT (#{count} | Raw #{raw_count}) | Nguồn: {addr[0]}:{addr[1]}")
                    print(f"      Node ID: {node_id} | Ăng-ten: {n_ant} | Tần số: {freq_mhz} MHz | Kênh: {freq_mhz_to_chan(freq_mhz)}")
                    print(f"      Sequence: #{seq} | RSSI: {rssi} dBm | Noise: {noise} dBm")
                    print(f"      Subcarriers: {num_subcarriers} | Zero Subcarriers (Guard Band): {zero_count} | Biên độ TB: {avg_amp:.2f}")

                    # Bar visualization of first 16 subcarrier amplitudes
                    bar_str = "".join(["█" if a > avg_amp else "▄" if a > 0 else " " for a in amplitudes[:32]])
                    print(f"      Phổ biên độ (32 Subcarriers đầu): [{bar_str}]")
                    print("-" * 65)

            elif magic == 0xC5110006:  # Feature State Packet
                print(f"[{now_str}] 📊 GÓI FEATURE STATE (#{count}) | Nguồn: {addr[0]}:{addr[1]} | Len={len(data)}B")
                print("-" * 65)

    except KeyboardInterrupt:
        print("\nĐã dừng kiểm tra.")

def freq_mhz_to_chan(freq):
    if 2412 <= freq <= 2472:
        return (freq - 2412) // 5 + 1
    elif freq == 2484:
        return 14
    return "?"

if __name__ == "__main__":
    main()
