import ssl
from socket import *


def authenticate(clientSocket):
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    clientSocket.send(username.encode())
    clientSocket.send(password.encode())
    authentication = clientSocket.recv(1024).decode()
    print(authentication + "\r\n")
    return authentication
    

serverName = '192.168.248.235'
serverPort = 6000
clientSocket = socket(AF_INET, SOCK_STREAM)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_socket = ssl_context.wrap_socket(clientSocket)
ssl_socket.connect((serverName, serverPort))


authentication = authenticate(ssl_socket)
if authentication == "Authenticated!":
    try:
        while True:
            command = input("Enter a command: ")
            ssl_socket.send(command.encode())
            
            if command == "QUIT":
                ssl_socket.close()
                break
            
            elif command == "LIST":
                print("\r\n")
                recieved_data = ''
                while True:
                    data = ssl_socket.recv(1024).decode()
                    recieved_data += data
                    if "EOF\r\n" in recieved_data:
                        break
                lines = recieved_data.split('\r\n')
                
                if len(lines) == 3:
                    print("Your Directory is Empty!\r\n")
                else:
                    for line in lines[:-2]:
                        print(line)
                    
            elif command.startswith("DOWNLOAD"):
                try:
                    temp, filename = command.split(' ',1)
                    data = ssl_socket.recv(1024)
                    if data == b"FILE NOT FOUND\r\n":
                        print(data.decode())
                        continue
                    with open(filename,'wb') as file:
                        while True:
                            if b"EOF\r\n" in data:
                                print("File Downloaded Successfully")
                                data = data.replace(b"EOF\r\n", b"")
                                file.write(data)
                                break
                            file.write(data)
                            data = ssl_socket.recv(1024)
                except ValueError:
                    print("Please input filename along with the command")
                except Exception as e:
                    print(f"Exception occurred: {e}")

                    
            elif command.startswith("UPLOAD"):
                try:
                    temp, filename = command.split(' ',1)
                    with open(filename, 'rb') as file:
                        while True:
                            data = file.read(1024)
                            if not data:
                                ssl_socket.send(b"EOF\r\n")
                                break
                            ssl_socket.send(data)
                    message = ssl_socket.recv(1024).decode()
                    print(message)
                except ValueError:
                    print("Please input filename along with the command")
                except Exception as e:
                    print(f"Exception occured: {e}")
                    
            else:
                print("Unknown Command")
                    
            print("\r\n")

    except Exception as e:
        print("Server Closed Connection!")
        print(f"{e}")
else:
    print("Closing Connection!")
