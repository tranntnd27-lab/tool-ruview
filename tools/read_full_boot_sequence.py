#!/usr/bin/env python3
import serial
import time
import sys

def main():
    port = "COM15"
    baud = 115200
    print(f"Resetting ESP32 and recording ALL boot log lines from {port}...")
    try:
        s = serial.Serial(port, baud, timeout=0.5)
        # Software command reset if possible or toggle RTS
        s.write(b"reboot\n")
        time.sleep(0.1)
        s.dtr = False
        s.rts = True
        time.sleep(0.15)
        s.rts = False
        time.sleep(0.2)
        s.reset_input_buffer()

        start = time.time()
        lines = []
        while time.time() - start < 15:
            line = s.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[LOG] {line}")
                lines.append(line)
        s.close()
        print(f"Captured {len(lines)} log lines.")
    except Exception as e:
        print(f"Serial Error: {e}")

if __name__ == "__main__":
    main()
