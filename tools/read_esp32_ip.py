#!/usr/bin/env python3
import serial
import time

def main():
    port = "COM15"
    baud = 115200
    print(f"Checking live ESP32 serial logs on {port}...")
    try:
        s = serial.Serial(port, baud, timeout=1)
        # Send a newline or status command
        s.write(b"\nstatus\nhelp\n")
        start = time.time()
        while time.time() - start < 8:
            line = s.readline().decode('utf-8', errors='replace').strip()
            if line:
                print(f"[ESP32 LOG] {line}")
        s.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
