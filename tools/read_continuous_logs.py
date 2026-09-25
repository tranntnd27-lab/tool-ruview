#!/usr/bin/env python3
import serial
import time

def main():
    port = "COM15"
    baud = 115200
    print(f"Opening {port} at {baud} baud (WITHOUT reset) to read continuous logs...")
    try:
        s = serial.Serial(port, baud, timeout=1)
        # Keep DTR/RTS high so USB CDC stays alive
        s.dtr = True
        s.rts = True
        
        start = time.time()
        count = 0
        while time.time() - start < 15:
            line = s.readline().decode('utf-8', errors='replace').rstrip()
            if line:
                print(f"[COM15] {line}")
                count += 1
        s.close()
        print(f"Monitoring finished. Total lines: {count}")
    except Exception as e:
        print(f"Serial Error: {e}")

if __name__ == "__main__":
    main()
