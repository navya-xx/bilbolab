#!/usr/bin/env python3
import socket
import time

HOST = ''  # Bind to all interfaces
PORT = 50007  # Arbitrary non-privileged port


def run_server():
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on port {PORT}...")

        # Wait for a client connection
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                # Record the start time
                start_time = time.perf_counter()

                # Send a message to the client
                message = b'Ping'
                conn.sendall(message)

                # Wait for the client to respond
                data = conn.recv(1024)
                if not data:
                    print("Client disconnected.")
                    break

                # Record the time after receiving the response
                end_time = time.perf_counter()
                rtt = (end_time - start_time) * 1000  # Convert to milliseconds
                print(f"Received {data!r} | RTT: {rtt:.2f} ms")

                # Pause briefly before sending the next message
                time.sleep(1)


if __name__ == '__main__':
    run_server()
