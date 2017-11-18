from socket import *
import datetime # Used when generating header
import time as time
import email.utils as eut
from rfc822 import parsedate
from time import strftime, gmtime

import pandas as pd

"""
This will be a simple HTTP web cache. It ain't fancy, but it's teaching me a lot about networking.
"""

html = """<html>
<head>
<title>Alex's Server!!</title>
</head>
<body>
The most basic server in the world!
</body>
</html>
"""


# Maximum amount of data we can receive in buffer.
MAX_DATA = 2056

port = 8080     # This is our welcoming socket. There are two sockets created for TCP socket connection.

webPort = 80    # Using port 80 since this server is only for http


# Create a dataframe with the following columns indexed by 'URL'
# I doubt we need to store this much info. 'WebPage' should probably be stored in a dictionary.
# All this data might need to go in dictionaries.
df = pd.DataFrame(columns=['URL', 'LastUpdate', 'WebPage', 'ResponseHeader'], index='URL')


server = socket(AF_INET, SOCK_STREAM)

# Binds the port number to the server's socket, explicitly assigning port number to socket.
server.bind(('', port))

# Tells server to listen for TCP connection requests from client.
server.listen(1)

def queryCache(url):

    # make sure url is in dataframe
    if url in df.index:

        # grab row of values from DataFrame
        row = df.loc(url)
        # Store webPage in variable.
        webPage = row.loc('WebPage')
        lastUpdate = row.loc('LastUpdate')
    else:
        # need to add row to dataframe
        df2 = pd.DataFrame([url, ])
        df.append(ignore_index = False)

    # we will probably return entire row from here.


    return row

def mkResponseHeader(status):
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

def requestPage(url, request):
    # Send request, receive response.
    # This is our http client.

    sock = socket(AF_INET, SOCK_STREAM)

    try:
        print("Requesting page since page isn't in cache yet...\n")
        # create a socket to connect to the web server


        hostIP = gethostbyname(url)
        # connect to webserver
        sock.connect((hostIP, webPort))
        sock.sendall(request)  # send request to webserver

        # Only want to receive the first part of the data.
        while len(data) > 0:
            data = sock.recv(2056)
        sock.close()
    except error, (value, message):
        print("An exeception occurred while trying to get partial data to make header\n")
        if sock:
            sock.close()

        print("socket connection to " + url + " failed", value, message)

    return data

"""Possibly done"""
def parseHeaderAsServer(request):
    # grab user agent info from request
    # create header we're sending in web request
    firstLine = request.split('\n')[0]
    # grab information after GET request (url file)
    urlFile = firstLine.split(' ')[1]

    # use index.dat if the request is "/"

    # depending on the header style, we get FQDN in different ways.
    if "http:" in urlFile:
        fqdn = urlFile # the request has the FQDN in it
        # urFileDrop = "http://"
        removeHttp = urlFile[7:]

        host = removeHttp.split('/')[0] # everything before http://ww.ggo.com/
    else:
        hostIndex = request.find("Host:")
        # slice string from beginning of url to end of string.
        afterHost = request[:hostIndex + 6]
        # split host on blank space and return first value (the host)

        """Might need to split on new line"""
        host = afterHost.split('\n')[0]
        fqdn = host + urlFile

    cookieIndex = request.find("Cookie:")

    if cookieIndex:
        afterCookie = cookieIndex[:cookieIndex + 8]
        """Might need to split on new line"""
        cookie = afterCookie.split('\n')
        ## 8
    else:
        cookie = ''

    return [fqdn, cookie, host]

"""Possibly done"""
def requestLastUpdate(request, hostName):
    # Send request to determine when the last update was.

    print("Requesting last updated time...\n")
    # create a socket to connect to the web server
    sock = socket(AF_INET, SOCK_STREAM)

    # not sure how to
    try:
        hostIP = gethostbyname(hostName)
        # connect to webserver
        sock.connect((hostIP, webPort))
        sock.sendall(request)  # send request to webserver

        # Only want to receive the first part of the data.
        while True:
            data = sock.recv(2056)
            if len(data) > 2000:
                break

        sock.close()
    except error, (value, message):
        print("An exeception occurred while trying to get partial data to make header\n")
        if sock:
            sock.close()

        print("socket connection to " + hostName + " failed", value, message)


    # convert received data to a string
    receivedPage = str(data)

    print("Here's the data that was received from requestLastUpdate")
    print(receivedPage)

    # take response and put it in lastUpdateValue
    (lastUpdate, lastUpdateValue) = parseLastUpdate(response)

    lastUpdateBool = False

    urlRow = df.loc['URL']

    if lastUpdateValue < urlRow['LastUpdate']: #compare dates and we don't have most recent
        df.replace(urlRow.loc['LastUpdate'], lastUpdateValue, inplace=True)
        lastUpdateBool = True

    return (lastUpdate, lastUpdateBool)

