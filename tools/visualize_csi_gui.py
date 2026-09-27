#!/usr/bin/env python3
"""
RuView CSI Visualizer & Plotter
Visualizes recorded CSI datasets (.pkl) with Matplotlib heatmaps, amplitude curves, and phase plots.
"""

import argparse
import math
import os
import pickle
import struct
import sys
import numpy as np
import matplotlib.pyplot as plt

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="RuView CSI Dataset Visualizer")
    parser.add_argument("file", nargs="?", default="idle_01.pkl", help="Path to .pkl dataset file (default: idle_01.pkl)")
    parser.add_argument("--save", "-s", type=str, default="csi_visual_analysis.png", help="PNG output path")
    parser.add_argument("--show", action="store_true", help="Display GUI window")
    parser.add_argument("--norm", action="store_true", help="Bù trừ khuếch đại AGC / RSSI Normalization")
    args = parser.parse_args()

    filepath = args.file
    if not os.path.exists(filepath):
        print(f"❌ Không tìm thấy file: {filepath}")
        sys.exit(1)

    print(f"📊 Đang đọc và xử lý ma trận sóng CSI từ file: {filepath}...")
    with open(filepath, "rb") as f:
        records = pickle.load(f)

    # Filter raw CSI frames
    raw_frames = []
    timestamps = []
    rssi_list = []

    for r in records:
        raw_data = r.get('data', b'')
        if len(raw_data) >= 20:
            m = struct.unpack("<I", raw_data[:4])[0]
            if m == 0xC5110001:  # Raw CSI
                magic_val, node_id, n_ant, n_sub, freq, seq, rssi, noise = struct.unpack("<IBBHIIbb", raw_data[:18])
                iq_bytes = raw_data[20:]
                num_subcarriers = len(iq_bytes) // 2

                # Compute scale factor for AGC normalization if requested
                scale = 10.0 ** (rssi / 20.0) if args.norm else 1.0

                amps = []
                phases = []
                for idx in range(num_subcarriers):
                    i_val = struct.unpack("b", iq_bytes[2*idx:2*idx+1])[0]
                    q_val = struct.unpack("b", iq_bytes[2*idx+1:2*idx+2])[0]
                    amp = math.sqrt(i_val**2 + q_val**2) * scale
                    amps.append(amp)
                    phases.append(math.atan2(q_val, i_val))

                # Ensure uniform subcarrier count (e.g. 64) for clean matrix operations
                if num_subcarriers < 64:
                    amps += [0.0] * (64 - num_subcarriers)
                elif num_subcarriers > 64:
                    amps = amps[:64]

                raw_frames.append(amps)
                timestamps.append(r['timestamp'])
                rssi_list.append(rssi)

    if not raw_frames:
        print("❌ Không tìm thấy gói tin Raw CSI (0xC5110001) nào để vẽ đồ thị.")
        sys.exit(1)

    # Convert to 2D numpy matrix: shape (num_frames, num_subcarriers)
    matrix = np.array(raw_frames)
    num_frames, num_subcarriers = matrix.shape
    t_rel = np.array(timestamps) - timestamps[0]

    print(f"✅ Đã trích xuất ma trận sóng CSI: {num_frames} Khung hình x {num_subcarriers} Subcarriers.")

    # Create multi-panel figure
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2.5, 2, 1.2]})
    fig.suptitle(f"MÔ PHỎNG VÀ PHÂN TÍCH MA TRẬN SÓNG VẬT LÝ WI-FI CSI ({os.path.basename(filepath)})", fontsize=14, fontweight='bold', y=0.98)

    # 1. HEATMAP (Subcarriers vs Time)
    im = axes[0].imshow(matrix.T, aspect='auto', cmap='viridis', origin='lower',
                        extent=[t_rel[0], t_rel[-1], 0, num_subcarriers])
    axes[0].set_title("1. Ma trận Phổ Biên độ Sóng CSI 2D (Heatmap - Cột = Subcarrier 0..63, Hàng = Thời gian)", fontsize=11, fontweight='bold')
    axes[0].set_xlabel("Thời gian (Giây)")
    axes[0].set_ylabel("OFDM Subcarrier Index (0..63)")
    cbar = fig.colorbar(im, ax=axes[0], orientation='vertical', pad=0.02)
    cbar.set_label("Biên độ A = √(I² + Q²)")

    # Highlight Guard Bands
    axes[0].axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Guard Band (A=0)')
    axes[0].axhline(y=27, color='red', linestyle='--', alpha=0.3)
    axes[0].axhline(y=38, color='red', linestyle='--', alpha=0.3)

    # 2. SUB-CARRIER AMPLITUDE WAVEFORMS (Time Domain Curves)
    for sub_idx in range(1, min(25, num_subcarriers)):
        if np.max(matrix[:, sub_idx]) > 0: # Skip zero guard subcarriers
            axes[1].plot(t_rel, matrix[:, sub_idx], label=f'Sub #{sub_idx}', alpha=0.7, linewidth=1.0)
    
    axes[1].set_title("2. Biểu đồ Đường cong Biên độ theo Thời gian (Subcarrier Amplitude Waveforms - A_k(t))", fontsize=11, fontweight='bold')
    axes[1].set_xlabel("Thời gian (Giây)")
    axes[1].set_ylabel("Biên độ Tín hiệu A")
    axes[1].grid(True, linestyle=':', alpha=0.6)

    # 3. RSSI SIGNAL STRENGTH OVER TIME
    axes[2].plot(t_rel, rssi_list, color='crimson', linewidth=1.5, label='RSSI (dBm)')
    axes[2].set_title("3. Cường độ Tín hiệu Mạng RSSI (Received Signal Strength Indicator)", fontsize=11, fontweight='bold')
    axes[2].set_xlabel("Thời gian (Giây)")
    axes[2].set_ylabel("RSSI (dBm)")
    axes[2].grid(True, linestyle=':', alpha=0.6)
    axes[2].legend(loc='upper right')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    save_path = os.path.abspath(args.save)
    plt.savefig(save_path, dpi=150)
    print(f"🖼️ Đã tạo đồ thị mô phỏng trực quan thành công: {save_path}")

    if args.show:
        plt.show()

if __name__ == "__main__":
    main()
