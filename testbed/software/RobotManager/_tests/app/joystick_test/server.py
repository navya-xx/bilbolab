# serve.py
import http.server, socketserver, ssl



if __name__ == '__main__':
    PORT = 4443
    Handler = http.server.SimpleHTTPRequestHandler

    # Create the HTTP server
    httpd = socketserver.TCPServer(("", PORT), Handler)

    # Create an SSLContext for TLS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # Load your self-signed certificate + key
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    # Wrap the server’s socket
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving HTTPS on 0.0.0.0 port {PORT} …")
    httpd.serve_forever()
