import threading

import paramiko


# def executeCommandOverSSH(hostname, username, password, command):
#     """Execute a command on a remote server via SSH."""
#     try:
#         # Initialize SSH client
#         client = paramiko.SSHClient()
#         client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#
#         # Connect to the host
#         print(f"Connecting to {hostname}...")
#         client.connect(hostname, username=username, password=password)
#         print("Connection successful!")
#
#         # Execute the command
#         stdin, stdout, stderr = client.exec_command(command)
#         # print("Command executed. Output:")
#         # print(stdout.read().decode('utf-8'))
#         # print("Errors (if any):")
#         # print(stderr.read().decode('utf-8'))
#
#         # Close the connection
#         client.close()
#     except Exception as e:
#         print(f"An error occurred: {e}")


def executeCommandOverSSH(hostname, username, password, command):
    """Execute a command on a remote server via SSH in a non-blocking way using threads."""

    connection_successful = threading.Event()

    def ssh_worker():
        try:
            # Initialize SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the host
            client.connect(hostname, username=username, password=password)

            # Set the event to indicate that the connection was successful
            connection_successful.set()

            # Execute the command
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            # Optionally handle the output and errors here...

            # Close the connection
            client.close()
        except Exception as e:
            print(f"An error occurred: {e}")
            # The connection was not successful, the event remains unset

    # Create and start a new thread to execute the command
    thread = threading.Thread(target=ssh_worker, daemon=True)
    thread.start()

    # Wait for a short time to see if the connection was successful
    connection_successful.wait(timeout=2)
    if connection_successful.is_set():
        return True
    else:
        return False
