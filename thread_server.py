from socket import *
import threading


class serverThread(threading.Thread):
    def __init__(self, server_port):
        self.last_thread_id = 0
        threading.Thread.__init__(self)
        self.server_port = server_port
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.connectionThreads = []

    def run(self):
        self.serverSocket.bind(('', self.server_port))
        self.serverSocket.listen(1)
        while True:
            print(f"Active Threads: {len(self.connectionThreads)}")
            # Establish the connection
            print('Ready to serve...')
            connectionSocket, addr = self.serverSocket.accept()
            message = connectionSocket.recv(1024).decode()  # Get message
            if message == "":
                print("Ignoring empty message")
                continue
            print("Message recieved, opening new thread")
            self.connectionThreads.append(connectionThread(connectionSocket, message, self.last_thread_id))
            self.last_thread_id += 1  # increment the id for the next possible thread
            self.connectionThreads[-1].daemon = 1
            self.connectionThreads[-1].start()
            self.close_finished_threads()  # remove all the threads that have done their work

    def close_finished_threads(self):
        for t in self.connectionThreads:
            if t.finished:
                print(f"Thread: {t.t_id} has been closed")
                self.connectionThreads.remove(t)


class connectionThread(threading.Thread):
    def __init__(self, conn_socket, message, t_id):
        threading.Thread.__init__(self)
        self.conn_socket = conn_socket
        self.message = message
        self.finished = False
        self.t_id = t_id

    def run(self):
        try:
            filename = self.message.split()[1]  # Getting requested HTML page
            f = open(filename[1:])  # Opening data stream from HTML
            output_data = f.read()  # Reading HTML page
            f.close()  # Closing data stream from HTML
            self.conn_socket.send("HTTP/1.0 200 OK\r\n\r\n".encode())  # Send one HTTP header line into socket
            for i in range(0, len(output_data)):  # Send the content of the requested file to the client
                self.conn_socket.send(output_data[i].encode())
            self.conn_socket.send("\r\n".encode())
        except IOError:  # Triggered if user requests bad link
            # Send response message for file not found
            self.conn_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
            self.conn_socket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        finally:
            self.conn_socket.shutdown(SHUT_RDWR)
            self.conn_socket.close()
            self.finished = True


def main():
    server = serverThread(80)  # initialize a server that listens on the port 80
    server.daemon = 1  # setting daemon to 1
    server.start()  # start the server
    input()  # to stop execution from ending
    print("Server execution terminated")  # infrom user that the server has stopped
    exit()  # end execution of the program


main()
