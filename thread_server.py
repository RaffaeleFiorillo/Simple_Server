from socket import *
import threading
import random

EX_FILES = ["ArqRedes.html", "Example_File_1.html", "Example_File_2.html", "Example_File_3.html"]
ERROR = ["HTTP/1.1 404 Not Found\r\n\r\n", "<html>\n\r<head>\n\r</head>\n\r\r<body>\n\r\r\r<h1>404 Not Found</h1>\n\r\r"
         "</body>\n</html>\r\n", "END"]


# Creates and returns a new socket and binds it to a given port
def create_socket(port):
    new_socket = socket(AF_INET, SOCK_STREAM)
    new_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    new_socket.bind(('127.8.8.8', int(port)))
    return new_socket


# main execution sequence
def main():
    server = Main_Thread(80)  # initialize a server that listens on the port 80
    server.daemon = 1  # setting daemon to 1
    server.start()  # start the server
    input()  # to stop execution from ending
    print("\n----- Server execution terminated -----")  # inform user that the server has stopped
    exit()  # end execution of the program


# This class works as a listening server. Every time it receives a new request, it creates a new threads and leads with
# it. After each request, it cleans the threads that have been closed in order not to occupy to much memory
class Main_Thread(threading.Thread):
    def __init__(self, server_port):
        self.last_thread_id = 0  # represents the id of the last thread, so that every thread has a different id
        threading.Thread.__init__(self)
        self.server_port = server_port  # server port where it listens to new requests
        self.serverSocket = create_socket(self.server_port)  # socket where the Clients make requests
        self.connectionThreads = []  # list of all the threads
        self.known_ports = []  # already seen ports

    def run(self):
        self.serverSocket.listen(1)  # makes the socket listen to Clients
        dangerous = False  # Identifies if a port is secure or not
        while True:
            # Establish the connection
            print('\n------ Server is listening ------\n')
            connectionSocket, address = self.serverSocket.accept()  # Receive Requests
            message = connectionSocket.recv(1024).decode()  # Get message  (with connection port)
            print(f"\n -> Received request for connection on port: {message} from ip: {address[0]}")
            if message == "":
                print("\n -> Ignoring empty message")
                continue
            elif message not in self.known_ports:  # this means that a port is not secure
                dangerous = True
            self.connectionThreads.append(connectionThread(create_socket(message), self.last_thread_id, dangerous))
            self.last_thread_id += 1  # increment the id for the next possible thread
            self.connectionThreads[-1].daemon = 1
            self.connectionThreads[-1].start()  # start new created thread in order to serve the client on defined port
            self.close_finished_threads()  # remove all the threads that have done their work
            print(f"\n -> Connecting with client on port: {message} in a new thread")
            dangerous = False  # resets the state of the port for the next iteration

    # cleans the thread list from all the threads that have been closed
    def close_finished_threads(self):
        opened_threads = []
        for i in range(len(self.connectionThreads)):
            if self.connectionThreads[i].finished:
                print(f" -> Thread: {self.connectionThreads[i].t_id} has been closed")
                self.connectionThreads[i].join()
            else:
                opened_threads.append(self.connectionThreads[i])
        self.connectionThreads = opened_threads


# this class makes a new connection for a client on a specific port, and then he sends a file
# that the client has requested (in case he finds it, otherwise it sends the 404 code)
class connectionThread(threading.Thread):
    def __init__(self, i_socket, t_id, dangerous):
        threading.Thread.__init__(self)
        self.thread_socket = i_socket  # the thread socket where the connection will be established
        self.message = None  # initialize a message
        self.finished = False  # tells if this thread has finished or not
        self.t_id = t_id  # id of this thread
        self.state = dangerous  # tells if it is a dangerous thread

    # in case of exception it sends the 404 error
    def exception_throw(self, cs, file_name):
        cs.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        cs.send("<html>\n\r<head>\n\r</head>\n\r\r<body>\n\r\r\r<h1>404 Not Found</h1>\n\r\r"
                "</body>\n</html>\r\n".encode())
        cs.send("END".encode())
        print(f"    --> Client: {self.t_id} has been informed that file: {file_name} have not been found")

    def run(self):
        self.thread_socket.listen(1)
        try:
            connectionSocket, address = self.thread_socket.accept()  # accept connection
            self.message = connectionSocket.recv(1024).decode()  # Get message
            filename = self.message.split()[1][1:]  # Getting requested HTML page
            print(f"    --> Client: {self.t_id} is requesting file: {filename}")
            if filename not in EX_FILES and self.state:
                self.exception_throw(connectionSocket, filename)
            else:
                f = open(filename)  # Opening data stream from HTML
                output_data = f.readlines()  # Reading HTML page
                f.close()  # Closing data stream from HTML
                connectionSocket.send("HTTP/1.0 200 OK\r\n\r\n".encode())  # Send one HTTP header line into socket
                for line in output_data:  # Send the content of the requested file to the client
                    connectionSocket.send(line.encode())
                connectionSocket.send("\r\n".encode())
                connectionSocket.send("END".encode())
                print(f"    --> {filename} has been sent to Client: {self.t_id}")
        except IOError:  # Triggered if user requests bad link
            # Send response message for file not found
            connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
            connectionSocket.send("<html>\n\r<head>\n\r</head>\n\r\r<body>\n\r\r\r<h1>404 Not Found</h1>\n\r\r"
                                  "</body>\n</html>\r\n".encode())
            connectionSocket.send("END".encode())
            print("    --> Client: {self.t_id} has been informed that file: {file_name} have not been found")
        connectionSocket.shutdown(SHUT_RDWR)
        connectionSocket.close()
        self.finished = True
        print(f"    --> Request for Client: {self.t_id} has been completed")
        print('\n------ Server is listening ------\n')


if __name__ == "__main__":
    main()
