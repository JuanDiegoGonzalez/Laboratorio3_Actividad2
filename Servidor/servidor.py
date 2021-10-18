import socket, threading, hashlib, time, os, platform, subprocess, ipaddress
from datetime import datetime

# Declaracion de atributos
sock = None
nombreArchivo = None
contenidoArchivo = None
cantConexionesTotales = None
threadsClientes = []
cantidadConectadosYListos = 0
direccionesClientes = []
tiemposDeTransmision = []

def enviarArchivoAlCliente(dirCliente, numCliente):
    # Se envía el id del cliente
    sock.sendto(numCliente.encode(), dirCliente)
    time.sleep(0.2)

    # Se envía la cantidad de conexiones concurrentes
    sock.sendto(str(cantConexionesTotales).encode(), dirCliente)
    time.sleep(0.2)

    # Se envía el nombre del archivo
    sock.sendto(nombreArchivo.encode(), dirCliente)
    time.sleep(0.2)

    inicioTransmision = time.time()

    # Se envía el contenido del archivo
    BUFFER_SIZE = 32768
    inicioFragmento = 0
    finFragmento = BUFFER_SIZE - 1
    while contenidoArchivo[inicioFragmento:finFragmento] != b'':
        sock.sendto(contenidoArchivo[inicioFragmento:finFragmento], dirCliente)
        inicioFragmento += BUFFER_SIZE
        finFragmento += BUFFER_SIZE
        time.sleep(0.000001)

    sock.sendto('Fin'.encode(), dirCliente)
    time.sleep(0.2)

    tiemposDeTransmision[int(numCliente)-1] = time.time() - inicioTransmision
    print("Archivo enviado al cliente ... ", dirCliente)

def escribirLog(tiemposDeTransmision):
    # a.
    fechaStr = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    archivo = open("Logs/{}-log.txt".format(fechaStr), "w")

    # b.
    archivo.write("Nombre del archivo enviado: {}\n".format(nombreArchivo))
    archivo.write("Tamano del archivo enviado: {} bytes\n\n".format(os.path.getsize("ArchivosAEnviar/{}".format(nombreArchivo))))

    # c.
    archivo.write("Clientes a los que se realizo la transferencia:\n")
    for i in range(cantConexionesTotales):
        archivo.write("Cliente {}: {}\n".format(i + 1, direccionesClientes[i]))
    archivo.write("\n")

    '''
    # d.
    archivo.write("Resultados de la transferencia:\n")
    for i in range(cantConexionesTotales):
        archivo.write("Cliente {}: {}\n".format(i + 1, resultComprobacionHash[i]))
    archivo.write("\n")
    '''

    # e.
    archivo.write("Tiempos de transmision:\n")
    for i in range(cantConexionesTotales):
        archivo.write("Cliente {}: {:.2f} segundos\n".format(i + 1, tiemposDeTransmision[i]))
    archivo.write("\n")

    archivo.close()

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
        cantConexionesTotales = int(input("\nIngrese la cantidad de conexiones concurrentes: "))
        if cantConexionesTotales < 1:
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
        tiemposDeTransmision = [None for i in range(cantConexionesTotales)]

        print("\nServidor listo para atender clientes")

        # Se escuchan las peticiones de los clientes (que son las mismas confirmaciones de listo)
        while True:
            request, address = sock.recvfrom(4096)
            print('Se recibio una peticion de {}'.format(address))
            thread = threading.Thread(target=enviarArchivoAlCliente, args=(address, str(len(threadsClientes)+1)))
            threadsClientes.append(thread)
            direccionesClientes.append(address)
            cantidadConectadosYListos += 1

            # Cuando se completa el grupo de clientes, se les envia el archivo y se escribe el log
            if cantidadConectadosYListos == cantConexionesTotales:
                for thread in threadsClientes:
                    thread.start()

                for thread in threadsClientes:
                    thread.join()

                escribirLog(tiemposDeTransmision)

                # Se reinician los atributos
                threadsClientes = []
                direccionesClientes = []
                cantidadConectadosYListos = 0
                tiemposDeTransmision = [None for i in range(cantConexionesTotales)]

    except (FileNotFoundError, ValueError, ConnectionResetError) as e:
        print("\n", e, sep="")