from socket import *

"""
TCP Client 
"""

# Here we should either provide a string containing either the IP Address of the server or hostname ("cis.poly.edu")
# If we use a hostname, DNS lookup is done automatically
serverName = 'servername'
serverPort = 12000
try:
    # Here we create our socket.
    # AF_INET says to use IPv4. SOCK_STREAM says use TCP. The OS takes care of client port number.
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # Initiates three-way handshake
    clientSocket.connect((serverName, serverPort))

except socket.error as err:
    print("Socket creation failed/n", err)

# Prompts user to write a message to send over socket.
message = input('Want to hear a secret? Enter Yes or No: ')
try:
    # sendto() attaches the destination address to the message and sends the resulting packet into the processes' socket.
    clientSocket.send(message.encode())

    # Client waits to receive data from the server.
    # recvfrom() takes the buffer size 1024 as input.
    modifiedMessage = clientSocket.recvfrom(1024)
except socket.error as err:
    print("An error occurred while sending or receiving data.", err)
# Print modifiedMessage after converting bytes to String.
print('From Server: ', modifiedMessage.decode())

clientSocket.close()
