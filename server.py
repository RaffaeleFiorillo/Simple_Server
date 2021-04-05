# Import socket module
from socket import *


def print_block(line, initial=False, final=False):
    DIVISION_LINE = "\n----------------------------------------------------------------"
    if initial:  # checks if the line is the initial line, if so, it prints a DIVISION_LINE to indicate it is initial
        print(DIVISION_LINE)
    print(" -->  "+line)
    if final:  # checks if the line is the final line, if so, it prints a DIVISION_LINE to indicate it is final
        print(DIVISION_LINE)


# Receive an initialized socket and listens to possible client connections
def listen(server_socket):
    print('# -- The server is listening -- #')
    connection_Socket, address = server_socket.accept()
    return connection_Socket, address


# Create a TCP server socket
# (AF_INET is used for IPv4 protocols)
# (SOCK_STREAM is used for TCP)

serverSocket = socket(AF_INET, SOCK_STREAM)

# Assign a port number
serverPort = 80  # 6789

# Bind the socket to server address and server port

serverSocket.bind(("127.8.8.8", serverPort))  # the server listens on the port 80 with the ip 127.8.8.8

# Listen to at most 5 connection at a time
serverSocket.listen(5)

# sometimes a connection is just for the client to communicate that he received a response, this kind of connection can
# be skipped
skip_connection = False

# Server should be up and running and listening to the incoming connections
while True:
    if skip_connection:
        skip_connection = not skip_connection
        continue
    # Set up a new connection from the client
    connectionSocket, addr = listen(serverSocket)
    print_block(f"Connection established with address: {addr[0]} on Port: {addr[1]}", initial=True)
    # If an exception occurs during the execution of try clause
    # the rest of the clause is skipped
    # If the exception type matches the word after except
    # the except clause is executed
    try:
        # Receives the request message from the client
        message = connectionSocket.recv(1024).decode()
        if message == "":  # make sure that the message is not empty so that it doesn't throw an error
            print_block("Just a useless connection (Client sent empty message)")
            print_block("Connection with client has been closed", final=True)
            continue
        print_block("GET request received")
        # Extract the path of the requested object from the message
        # The path is the second part of HTTP header, identified by [1]
        # Also, because the extracted path of the HTTP request includes a character '\',
        # we read the path from the second character
        filename = message.split()[1][1:]
        print_block(f"Searching for file: {filename}")
        f = open(filename)
        print_block(f"File: {filename} - found!")
        # Store the entire contenet of the requested file in a temporary buffer
        outputdata = f.read()
        # Send the HTTP response header line to the connection socket
        connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        print_block("HTTP response header sent to client")
        # Send the content of the requested file to the connection socket
        print_block("Sending the content of the requested file to the client - STARTED")
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        print_block("Sending the content of the requested file to the client - COMPLETED")
        # Close the client connection socket
        connectionSocket.close()
        print_block("Connection with client has been closed", final=True)

    except IOError:
        print_block(f"Error: File: {filename} NOT FOUND!!!")
        # Send HTTP response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        print_block("Client informed of the Error")
        # Close the client connection socket
        connectionSocket.close()
        print_block("Connection with client has been closed", final=True)


serverSocket.close()
exit()  # Terminate the program after sending the corresponding data
