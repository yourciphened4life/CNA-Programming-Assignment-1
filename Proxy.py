#!/usr/bin/env python3
import socket
import sys
import os
import argparse
import re

# 1MB buffer size
BUFFER_SIZE = 1000000

def main():
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
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Created socket')
    except Exception as e:
        print('Failed to create socket:', e)
        sys.exit()

    try:
        # Bind the server socket to a host and port
        serverSocket.bind((proxyHost, proxyPort))
        print('Port is bound')
    except Exception as e:
        print('Port is already in use:', e)
        sys.exit()

    try:
        # Listen on the server socket with a backlog of 50
        serverSocket.listen(50)
        print('Listening to socket')
    except Exception as e:
        print('Failed to listen:', e)
        sys.exit()

    # ---------------
    # STEP 2 & 4: ACCEPT CLIENT, FORWARD REQUEST, & CACHE RESPONSE
    # ---------------
    while True:
        print('Waiting for connection...')
        clientSocket = None

        try:
            # Accept connection from client
            clientSocket, clientAddress = serverSocket.accept()
            print(f'Received a connection from: {clientAddress}')
        except Exception as e:
            print('Failed to accept connection:', e)
            sys.exit()

        try:
            message_bytes = clientSocket.recv(BUFFER_SIZE)
            if not message_bytes:
                print("No data received, closing connection.")
                clientSocket.close()
                continue

            message = message_bytes.decode('utf-8', errors='replace')
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
            # Remove any leading slash, then remove the "http://" or "https://" prefix
            URI = URI.lstrip('/')
            URI = re.sub('^http(s?)://', '', URI, count=1)

            # Split hostname from resource name
            resourceParts = URI.split('/', 1)
            hostname = resourceParts[0]
            resource = '/'
            if len(resourceParts) == 2:
                resource = '/' + resourceParts[1]

            print('Requested Resource:\t' + resource)

            # Determine cache location based on hostname and resource
            cacheLocation = './' + hostname + resource
            if cacheLocation.endswith('/'):
                cacheLocation += 'default'
            print('Cache location: ' + cacheLocation)

            # Check if resource is in cache
            if os.path.isfile(cacheLocation):
                try:
                    with open(cacheLocation, 'rb') as cacheFile:
                        cacheData = cacheFile.read()
                    print('Cache hit! Loading from cache file: ' + cacheLocation)
                    clientSocket.sendall(cacheData)
                    print('Sent cached response to client')
                    clientSocket.close()
                    continue
                except Exception as e:
                    print('Error reading cache file:', e)

            # Resource not in cache, proceed to contact the origin server
            try:
                originServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                address = socket.gethostbyname(hostname)
                originPort = 80  # Default to port 80
                print('Connecting to:\t\t' + hostname)
                originServerSocket.connect((address, originPort))
                print('Connected to origin server')

                # Construct a minimal HTTP request with the Host header
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

                # Read the response from the origin server
                response_data = b''
                while True:
                    chunk = originServerSocket.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    response_data += chunk

                try:
                    response_str = response_data.decode('utf-8', errors='replace')
                    status_line = response_str.split("\r\n")[0]
                    if "404" in status_line:
                        print("Received 404 Not Found from origin server. Forwarding error response without caching.")
                except Exception as e:
                    print("Error decoding response for status check:", e)

                # Check if caching is allowed by examining the Cache-Control header
                cacheable = True
                try:
                    header_data = response_data.split(b"\r\n\r\n", 1)[0]
                    header_text = header_data.decode('utf-8', errors='replace').lower()
                    if "cache-control:" in header_text:
                        if "no-store" in header_text or "private" in header_text:
                            cacheable = False
                except Exception as e:
                    print("Error processing headers for caching:", e)

                # If allowed, store the response in the cache
                if cacheable:
                    cacheDir, _ = os.path.split(cacheLocation)
                    print('Caching response in directory: ' + cacheDir)
                    if not os.path.exists(cacheDir):
                        os.makedirs(cacheDir)
                    try:
                        with open(cacheLocation, 'wb') as cacheFile:
                            cacheFile.write(response_data)
                        print('Response cached in ' + cacheLocation)
                    except Exception as e:
                        print('Failed to write cache file:', e)
                else:
                    print('Response not cacheable, not storing in cache.')

                # Send the response back to the client
                clientSocket.sendall(response_data)
                print('Sent response to client')
                originServerSocket.close()

            except OSError as err:
                print('Origin server request failed. ' + str(err))

        except Exception as e:
            print('Error while processing request:', e)
        finally:
            try:
                clientSocket.close()
                print('Closed client socket\n')
            except Exception as e:
                print('Failed to close client socket:', e)

if __name__ == '__main__':
    main()
