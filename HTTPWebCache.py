from socket import *
import datetime # Used when generating header
# import time as time
# from rfc822 import parsedate
from time import strftime, gmtime
import pandas as pd
import hashlib as hashlib
import os as os

"""
This will be a simple HTTP web cache. It ain't fancy, but it's teaching me a lot about networking.

I realize that it's weird to write this with dataframes, but I did it anyways because if you don't 
lose it, you lose it. I don't spend enough time with pandas as I should.
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

# create directory to store binary web pages.
if not os.path.exists('binary_pages'):
    os.makedirs('binary_pages')

# Create a dataframe with the following columns indexed by 'url'
# I doubt we need to store this much info. 'webpage' should probably be stored in a dictionary.
# All this data might need to go in dictionaries.
df = pd.DataFrame(columns=['url', 'last_update', 'last_update_value', 'page_hash', 'response_header'])

server = socket(AF_INET, SOCK_STREAM)

# Binds the port number to the server's socket, explicitly assigning port number to socket.
server.bind(('', port))

# Tells server to listen for TCP connection requests from client.
server.listen(1)

# def queryCache(url):
# # make sure url is in dataframe
#    if url in df.index:
#
#        # grab row of values from DataFrame
#        row = df.loc(url)
#        # Store webpage in variable.
#        webpage = row.loc('webpage')
#        last_update = row.loc('last_update')
#    else:
#        # need to add row to dataframe
#        df2 = pd.DataFrame([url, ])
#        df.append(ignore_index = False)
#
#    # we will probably return entire row from here.
#
#    return row


# write page to file. Return full name to store in dataframe.
def write_page(response):
    page_hash = hashlib.md5(response)
    full_name = 'binary_pages/' + page_hash + '.bin'

    print('Attempting to write binary page to file as ' + full_name)

    with open(full_name, 'wb') as file:
        file.write(response)

    return full_name


# this is not used in the cache.
def mk_response_header(status):
    new_time = strftime("Date: %a, %d %b %Y %H:%M:%S GMT", gmtime())

    # length of the string in bytes (not the string object)
    length = len(html.encode('utf-8'))

    # head = status + "\r\ncontent Type: text/html" + "\r\n\r\n"
    head = status + "Connection: close\n" + "Date: " + new_time +  "\nServer: Simple Python Server\n" + \
           "Last modified: Tue, 7 Nov 2017 14:03:00 GMT\n" + "content Length: " + str(length) + \
           "\ncontent Type: text/html" + "\n\n"

    # here's where we make the header for our response.
    # We need a way to pass values here that determine which header.
    return head


# Request full page. Only supports IPv4 for now.
def request_page(request, host):
    # Send request, receive response.
    # This is our http client.

    sock = socket(AF_INET, SOCK_STREAM)
    print('Printing host in request_page()', host)

    try:
        print("Requesting page since page isn't in cache yet...\n")

        # create a socket to connect to the web server
        print('the host is', host)
        host_ip = gethostbyname(host)
        print('the host ip is,', host_ip)
        sock.connect((host_ip, webPort))

        # send request to webserver
        sock.sendall(request)
        # receive response from webserver
        data = sock.recv(2056)

        # while True:
        #    data = sock.recvfrom(2056)
        #    if len(data) <= 0:
        #        break

        print('Received data:\n', str(data))
        sock.close()
    except error:
        print("An exception occurred while trying to get partial data to make header\n")
        if sock:
            sock.close()
        print("socket connection to " + host + " failed" + str(error))

    return data


# Gets data we need from server. And some extras.
def parse_header_server(request):

    print('Printing request', request)
    # grab user agent info from request
    # create header we're sending in web request
    first_line = request.split('\n')[0]

    # grab information after GET request (url file)
    url_file = first_line.split(' ')[1]

    # use index.dat if the request is "/"

    # depending on the header style, we get FQDN in different ways.
    if "http:" in url_file:
        fqdn = url_file # the request has the FQDN in it
        # urFileDrop = "http://"
        remove_http = url_file[7:]

        host = remove_http.split('/')[0] # everything before http://ww.ggo.com/
    else:
        host_index = request.find("Host:")
        # slice string from beginning of url to end of string.
        after_host = request[:host_index + 6]
        # split host on blank space and return first value (the host)

        """Might need to split on new line"""
        host = after_host.split('\n')[0]
        fqdn = host + url_file
        print('the new host is:', host)
        print('The fqdn is:', fqdn)

    print('The final host is', host)
    print('The final fqdn is', fqdn)
    return fqdn, host


# Send request to determine when the last update was.
def request_last_update(request, host_name):

    print("Requesting last updated time...\n")
    # create a socket to connect to the web server
    sock = socket(AF_INET, SOCK_STREAM)

    try:
        host_ip = gethostbyname(host_name)
        print('the host_ip is', host_ip)
        # connect to webserver
        sock.connect((host_ip, webPort))
        header = str(request).replace('GET', 'HEAD', 1)
        print('request_last_update() header:', header)
        sock.sendall(header.encode())  # send request to webserver

        # Only want to receive the first part of the data.
        print('receiving header')
        while True:
            data = sock.recv(2056)
            if len(data) <= 0:
                break

        sock.close()

    # Can throw socket.timeout or InterruptedError
    except error:
        print("An exception occurred while trying to get the header\n")
        if sock:
            sock.close()

        print("socket connection to " + host_name + " failed")

    # convert received data to a string
    response = str(data)

    print("Here's the data that was received from request_last_update()")
    print(response)

    # take response and put it in last_update_value
    (last_update, last_update_value) = parselast_update(response)

    last_update_bool = False

    url_row = df.loc['url']
    print('Printing url_row: ' + url_row)

    if last_update_value < url_row['last_update']:  # compare dates and we don't have most recent

        df.replace(url_row.loc['last_update'], last_update_value, inplace=True)
        last_update_bool = True

    return last_update, last_update_bool


# Possibly done
def parselast_update(response):
    # grab last_update from response

    print("Attempting to parse last-modified date in parselast_update()\n")

    # Convert response to string, just in case.
    response_str = str(response)

    # Find index position of Last-Modified
    update_index = response_str.find("Last-Modified:")

    # Find index position of date.
    mod_line = response_str[:update_index + 15]

    print('mod_line is:', mod_line)
    lastmod_datetime = mod_line.split('\n')[0]

    # parse date
    # parsed_date = parsedate(lastmod_datetime)
    print('lastmod_datetime is:', lastmod_datetime)

    exact_time = datetime.datetime.strptime(lastmod_datetime, '%b %d %H:%M:%S %Y')
    print("Exact time is: " + str(exact_time))

    if not exact_time:
        print("Couldn't parse date into the proper time format.")

    # make sure datetime format is the same.
    return lastmod_datetime, exact_time


# request the page (request, host).
def requestAndParsePage(request, host):

    print("running requestAndParsePage()")
    data = request_page(request, host)
    print('back in requestAndParsePage')
    # split the header on beginning of html
    data_str = str(data)

    print('here is the raw page', data_str)
    split_data = data_str.split('<!')
    header = split_data[0]

    return header, data


# get web-page from file.
def get_filepage(file_name):
    print('getting page from file.')
    try:
        with open(file_name, 'rb') as file:
            data = file.read()
    except IOError:
        print("Failed to retrieve cached page.")
        data = ''
        pass

    return data


# Send page to client.
def send_page(conn, page):
    print('Sending page to client.')

    # if page is str, we need to convert to byte array.
    if page is str:
        content = page.encode()
        print('Sending page to user.')
        while True:
            conn.send(content)
            if len(content) <= 0:
                break
    else:
        print("Sending page to user.")
        while True:
            conn.send(page)
            if len(page) <= 0:
                break


# this is pretty much the main method.
def run_program(conn, addr):

    # Receive http request
    request = conn.recv(2056)

    print('parsing header')
    # return (fqdn, cookie, host)
    (fqdn, host) = parse_header_server(str(request))

    last_update_bool = False
    cached_page = False

    print("checking if page in dataframe")
    # check if url is already in the dataframe
    if fqdn in df:
        # Determine the last update time (time, last_update_bool)
        (last_update, last_update_bool) = request_last_update(request, host)
        cached_page = True

    # if the page has been updated
    if last_update_bool:
        # Request full page
        print('page has been updated')
        (header, content) = requestAndParsePage(request, host)

        # write page to file.
        file_name = write_page(content)

        # update filename in dataframe
        df.loc[(df['url'] == fqdn), 'page_hash'] = file_name
        new_date, exact_time = parselast_update(content)
        df.loc[(df['url'] == fqdn), 'last_update_value'] = exact_time

        send_page(conn, content)

    # if the page is already cached and doesn't need to be updated.
    elif cached_page:
        print("Page is already in cache. Don't need to update.")
        file_name = df.loc[(df['url'] == fqdn), 'page_hash']
        # df_by_index = df_row['url']
        # file_name = df_by_index['page_hash']

        page = get_filepage(file_name)

        if not page:
            (header, full_content) = requestAndParsePage(request, host)

            # Update the cache
            hash_filename = write_page(full_content)

            # send the page to client.
            send_page(conn, full_content)

            # Update the filename in the cache
            df.loc[(df['url'] == fqdn), 'page_hash'] = hash_filename

    # if the page is not in cache
    else:  # append header to content
        print("page is not in cache")
        # get header and full page content
        header, content = requestAndParsePage(request, host)

        print('The header is:', header)
        print('The Content is:', str(content))
        # send all the data on to the client.
        while True:
            conn.send(content)
            if len(content) <= 0:
                break

        # parse last_update info from header
        last_update, header_datetime = parselast_update(header)

        page_hash = write_page(content)
        # store the page in the dataframe (or whatever we put it in)
        # , columns=['url', 'last_update', "last_update_value", "page_hash", "response_header"])
        df.append([fqdn, last_update, header_datetime, page_hash, header])

        # Send page to client.
        send_page(conn, content)

   #  print("Request: ", first_line, url )

    """
    Sample Response: 
    