"""Possibly done"""
def parseLastUpdate(response):
    # grab lastUpdate from response

    print("Attempting to parse last-modified data\n")

    updateIndex = response.find("Last-Modified:")
    # 15
    modLine = response[:updateIndex + 15]
    lastModDateTime = modLine.split('\n')[0]

    # parse date
    parsedDate = parsedate(lastModDateTime)
    try:
        exactTime = time.mktime(parsedDate)
    except TypeError:
        print("Couldn't parse date into the proper time format.")

    # make sure datetime format is the same.
    return (lastModDateTime, exactTime)

def requestAndParsePage(request, host):
    # request the page (request, host).
    data = requestPage(request, host)
    # split the header on beginning of html
    splitData = data.split('<!')
    header = splitData[0]
    content = '<!' + splitData[1]

    return header, content

def runProgram(conn, addr):
    request = conn.recv(2056)

    # return (fqdn, cookie, host)
    parsedHeader = parseHeaderAsServer(request)

    lastUpdateBool = False
    cachedPage = False

    # check if url is already in the dataframe
    if parsedHeader[0] in df:
        # Determine the last update time (time, lastUpdateBool)
        (lastUpdate, lastUpdateBool) = requestLastUpdate(request, parsedHeader[2])
        cachedPage = True

    # if the page has been updated
    if lastUpdateBool:
        # Request full page 
        (header, content) = requestAndParsePage(request, parsedHeader[2])
        
        # Update the cache 
        
        # send the page on to client 
        


    # if the page is already cached and doesn't need to be updated.
    elif cachedPage:
        row = df.loc(parsedHeader[0])

        content = row['ResponseHeader'] + row['Content']  # request the page

        # send page back to the client
        # parse last modified time from header
        # create new row in dataframe
        # store data from rows in dataframe

    # if the page is not in cache
    else:  # append header to content

        # get header and full page content
        header, content = requestAndParsePage(request, parsedHeader[2])
        # parse lastUpdate info from header
        lastUpdate, dateTime = parseLastUpdate(header)

        # store the page in the dataframe (or whatever we put it in)
        df.append([parsedHeader[0], lastUpdate, dateTime, content, header],
                  columns=['URL', 'LastUpdate', "LastUpdateValue", "Content", "ResponseHeader"])

        # parse the date
        # change the date in the dataframe

        
    print("Request: ", firstLine, url )

    """
    Sample Response: 
    
HTTP/1.1 200 OK\n
Cache-Control: private, max-age=0\n
Content-Type: text/html; charset=utf-8\n
Expires: Wed, 01 Nov 2017 16:55:24 GMT\n
Last-Modified: Thu, 16 Nov 2017 17:55:24 GMT\n
Server: Microsoft-IIS/8.5\n
X-SharePointHealthScore: 0\n
X-AspNet-Version: 4.0.30319\n
SPRequestGuid: 57822d9e-5e00-204d-f2e7-25f7c67ce392\n
request-id: 57822d9e-5e00-204d-f2e7-25f7c67ce392\n
X-FRAME-OPTIONS: SAMEORIGIN\n
SPRequestDuration: 708\n
SPIisLatency: 0\n
Set-Cookie: SPUsageId=2e397f36-dc67-46a2-891a-40f79a038e9a; expires=Thu, 30-Nov-2017 17:55:25 GMT; path=/; HttpOnly\n
X-Powered-By: ASP.NET\n
MicrosoftSharePointTeamServices: 15.0.0.4709\n
X-Content-Type-Options: nosniff\n
X-MS-InvokeApp: 1; RequireReadOnly\n
Date: Thu, 16 Nov 2017 17:55:24 GMT\n
Content-Length: 141184\n
Set-Cookie: NSC_OFX-jij.psh-tibsfqpjou-IUUQ=ffffffff09bcb60a45525d5f4f58455e445a4a423660;expires=Thu, 16-Nov-2017 18:14:44 GMT;path=/;httponly\n
\n\n
    """


print("\nThe server is ready to receive HTTP GET requests.")


"""THIS IS OLD CODE."""
while True:
    # This is the exclusive socket for client.
    connectionSocket, addr = server.accept()
    runProgram(connectionSocket, addr)
    # receives message and clientAddress. All bytes are both guaranteed to arrive and to arrive in order.
    # message = connectionSocket.recv(999999)
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

    # server takes the String converted to uppercase, converts it to bytes, and sends it back to client.
    print("Printing Response:")
    print(response)
    connectionSocket.sendall(response.encode())

    # Close socket connection. However, the serverSocket connection remains open.
    connectionSocket.close()  # different than UDP
