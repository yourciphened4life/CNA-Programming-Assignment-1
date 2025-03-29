# CNA-Programming-Assignment-1
Programming Assignment 1: HTTP Web Proxy Server Programming Assignment (Python based ) (2025)

# STEP - 1 (Main Branch) 

- Created a TCP socket using AF_INET and SOCK_STREAM
- Bound it to the hostname/port from command-line args
- Began listening for incoming connections
- Accepted a single connection and immediately closed it

# STEP - 2 (Obtaining_remote_homepage Branch)

fixed: Remove extra leading slash in URI parsing and implement basic request forwarding

- Created a server socket using socket.socket(socket.AF_INET, socket.SOCK_STREAM).
- Bound the server socket to the provided hostname and port from command-line arguments.
- Set the server to listen with a backlog of 50 connections.
- Accepted incoming client connections.
- Read the HTTP request from the client and decoded it.
- Parsed the HTTP request line to extract the method, URI, and version.
- Fixed the URI parsing by first removing any leading slash with lstrip('/') and then stripping the "http://" or "https://" protocol prefix.
- Extracted the hostname and resource from the modified URI.
- Connected to the origin server (default port 80) by resolving the hostname.
- Constructed and forwarded a minimal HTTP request (including Host and Connection: close headers) to the origin server.
- Received the response from the origin server and forwarded it back to the client.
- Implemented basic error handling and ensured proper cleanup by closing the client socket after processing.
