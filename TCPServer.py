from socket import *

"""
This code does not handle exceptions. 
"""

# Determine port number to use
serverPort = 12000

# Here we create our socket.
# This is our welcoming socket. There are two sockets created for TCP socket connection.
serverSocket = socket(AF_INET, SOCK_STREAM)

# Binds the port number to the server's socket, explicitly assigning port number to socket.
# Any packet that sends a message to port 12000 will be automatically directed to this socket.
serverSocket.bind(('', serverPort))

# Tells server to listen for TCP connection requests from client.
serverSocket.listen(1)

print("The server is ready to receive.")

# while loop allows UPDServer to receive and process packets from clients indefinitely.
# the server is always waiting to receive messages.
while True:
    # This is the exclusive socket for client.
    connectionSocket, addr = serverSocket.accept()

    # receives message and clientAddress. All bytes are both guaranteed to arrive and to arrive in order.
    message = serverSocket.recvfrom(2048).decode()
    # converts from byte to String and makes uppercase
    capitalizedMessage = message.upper()

    if capitalizedMessage == 'YES':
        response = "I think Beth and I should go on vacation for a month once we finally get to be together./n" \
                   "And we should get a dog. She can choose the breed. I'll train it and deal with the poop."
    elif capitalizedMessage == 'NO':
        response = "You're super boring. Why you wasting my server's time?/nBitch!"
    else:
        response = "You suck at typing. You gave an invalid response. You also suck at life."
    # server takes the String converted to uppercase, converts it to bytes, and sends it back to client.
    serverSocket.sendto( response.encode() )

    # Close socket connection. However, the serverSocket connection remains open.
    connectionSocket.close() #different than UDP
