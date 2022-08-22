import socket

UDP_IP = "192.168.1.255"
UDP_PORT_SEND = 51235
UDP_PORT_RECEIVE = 44444
MESSAGE = b"STYLE BANK 92 18 TEXT CIAO"

print("UDP receiving Port: %s" %UDP_PORT_RECEIVE)
print("UDP target IP: %s" %UDP_IP)
print("UDP target Port: %s" %UDP_PORT_SEND)
print("message: %s" %MESSAGE.decode())

sock_r = socket.socket(socket.AF_INET,
       socket.SOCK_DGRAM)
sock_s = socket.socket(socket.AF_INET,
       socket.SOCK_DGRAM)

sock_r.bind(('0.0.0.0', 44444))

sock_r.

while True:
    data, addr = sock_r.recvfrom(1024)
    print("received message: %s" %data.decode())
    sock_s.sendto(data, (UDP_IP, UDP_PORT_SEND))
    print("message \'%s\' sent to \'%s\' on port \'%s\'" %(data.decode(), UDP_IP, UDP_PORT_SEND))