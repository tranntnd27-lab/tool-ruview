#!/usr/bin/env python3
import serial
import time

def monitor_esp32(port="COM15", baud=115200):
    print(f"Connecting to {port} at {baud} baud to capture live ESP-IDF log lines...")
    try:
        s = serial.Serial(port, baud, timeout=1)
        # Soft reset
        s.dtr = False
        s.rts = True
        time.sleep(0.1)
        s.rts = False
        time.sleep(0.2)
        s.reset_input_buffer()

        start = time.time()
        print("=== LIVE ESP32 SERIAL OUTPUT ===")
        while time.time() - start < 10:
            raw = s.readline()
            if raw:
                try:
                    text = raw.decode('utf-8', errors='replace').rstrip()
                    print(text)
                except Exception as e:
                    print(f"raw: {raw}")
        s.close()
    except Exception as e:
        print(f"Serial Error: {e}")

if __name__ == "__main__":
    monitor_esp32()
