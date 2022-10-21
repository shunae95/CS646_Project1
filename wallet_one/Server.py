import socket

def Server():
    host = socket.gethostname()
    port = 5000  
    server_socket = socket.socket()  
    server_socket.bind((host, port))  

    server_socket.listen(10)
    conn, address = server_socket.accept()  
    print("Connection from: " + str(address))
    while True:

        data = conn.recv(1024)
        if not data:
            break
        print("from connected user: " + str(data))
        data = input(' -> ')
        conn.send(data.encode()) 

    conn.close() 


if __name__ == '__main__':
    Server()
