#!/usr/bin/env python3
import subprocess
import concurrent.futures
import re

def ping_ip(ip):
    try:
        subprocess.run(["ping", "-n", "1", "-w", "200", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def main():
    base = "192.168.2."
    print("Sweeping 192.168.2.1-254 to find ESP32 (MAC: 84-fc-e6-68-8d-7c)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(ping_ip, f"{base}{i}") for i in range(1, 255)]
        concurrent.futures.wait(futures)

    arp_out = subprocess.check_output(["arp", "-a"], text=True, errors="ignore")
    print("\nSearch results for Espressif MAC (84-fc-e6...):")
    found = False
    for line in arp_out.splitlines():
        if "84-fc-e6" in line.lower() or "84:fc:e6" in line.lower():
            print(f"-> FOUND ESP32 AT: {line.strip()}")
            found = True
    if not found:
        print("No matching ESP32 MAC in ARP table yet. Full active ARP entries:")
        for line in arp_out.splitlines():
            if "192.168.2." in line:
                print(f"   {line.strip()}")

if __name__ == "__main__":
    main()
