#!/usr/bin/env python3
import serial
import time

def read_boot_log(port="COM15", baud=115200):
    print(f"Connecting to {port} and resetting ESP32...")
    try:
        s = serial.Serial(port, baud, timeout=2)
        # Reset ESP32 using DTR/RTS pins (same as esptool hard reset)
        s.dtr = False
        s.rts = True
        time.sleep(0.1)
        s.rts = False
        time.sleep(0.2)
        s.reset_input_buffer()

        print("=== ESP32 Serial Boot Output ===")
        start = time.time()
        lines_read = 0
        while time.time() - start < 8 and lines_read < 40:
            line = s.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(line)
                lines_read += 1
        s.close()
    except Exception as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    read_boot_log()
