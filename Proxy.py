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
  serverSocket.listen(50)  # You can set the backlog to an appropriate value
  # ~~~~ END CODE INSERT ~~~~
  print('Listening to socket')
except:
  print('Failed to listen')
  sys.exit()

# Continuously accept connections
while True:
  print('Waiting for connection...')
  clientSocket = None

  try:
    # Accept connection from client and store in clientSocket
    # ~~~~ INSERT CODE ~~~~
    clientSocket, clientAddress = serverSocket.accept()
    # ~~~~ END CODE INSERT ~~~~
    print('Received a connection from:', clientAddress)
  except:
    print('Failed to accept connection')
    sys.exit()

  # At this point, the proxy server is connected to the client
  # (You can proceed with reading the request, etc.)

  # For now, we can simply close the client socket right away
  # to demonstrate that the connection was accepted.
  try:
    clientSocket.close()
    print('Closed the client socket.\n')
  except:
    print('Failed to close client socket')