HTTP/1.1 200 OK\n
Cache-Control: private, max-age=0\n
content-Type: text/html; charset=utf-8\n
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
X-content-Type-Options: nosniff\n
X-MS-InvokeApp: 1; RequireReadOnly\n
Date: Thu, 16 Nov 2017 17:55:24 GMT\n
content-Length: 141184\n
Set-Cookie: NSC_OFX-jij.psh-tibsfqpjou-IUUQ=ffffffff09bcb60a45525d5f4f58455e445a4a423660;expires=Thu, 16-Nov-2017 18:14:44 GMT;path=/;httponly\n
\n\n
    """


print("\nThe server is ready to receive HTTP GET requests.")

"""THIS IS OLD CODE."""
while True:
    # This is the exclusive socket for client.
    connectionSocket, addr = server.accept()
    run_program(connectionSocket, addr)

    # receives message and clientAddress. All bytes are both guaranteed to arrive and to arrive in order.
    # message = connectionSocket.recv(999999)
    #message_str = str(message)
    #print("Print Message received")
    #print(message_str[1:])
    # decoded = message.decode()

    # Split header into list of lines
    #header_lines = message_str[2:]
    ##print("Printing header lines..\n")
    #print(header_lines)
    # split first line on white space.

    #split_head = header_lines.split()
    #print("Printing split_head\n")
    #print(str(split_head))

    # server takes the String converted to uppercase, converts it to bytes, and sends it back to client.
    # print("Printing Response:")
    # print(response)
    #connectionSocket.sendall(response.encode())

    # Close socket connection. However, the serverSocket connection remains open.
    connectionSocket.close()  # different than UDP
