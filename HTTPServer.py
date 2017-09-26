from socket import *
import datetime # Used when generating header

"""
This will be a simple HTTP server that only handles GET requests. 
There isn't much to it, but it's not done yet. 
"""

port = 80     # This is our welcoming socket. There are two sockets created for TCP socket connection.

# How does the server know it's name?

server = socket(AF_INET, SOCK_STREAM)
# Binds the port number to the server's socket, explicitly assigning port number to socket.
server.bind(('', port))
# Tells server to listen for TCP connection requests from client.
server.listen(3)

def mkHeader(status):
    date = datetime
    header = status + "Other stuff"
    # here's where we make the header for our response.
    # We need a way to pass values here that determine which header.
    return header

print("The server is ready to receive HTTP GET requests.")

while True:
    # This is the exclusive socket for client.
    connectionSocket, addr = server.accept()
    # receives message and clientAddress. All bytes are both guaranteed to arrive and to arrive in order.
    message = server.recvfrom(2048).decode()

    # Split header into list of lines
    header_lines = message.splitlines
    # split first line on white space.
    split_head = header_lines[0].split(' ')

    # check and make sure status line is for a GET request.
    if(split_head[0] == 'GET'):
        # We have no files so this is the only page that doesn't throw error.
        if split_head[1] == '/':
            # we are going to the index page.
            # need to call mkHeader() to make a response and append html onto it.
            status_response = 'HTTP/1.1 200 OK\r\n'
            header = mkHeader(status_response)
            response = header + "HTML!!!! "

            # ADD SOMETHING ONTO HEADER
        else:
            status_response = 'HTTP/1.1 404 Not Found\r\n'
            header = mkHeader(status_response)
            response = header + "HTML!!!!!"
            # ADD SOMETHING ON TO HEADER
    else:
        status_response = 'HTTP/1.1 404 Not Found\r\n'
        header = mkHeader(status_response)
        response = header + "HTML!!!!!!!!!"
        # ADD SOMETHING ON TO HEADER


    # Need to append message onto header

    # server takes the String converted to uppercase, converts it to bytes, and sends it back to client.
    server.sendto(response.encode())

    # Close socket connection. However, the serverSocket connection remains open.
    connectionSocket.close()  # different than UDP
