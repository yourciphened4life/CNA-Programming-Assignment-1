# CNA-Programming-Assignment-1
Programming Assignment 1: HTTP Web Proxy Server Programming Assignment (Python based ) (2025)

# STEP - 1 (Main Branch) 

- Created a TCP socket using AF_INET and SOCK_STREAM
- Bound it to the hostname/port from command-line args
- Began listening for incoming connections
- Accepted a single connection and immediately closed it

# STEP - 2 & 3 (Obtaining_remote_homepage Branch)

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

# STEP - 4 (Handle page that does not exist)

- After reading the response from the origin server, decode the header to extract the status line.
- Check if the status line contains "404" to detect a "Not Found" error.
- Log a message indicating that a 404 Not Found was received, and forward the error response to the client without caching.

fixed: 
• Calling server_socket.listen(50) instead of serverSocket.listen(50) in the listening step.
• A typo in printing the requested resource (resourse instead of resource).
• Using the undefined variable host when constructing the HTTP request instead of hostname.

# STEP - 5 (Cache requested webpages where caching is not prohibited by the RFC)

- Determined cache location based on the hostname and requested resource.
- Added a check to see if the resource is already cached; if so, serve it directly.
- If not cached, forward the client request to the origin server.
- After receiving the response, examined the Cache-Control header for "no-store" or "private" directives.
- If caching is permitted, created necessary directories and stored the full response in the cache.
- Logged actions for cache hit, caching, and if caching was skipped due to prohibited directives.

# STEP - 6 (Read from a cached file & Redownload the file from the origin server after file was removed from the proxy server)

- The proxy checks if a requested resource exists in the cache. If a cache hit occurs, the server reads the file from disk and sends the cached response directly back to the client without contacting the origin server.
- If the cache file is missing, the proxy does not detect a cache hit. In this case, it contacts the origin server, downloads the requested file, caches the new response, and then sends it back to the client.
- This code is implemented by the following commit message from an earlier update:
 "Added a check to see if the resource is already cached.if so, serve it directly"
