from socket import *

"""
This code does not handle exceptions. 
Code taken from "Computer Networking: A Top Down Approach" By Kurose and Ross
"""

# Determine port number to use
serverPort = 12000

# Here we create our socket.
# AF_INET says to use IPv4. SOCK_DGRAM says use UDP. The OS takes care of client port number.
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Binds the port number to the server's socket, explicitly assigning port number to socket.
# Any packet that sends a message to port 12000 will be automatically directed to this socket.
serverSocket.bind(('', serverPort))

print("The server is ready to receive.")

# while loop allows UPDServer to receive and process packets from clients indefinitely.
# the server is always waiting to receive messages.
while True:
    # receives message and clientAddress
    message, clientAddress = serverSocket.recvfrom(2048)
    # converts from byte to String and makes uppercase
    modifiedMessage = message.decode().upper()
    # server takes the String converted to uppercase, converts it to bytes, and sends it back to client.
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
