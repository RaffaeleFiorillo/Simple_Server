from socket import *
import sys
import thread_server


# displays the content of the received file on the console
def show_on_console(file):
    DIVISION_LINE = "----------------------------------------------------------------"
    # Shows the Response from server (OK or 404)
    print(f"\n{DIVISION_LINE}\n# Response from server: {file[0]}{DIVISION_LINE}")
    print(f"# Content of the file: \n\n{''.join(file[1:-1])}")  # Shows the content of the received file
    return True


# sends a message to the server. This message contains the port where the client will receive the data
def send_connection_request(ip_r, desired_port):
    tcp_client = socket(AF_INET, SOCK_STREAM)
    try:
        # Establish connection to TCP server and exchange data
        tcp_client.connect((ip_r, 80))
        tcp_client.sendall(str(desired_port).encode())
    finally:
        tcp_client.close()


# sends a message to the server asking for a specific file. Then receives the server's response and returns it
def ask_for_file(ip_r, desired_port, desired_file):
    tcp_client = socket(AF_INET, SOCK_STREAM)
    try:
        # Establish connection to TCP server and exchange data
        tcp_client.connect((ip_r, desired_port))
        tcp_client.sendall(f"GET /{desired_file} HTTP/1.1".encode())
    except IOError:
        print("Error")
    files, file = [], ""
    max_it, current = 1000, 0
    while file != "END":
        file = tcp_client.recv(1024).decode()
        files.append(file)
        if max_it <= current:
            files = thread_server.ERROR
            break
        current +=1
    tcp_client.close()
    return files


# establishes the connection with a server on a specified port (handshake) and then asks for a file
def reaction(ip_r, desired_file, desired_port):
    send_connection_request(ip_r, desired_port)  # sends, the server, a connection request for a given port
    file = ask_for_file(ip_r, desired_port, desired_file)  # receive a file from the server
    return show_on_console(file)  # show the file (line per line) on the console


def main():
    try:
        ip = sys.argv[1]  # ip of the server
        port = int(sys.argv[2])  # port where the server wil respond
        file_name= sys.argv[3]  # name of the desired file
        return reaction(ip, file_name, port)
    except IndexError:
        print("Error: Arguments given are not valid")


if __name__ == '__main__':
    # in case of bad connection, the client makes another request for the file, in this case we don't want the output to
    # be shown 2 times, so the variable "has_been_shown" indicates if the file should be shown or not (False)
    has_been_shown = False
    try:
        if not has_been_shown:  # verify if file has already been shown
            has_been_shown = main()  # main will return the correct boolean value of the variable "has_been_shown"
    except ConnectionResetError:
        if not has_been_shown:  # if file has never been shown it will be shown now
            main()
