#!/usr/bin/env python3
import serial
import time
import sys

def main():
    port = "COM15"
    baud = 115200
    print(f"Resetting ESP32 on {port} and monitoring Wi-Fi connection logs for 15 seconds...")
    try:
        s = serial.Serial(port, baud, timeout=1)
        # Force DTR/RTS reset
        s.dtr = False
        s.rts = True
        time.sleep(0.1)
        s.rts = False
        time.sleep(0.2)
        s.reset_input_buffer()

        start = time.time()
        while time.time() - start < 15:
            line = s.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[ESP32] {line}")
        s.close()
    except Exception as e:
        print(f"Serial Error: {e}")

if __name__ == "__main__":
    main()
