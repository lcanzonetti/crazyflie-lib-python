import socket

UDP_IP = "192.168.1.255"
UDP_PORT_SEND = 51235
UDP_PORT_RECEIVE = 44444
MESSAGE = b"STYLE BANK 92 18 TEXT CIAO"

print("UDP receiving Port: %s" %UDP_PORT_RECEIVE)
print("UDP target IP: %s" %UDP_IP)
print("UDP target Port: %s" %UDP_PORT_SEND)
print("message: %s" %MESSAGE)

sock_r = socket.socket(socket.AF_INET,
       socket.SOCK_DGRAM)
sock_s = socket.socket(socket.AF_INET,
       socket.SOCK_DGRAM)

sock_r.bind(('127.0.0.1', 44444))

while True:
    msgAndAddress = sock_r.recvfrom(1024)
    print("received message: %s" %msgAndAddress[0].decode())
    sock_s.sendto(msgAndAddress[0], (UDP_IP, UDP_PORT_SEND))
    print("message %s sent to %s on port %s" %(msgAndAddress[0].decode(), UDP_IP, UDP_PORT_SEND))