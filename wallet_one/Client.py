import socket
from Wallet import Wallet

def Client():
    host = socket.gethostname()  
    port = 5000 

    client_socket = socket.socket()  
    client_socket.connect((host, port))  

    message = Wallet() 

    while message != None:
        client_socket.send(message)  #sends block here 
        data = client_socket.recv(1024)  

        print('Received from server: ' + data) 

        message = input(" -> ")  

    client_socket.close()  # close the connection


if __name__ == '__main__':
    Client()