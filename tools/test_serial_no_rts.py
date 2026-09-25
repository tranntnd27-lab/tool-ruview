#!/usr/bin/env python3
import serial
import time

def main():
    port = "COM15"
    baud = 115200
    print(f"Opening {port} at {baud} (no DTR/RTS reset)...")
    try:
        s = serial.Serial(port, baud, timeout=1)
        start = time.time()
        count = 0
        while time.time() - start < 15:
            line = s.readline().decode('utf-8', errors='replace').strip()
            if line:
                try:
                    print(f"[SERIAL] {line}")
                except UnicodeEncodeError:
                    print(f"[SERIAL] {line.encode('ascii', errors='replace').decode('ascii')}")
                count += 1
        s.close()
        print(f"Finished. Total lines read: {count}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
