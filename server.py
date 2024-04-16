import os
import ssl
import threading
from socket import *
from cryptography.fernet import Fernet

def authenticate(username, password):
    try:
        if os.path.exists(f"C:/Non-Software/Coding_Things/CN/Mini_Project/{username}"):
            os.chdir('C:/Non-Software/Coding_Things/CN/Mini_Project/database')
            with open(f"password_{username}.txt", 'rb') as file:
                encrypted_pass = file.read()
                with open(f"key_{username}.txt", 'rb') as key_file:
                    key = key_file.read()
                    cypher_suite = Fernet(key)
                    plain_password = cypher_suite.decrypt(encrypted_pass).decode()
                    if plain_password == password:
                        authentication = True
                    else:
                        authentication = False
            # parent_dir = os.path.dirname(os.getcwd())
            # os.chdir(parent_dir)
            return authentication
        else:
            os.mkdir(f"C:/Non-Software/Coding_Things/CN/Mini_Project/{username}")
            print("Created directory: ", username)
            os.chdir('C:/Non-Software/Coding_Things/CN/Mini_Project/database')
            key = Fernet.generate_key()
            with open(f"key_{username}.txt",'wb') as key_file:
                key_file.write(key)
                
            cypher_suite = Fernet(key)
            encrypted_password = cypher_suite.encrypt(password.encode())
            with open(f"password_{username}.txt", 'wb') as pass_file:
                pass_file.write(encrypted_password)
            # parent_dir = os.path.dirname(os.getcwd())
            # os.chdir(parent_dir)
            return True
    except:
        print("No username Entered\r\n")
    
    
def handleclient(connectionSocket, addr):
    print("Connection from ", addr)
    username = connectionSocket.recv(1024).decode()
    password = connectionSocket.recv(1024).decode()
    print(f"Checking Authentication for {addr}")
    authentication = authenticate(username, password)
    if authentication:
        connectionSocket.send("Authenticated!".encode())
        print("Authenticated!\r\n")
        os.chdir(f"C:/Non-Software/Coding_Things/CN/Mini_Project/{username}")
        try:
            while True:
                command = connectionSocket.recv(1024).decode().strip()

                if not command:
                    break
                
                if command == "QUIT":
                    print(f"Terminating connection {addr}\r\n")
                    break
                
                elif command == "LIST":
                    files = os.listdir('.')
                    print(f"Listed files to {addr}\r\n")
                    connectionSocket.send(f"The List of Files in the {os.getcwd()} Directory are:\r\n".encode())
                    for file in files:
                        connectionSocket.send((file + '\r\n').encode())
                    connectionSocket.send("EOF\r\n".encode())
                    
                elif command.startswith("DOWNLOAD"):
                    try:
                        temp, filename = command.split(' ', 1)
                        print(f"Sending {filename} to {addr}")
                        with open(filename, 'rb') as file:
                            while True:
                                data = file.read(1024)
                                if not data:
                                    connectionSocket.send(b"EOF\r\n")
                                    break
                                connectionSocket.send(data)
                    except ValueError as e:
                        print(f"Exception occurred: {e}\r\n")
                    except Exception as e:
                        print(f"Exception occurred: {e}\r\n")
                        connectionSocket.send(b"FILE NOT FOUND\r\n")
                        
                elif command.startswith("UPLOAD"):
                    try:
                        temp, filename = command.split(' ',1)
                        print(f"Recieving {filename} from {addr}")
                        with open(filename, 'wb') as file:
                            while True:
                                data = connectionSocket.recv(1024)
                                if b"EOF\r\n" in data:
                                    connectionSocket.send("File Uploaded Successfully".encode())
                                    print(f"Recieved {filename}\r\n")
                                    data = data.replace(b"EOF\r\n", b"")
                                    file.write(data)
                                    break
                                file.write(data)
                    except ValueError as e:
                        print(f"Exception occured: {e}\r\n")
                    except Exception as e:
                        print(f"Exception occured: {e}\r\n")
                        connectionSocket.send(f"Error in Uploading file: {e}".encode())
        except Exception as e:
            print(f"Client Connection {addr} Terminated!\r\n")
            print(f"{e}")
            
        parent_dir = os.path.dirname(os.getcwd())
        os.chdir(parent_dir)
    else:
        connectionSocket.send("Not Authenticated!".encode())
        print("Not Authenticated!\r\n")

def startServer(ssl_socket):
    while True:
        print('The server is ready for connections!\r\n')
        connectionSocket, addr = ssl_socket.accept()
        # threading.Thread(target=handleclient, args=(connectionSocket, addr)).start()
        handleclient(connectionSocket, addr)
        connectionSocket.close()
                
    
serverPort = 6000
serverSocket = socket(AF_INET,SOCK_STREAM)
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile="server_new.cer", keyfile="server.key")
ssl_socket = ssl_context.wrap_socket(serverSocket, server_side=True)
ssl_socket.bind(('192.168.248.235', serverPort))
ssl_socket.listen(5)

startServer(ssl_socket)    