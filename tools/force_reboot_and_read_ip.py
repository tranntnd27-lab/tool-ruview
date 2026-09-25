#!/usr/bin/env python3
import serial
import time
import sys

def main():
    port = "COM15"
    baud = 115200
    print(f"Opening {port} at {baud} baud and waiting for boot/status logs...")
    try:
        s = serial.Serial(port, baud, timeout=1)
        s.dtr = True
        s.rts = True
        # Try sending soft reboot text
        s.write(b"\r\nreboot\r\n")
        s.write(b"RUVIEW_REBOOT\r\n")
        
        start = time.time()
        print("=== MONITORING LOGS FOR GOT_IP & TARGET IP ===")
        while time.time() - start < 15:
            line = s.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # Replace non-ascii chars to avoid Windows cp1252 print errors
                safe_line = line.encode('ascii', errors='replace').decode('ascii')
                print(f"[COM15 LOG] {safe_line}")
        s.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
