import socket, threading, hashlib, time, os, platform, subprocess, ipaddress
from datetime import datetime

if __name__ == "__main__":
    try:
        # Se carga el contenido del archivo
        nombreArchivo = input("\nIngrese el nombre del archivo a transferir (incluyendo la extension): ")
        print("Cargando archivo...")
        archivo = open("ArchivosAEnviar/{}".format(nombreArchivo), "rb")
        contenidoArchivo = archivo.read()
        archivo.close()
        print("Archivo cargado")

        # Se establece la cantidad de clientes a atender al tiempo
        cantConexiones = int(input("\nIngrese la cantidad de conexiones concurrentes: "))
        if cantConexiones < 1:
            raise ValueError("[Error] El numero debe ser mayor a 0")

        # Se crea el socket UDP del servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = None

        try:  # Se intenta identificar la IP automaticamente
            if platform.system() == 'Windows':
                p = subprocess.Popen('ipconfig', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                host = str(p.stdout.readlines()[7]).split(" ")[-1].split("\\")[0]  # host = 192.168.0.2 (o similar)
            elif platform.system() == 'Linux':
                p = subprocess.Popen('ifconfig', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                host = str(p.stdout.readlines()[1]).split("inet")[1].split(" ")[1]  # host = 192.168.0.16 (o similar)

            ipaddress.IPv4Network(host)

        except:  # Si no se puede (es decir, si hay error), se le pregunta al usuario
            host = input("\nIngrese la direccion IP de esta maquina (ejecutar el comando ipconfig o ifconfig en una terminal): ")

        port = 1234
        sock.bind((host, port))
        print("\nDireccion IP del servidor:", host)

        # Se crea la carpeta para guardar el log (si no existe)
        if not os.path.isdir('Logs'):
            os.mkdir(os.path.join(os.getcwd(), "Logs"))




        # Se inicializan las listas de clientes
        resultComprobacionHash = [None for i in range(cantConexiones)]
        tiemposDeTransmision = [None for i in range(cantConexiones)]

        print("\nServidor listo para atender clientes")

        # Se
        while True:
            print('\nwaiting to receive message')
            data, address = sock.recvfrom(4096)

            print('received {} bytes from {}'.format(
                len(data), address))
            print(data)

            if data:
                sent = sock.sendto(data, address)
                print('sent {} bytes back to {}'.format(
                    sent, address))

    except (FileNotFoundError, ValueError, ConnectionResetError) as e:
        print("\n", e, sep="")