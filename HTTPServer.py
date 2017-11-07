from socket import *
# import datetime # Used when generating header
from time import strftime, gmtime

"""
This will be a simple HTTP server that only handles GET requests. 
There isn't much to it, but it's not done yet. 
"""

port = 8018     # This is our welcoming socket. There are two sockets created for TCP socket connection.

# How does the server know it's name?

html = """<html>
<head>
<title>Alex's Server!!</title>
</head>
<body>
The most basic server in the world!
</body>
</html>
"""

server = socket(AF_INET, SOCK_STREAM)

# Binds the port number to the server's socket, explicitly assigning port number to socket.
server.bind(('', port))

# Tells server to listen for TCP connection requests from client.
server.listen(1)

def mkHeader(status):
    new_time = strftime("Date: %a, %d %b %Y %H:%M:%S GMT", gmtime())

    # length of the string in bytes (not the string object)
    length = len(html.encode('utf-8'))

    # head = status + "\r\nContent Type: text/html" + "\r\n\r\n"
    head = status + "Connection: close\n" + "Date: " + new_time +  "\nServer: Simple Python Server\n" + \
           "Last modified: Tue, 7 Nov 2017 14:03:00 GMT\n" + "Content Length: " + str(length) + \
           "\nContent Type: text/html" + "\n\n"

    # here's where we make the header for our response.
    # We need a way to pass values here that determine which header.
    return head

print("\n\rThe server is ready to receive HTTP GET requests.")

while True:
    # This is the exclusive socket for client.
    connectionSocket, addr = server.accept()
    # receives message and clientAddress. All bytes are both guaranteed to arrive and to arrive in order.
    message = connectionSocket.recv(2048)
    message_str = str(message)
    print("Print Message received")
    print(message_str[1:])
    # decoded = message.decode()

    # Split header into list of lines
    header_lines = message_str[2:]
    print("Printing header lines..\n")
    print(header_lines)
    # split first line on white space.

    split_head = header_lines.split()
    print("Printing split_head\n")
    print(str(split_head))

    # check and make sure status line is for a GET request.
    if split_head[0] == 'GET':
        # We have no files so this is the only page that doesn't throw error.
        if split_head[1] == '/':
            # we are going to the index page.
            # need to call mkHeader() to make a response and append html onto it.
            status_response = 'HTTP/1.1 200 OK\n'
            header = mkHeader(status_response)
            response = header + html

            # ADD SOMETHING ONTO HEADER
        elif split_head == "index.dat":
            # we are going to the index page.
            # need to call mkHeader() to make a response and append html onto it.
            status_response = 'HTTP/1.1 200 OK\n'
            header = mkHeader(status_response)
            response = header + html
        else:
            status_response = 'HTTP/1.1 404 Not Found\n'
            # header = mkHeader(status_response)
            response = status_response
            # ADD SOMETHING ON TO HEADER
    else:
        status_response = 'HTTP/1.1 400 Bad Request\n'
        header = mkHeader(status_response)
        response = header
        # ADD SOMETHING ON TO HEADER

    # server takes the String converted to uppercase, converts it to bytes, and sends it back to client.
    print("Printing Response:")
    print(response)
    connectionSocket.sendall(response.encode())

    # Close socket connection. However, the serverSocket connection remains open.
    connectionSocket.close()  # different than UDP
