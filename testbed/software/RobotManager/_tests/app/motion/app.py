import http.server
import ssl
import socketserver

# HTTPS server configuration
HTTP_PORT = 8443  # HTTPS port
CERT_FILE = 'cert.pem'  # Path to your SSL certificate
KEY_FILE = 'key.pem'  # Path to your SSL key
Handler = http.server.SimpleHTTPRequestHandler

if __name__ == '__main__':
    # Generate a self-signed cert (once) with:
    # openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem -subj "/CN=localhost"

    httpd = socketserver.TCPServer(('0.0.0.0', HTTP_PORT), Handler)

    # Create an SSL context for TLS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    # Wrap the server socket
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving HTTPS on 0.0.0.0 port {HTTP_PORT} (https://<your-ip>:{HTTP_PORT}/) ...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server.")
        httpd.server_close()