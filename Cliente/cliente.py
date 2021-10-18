import socket, threading, hashlib, time, os
from datetime import datetime

# Declaracion de atributos
server_address = None

def recibirArchivoDelServidor(sock):
    # Se envia una peticion al servidor (que es la misma confirmacion de listo)
    sent = sock.sendto(b'Enviame el archivo', server_address)
    print("Cliente listo para recibir, esperando a los demas clientes")

    # Se recibe el numero del cliente
    numCliente, server = sock.recvfrom(4096)
    numCliente = numCliente.decode()

    # Se recibe la cantidad de conexiones concurrentes
    cantConexionesTotales, server = sock.recvfrom(4096)
    cantConexionesTotales = cantConexionesTotales.decode()

    # Se recibe el nombre del archivo
    nombreArchivo, server = sock.recvfrom(4096)
    nombreArchivo = nombreArchivo.decode()

    # Se abre el archivo donde se guardara el contenido recibido
    archivo = open("ArchivosRecibidos/Cliente{}-Prueba-{}.{}".format(numCliente, cantConexionesTotales, nombreArchivo.split(".")[-1]), "wb")

    print("Transmision iniciada, recibiendo archivo desde el servidor...")
    inicioTransmision = time.time()

    # Se recibe y se escribe el contenido del archivo
    recibido, server = sock.recvfrom(4096)
    i = 0
    while not str(recibido).endswith('Fin\''):
        archivo.write(recibido)
        i+=1
        print("Cliente {}: Parte {} recibida".format(numCliente,i))
        recibido, server = sock.recvfrom(4096)
    archivo.write(recibido[:-3])

    tiempoDeTransmision = time.time() - inicioTransmision
    print("Transmision completa. Archivo recibido.")

    archivo.close()

    # Se crea y se escribe el log
    escribirLog(numCliente, nombreArchivo, cantConexionesTotales, tiempoDeTransmision)

    sock.close()

def escribirLog(numCliente, nombreArchivo, cantConexionesTotales, tiempoDeTransmision):
    global server_address

    # a.
    fechaStr = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    archivo = open("Logs/{}-log (Cliente {}).txt".format(fechaStr, numCliente), "w")

    # b.
    archivo.write("Nombre del archivo recibido: {}\n".format(nombreArchivo))
    archivo.write("Tamano del archivo recibido: {} bytes\n\n".format(os.path.getsize("ArchivosRecibidos/Cliente{}-Prueba-{}.{}".format(numCliente, cantConexionesTotales, nombreArchivo.split(".")[-1]))))

    # c.
    archivo.write("Servidor desde el que se realizo la transferencia: ({}, {})\n\n".format(host, port))

    '''
    # d.
    archivo.write("Resultado de la transferencia: {}\n\n".format(mensajeComprobacionHash))
    '''

    # e.
    archivo.write("Tiempo de transmision: {:.2f} segundos\n".format(tiempoDeTransmision))

    archivo.close()

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

        # Se crean los threads de los clientes
        host = input("Ingrese la direccion IP del servidor (esta fue indicada en la terminal donde se ejecuto el servidor): ")
        port = 1234
        server_address = (host, port)
        threads = []

        for i in range(cantThreads):
            # Se crea el socket UDP del cliente
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            thread = threading.Thread(target=recibirArchivoDelServidor, args=(sock,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        time.sleep(2)

    except (ValueError, ConnectionResetError) as e:
        print("\n", e, sep="")
