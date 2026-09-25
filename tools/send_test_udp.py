import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Send ADR-018 header magic 0xC5110001
data = b"\x01\x00\x11\xC5" + b"\x00" * 16
print("Sending test UDP packet to 127.0.0.1:5005...")
sock.sendto(data, ("127.0.0.1", 5005))
print("Sent successfully!")
