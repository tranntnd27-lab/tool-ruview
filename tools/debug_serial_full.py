#!/usr/bin/env python3
import serial
import time
import sys

def main():
    port = "COM15"
    baud = 115200
    print(f"Opening {port} at {baud} baud and monitoring serial output for 15 seconds...")
    try:
        s = serial.Serial(port, baud, timeout=1)
        # Pulse RTS to reset board
        s.dtr = False
        s.rts = True
        time.sleep(0.1)
        s.rts = False
        time.sleep(0.2)
        s.reset_input_buffer()

        start = time.time()
        count = 0
        while time.time() - start < 15:
            line = s.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[ESP32 LOG] {line}")
                count += 1
        s.close()
        print(f"Finished monitoring. Read {count} lines.")
    except Exception as e:
        print(f"Error reading serial: {e}")

if __name__ == "__main__":
    main()
