from socket import *

"""
UDP Client 
Code taken from "Computer Networking: A Top Down Approach" By Kurose and Ross
"""

# Here we should either provide a string containing either the IP Address of the server or hostname ("cis.poly.edu")
# If we use a hostname, DNS lookup is done automatically
serverName = 'hostname'
serverPort = 12000
try:
    # Here we create our socket.
    # AF_INET says to use IPv4. SOCK_DGRAM says use UDP. The OS takes care of client port number.
    clientSocket = socket(AF_INET, SOCK_DGRAM)

except socket.error as err:
    print("Socket creation failed/n", err)

# Prompts user to write a message to send over socket.
message = input('Input lowercase sentence: ')

# First converts message from String to byte with encode().
# sendto() attaches the destination address to the message and sends the resulting packet into the processes' socket.
# Source address is also attached to the packet implicitly
clientSocket.sendto(message.encode(), (serverName, serverPort))

# Client waits to receive data from the server.
# Packet's data is put into the modifiedMessage variable and packet's source address is put in serverAddress.
# recvfrom() takes the buffer size 2048 as input. This is usually a good buffer size.
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

# Print modifiedMessage after converting bytes to String.
print(modifiedMessage.decode())

# close socket.
clientSocket.close()
