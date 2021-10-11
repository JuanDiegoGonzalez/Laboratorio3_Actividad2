import socket, threading, hashlib, time, os
from datetime import datetime

if __name__ == "__main__":
    try:
        # Se establece la cantidad de clientes que se van a crear
        cantThreads = int(input("Ingrese la cantidad de clientes a crear: "))
        if cantThreads < 1:
            raise ValueError("[Error] El numero debe ser mayor a 0")

        # Se crea la carpeta para guardar los archivos (si no existe)
        if not os.path.isdir('ArchivosRecibidos'):
            os.mkdir(os.path.join(os.getcwd(), "ArchivosRecibidos"))

        # Se crea la carpeta para guardar los logs (si no existe)
        if not os.path.isdir('Logs'):
            os.mkdir(os.path.join(os.getcwd(), "Logs"))




        # Se crea el socket UDP del cliente
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        host = input("Ingrese la direccion IP del servidor (esta fue indicada en la terminal donde se ejecuto el servidor): ")
        port = 1234
        server_address = (host, port)
        message = b'This is the message.'

        # Send data
        print('sending {!r}'.format(message))
        sent = sock.sendto(message, server_address)

        # Receive response
        print('waiting to receive')
        data, server = sock.recvfrom(4096)
        print('received {!r}'.format(data))

        print('closing socket')
        sock.close()

    except (ValueError, ConnectionResetError) as e:
        print("\n", e, sep="")
