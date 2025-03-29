# Include the libraries for socket and system calls
import socket
import sys
import os
import argparse
import re

# 1MB buffer size
BUFFER_SIZE = 1000000

# Get the IP address and Port number to use for this web proxy server
parser = argparse.ArgumentParser()
parser.add_argument('hostname', help='the IP Address Of Proxy Server')
parser.add_argument('port', help='the port number of the proxy server')
args = parser.parse_args()
proxyHost = args.hostname
proxyPort = int(args.port)

# ---------------
# STEP 1: CREATE / BIND / LISTEN
# ---------------
try:
  # Create a server socket
  # ~~~~ INSERT CODE ~~~~
  serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # ~~~~ END CODE INSERT ~~~~
  print('Created socket')
except:
  print('Failed to create socket')
  sys.exit()

try:
  # Bind the server socket to a host and port
  # ~~~~ INSERT CODE ~~~~
  serverSocket.bind((proxyHost, proxyPort))
  # ~~~~ END CODE INSERT ~~~~
  print('Port is bound')
except:
  print('Port is already in use')
  sys.exit()

try:
  # Listen on the server socket
  # ~~~~ INSERT CODE ~~~~
  serverSocket.listen(50)  # backlog of 50, adjust as needed
  # ~~~~ END CODE INSERT ~~~~
  print('Listening to socket')
except:
  print('Failed to listen')
  sys.exit()

# ---------------
# STEP 2: ACCEPT CLIENT & FORWARD REQUEST
# ---------------
while True:
  print('Waiting for connection...')
  clientSocket = None

  try:
    # Accept connection from client
    # ~~~~ INSERT CODE ~~~~
    clientSocket, clientAddress = serverSocket.accept()
    # ~~~~ END CODE INSERT ~~~~
    print(f'Received a connection from: {clientAddress}')
  except:
    print('Failed to accept connection')
    sys.exit()

  # ---------------
  # READ CLIENT REQUEST
  # ---------------
  try:
    # ~~~~ INSERT CODE ~~~~
    message_bytes = clientSocket.recv(BUFFER_SIZE)
    if not message_bytes:
      print("No data received, closing connection.")
      clientSocket.close()
      continue

    message = message_bytes.decode('utf-8', errors='replace')
    # ~~~~ END CODE INSERT ~~~~

    print('Received request:')
    print('< ' + message)

    # Parse the first line of the HTTP request (method, URI, version)
    request_line = message.split('\r\n')[0]
    requestParts = request_line.split()
    method = requestParts[0]
    URI = requestParts[1]
    version = requestParts[2]

    print('Method:\t\t' + method)
    print('URI:\t\t' + URI)
    print('Version:\t' + version)
    print('')

    # ---------------
    # EXTRACT HOSTNAME AND RESOURCE
    # ---------------
    # Remove leading http:// or https://
    URI = re.sub('^http(s?)://', '', URI, count=1)

    # Split hostname from resource name
    resourceParts = URI.split('/', 1)
    hostname = resourceParts[0]
    resource = '/'
    if len(resourceParts) == 2:
      resource = '/' + resourceParts[1]

    print('Requested Resource:\t' + resource)

    # ---------------
    # CONNECT TO ORIGIN SERVER
    # ---------------
    try:
      originServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      address = socket.gethostbyname(hostname)
      # By default, assume port 80 unless the URL indicates otherwise
      originPort = 80

      print('Connecting to:\t\t' + hostname)
      originServerSocket.connect((address, originPort))
      print('Connected to origin server')

      # ---------------
      # FORWARD CLIENT REQUEST TO ORIGIN SERVER
      # ---------------
      # Minimal HTTP request with Host header
      originServerRequest = f"{method} {resource} {version}\r\n"
      originServerRequest += f"Host: {hostname}\r\n"
      originServerRequest += "Connection: close\r\n"
      originServerRequest += "\r\n"

      print('Forwarding request to origin server:')
      for line in originServerRequest.split('\r\n'):
        if line:
          print('> ' + line)

      originServerSocket.sendall(originServerRequest.encode())
      print('Request sent to origin server\n')

      # ---------------
      # READ RESPONSE FROM ORIGIN SERVER
      # ---------------
      response_data = b''
      while True:
        chunk = originServerSocket.recv(BUFFER_SIZE)
        if not chunk:
          break
        response_data += chunk

      # ---------------
      # SEND RESPONSE BACK TO CLIENT
      # ---------------
      clientSocket.sendall(response_data)
      print('Sent response to client')

      # Close origin server socket
      originServerSocket.close()

    except OSError as err:
      print('Origin server request failed. ' + str(err))

  except Exception as e:
    print('Error while processing request:', e)

  finally:
    # Close the client socket for this request
    try:
      clientSocket.close()
      print('Closed client socket\n')
    except:
      print('Failed to close client socket')
