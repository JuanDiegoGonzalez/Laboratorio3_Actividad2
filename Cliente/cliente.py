import socket, threading, hashlib, time, os
from datetime import datetime

# Socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host = input("Ingrese la direccion IP del servidor (esta fue indicada en la terminal donde se ejecuto el servidor): ")
port = 1234
server_address = (host, port)
message = b'This is the message.'

try:
    # Send data
    print('sending {!r}'.format(message))
    sent = sock.sendto(message, server_address)

    # Receive response
    print('waiting to receive')
    data, server = sock.recvfrom(4096)
    print('received {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()
