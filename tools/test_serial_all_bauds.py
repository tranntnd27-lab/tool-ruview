#!/usr/bin/env python3
import serial
import time

bauds = [115200, 460800, 921600, 9600]
port = "COM15"

for b in bauds:
    print(f"Testing {port} at baud {b}...")
    try:
        s = serial.Serial(port, b, timeout=2)
        s.dtr = True
        s.rts = True
        time.sleep(0.1)
        s.dtr = False
        s.rts = False
        t0 = time.time()
        buf = b""
        while time.time() - t0 < 2:
            chunk = s.read(100)
            if chunk:
                buf += chunk
        s.close()
        if buf:
            print(f"[FOUND AT {b}] Read {len(buf)} bytes:")
            print(buf[:200])
            break
        else:
            print(f"Baud {b}: 0 bytes received.")
    except Exception as e:
        print(f"Error at baud {b}: {e}")
