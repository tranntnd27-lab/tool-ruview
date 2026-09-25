#!/usr/bin/env python3
"""
RuView CSI Dataset Recorder
Records incoming UDP CSI packets for a specified duration and saves them into a .pkl dataset file.

Usage:
    python tools/record_csi_dataset.py --output idle_01.pkl --duration 60
    python tools/record_csi_dataset.py --output motion_01.pkl --duration 60
"""

import argparse
import math
import os
import pickle
import socket
import struct
import sys
import time

def main():
    parser = argparse.ArgumentParser(description="RuView CSI Dataset Recorder")
    parser.add_argument("--output", "-o", type=str, default="idle_01.pkl", help="File đầu ra (.pkl)")
    parser.add_argument("--duration", "-d", type=int, default=60, help="Thời gian thu (giây)")
    parser.add_argument("--port", "-p", type=int, default=5005, help="Cổng UDP (mặc định 5005)")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("0.0.0.0", args.port))
    except Exception as e:
        print(f"Lỗi mở cổng UDP {args.port}: {e}")
        print("Gợi ý: Bấm Ctrl+C tắt các terminal cũ đang mở cổng 5005 rồi thử lại.")
        sys.exit(1)

    print("=" * 65)
    print("      RUVIEW CSI DATASET RECORDER - TRÌNH THU DỮ LIỆU SÓNG")
    print("=" * 65)
    print(f"  Tên file đầu ra : {args.output}")
    print(f"  Thời gian thu    : {args.duration} giây")
    print(f"  Cổng UDP         : {args.port}")
    print("-" * 65)

    if "idle" in args.output.lower():
        print("👉 HƯỚNG DẪN: Giữ phòng trống HOÀN TOÀN TĨNH trong suốt quá trình thu!")
    elif "motion" in args.output.lower():
        print("👉 HƯỚNG DẪN: Cho người di chuyển, bước đi trong khu vực phủ sóng Wi-Fi!")
    print("-" * 65)

    input("Bấm Enter để BẮT ĐẦU THU DỮ LIỆU...")

    start_time = time.time()
    end_time = start_time + args.duration

    records = []
    raw_csi_count = 0
    feature_count = 0

    sock.settimeout(1.0)

    try:
        while time.time() < end_time:
            now = time.time()
            remaining = int(end_time - now)
            elapsed = now - start_time
            progress_pct = (elapsed / args.duration) * 100

            try:
                data, addr = sock.recvfrom(2048)
                if len(data) >= 4:
                    magic = struct.unpack("<I", data[:4])[0]
                    rec = {
                        "timestamp": now,
                        "addr": addr[0],
                        "port": addr[1],
                        "len": len(data),
                        "data": data
                    }

                    if magic == 0xC5110001:  # Raw CSI
                        raw_csi_count += 1
                        if len(data) >= 20:
                            magic_val, node_id, n_ant, n_sub, freq, seq, rssi, noise = struct.unpack("<IBBHIIbb", data[:18])
                            rec["node_id"] = node_id
                            rec["seq"] = seq
                            rec["rssi"] = rssi
                            rec["freq"] = freq
                            rec["n_subcarriers"] = n_sub

                    elif magic == 0xC5110006:  # Feature State
                        feature_count += 1

                    records.append(rec)
            except socket.timeout:
                pass

            # Update progress bar
            bar_len = 30
            filled = int(bar_len * elapsed / args.duration)
            bar = "=" * filled + "-" * (bar_len - filled)
            print(f"\r[{bar}] {progress_pct:5.1f}% | ⏱️ {remaining:2d}s còn lại | 📦 Tổng: {len(records)} (CSI: {raw_csi_count})", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\nĐã hủy quá trình thu giữa chừng.")

    print("\n\n" + "=" * 65)
    print("  HOÀN THÀNH QUÁ TRÌNH THU DỮ LIỆU!")
    print("=" * 65)
    print(f"  Tổng số gói thu được : {len(records)}")
    print(f"  Số gói Raw CSI       : {raw_csi_count}")
    print(f"  Số gói Feature State : {feature_count}")

    if records:
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        with open(args.output, "wb") as f:
            pickle.dump(records, f)

        file_size_kb = os.path.getsize(args.output) / 1024
        print(f"  Đã lưu file thành công : {os.path.abspath(args.output)} ({file_size_kb:.1f} KB)")
        print("-" * 65)
        print("✨ Bạn có thể sử dụng file .pkl này để huấn luyện AI hoặc phân tích phổ tín hiệu!")
    else:
        print("⚠️ Không thu được gói tin nào. Vui lòng kiểm tra lại kết nối ESP32.")

if __name__ == "__main__":
    main()
