import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import subprocess
import os

def ask_for_credentials():
    root = tk.Tk()
    root.withdraw()

    hostname = simpledialog.askstring("Raspberry Pi Host", "Enter Raspberry Pi hostname or IP:")
    if not hostname:
        return None

    username = simpledialog.askstring("Username", "Enter username (default: pi):") or "pi"
    password = simpledialog.askstring("Password", f"Enter password for {username}@{hostname}:", show="*")

    return hostname, username, password

def test_ssh_connection(hostname, username, password):
    print("Testing SSH connection...")
    try:
        test_cmd = [
            "sshpass", "-p", password,
            "ssh", "-o", "StrictHostKeyChecking=no",
            f"{username}@{hostname}", "echo connected"
        ]
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        return "connected" in result.stdout
    except FileNotFoundError:
        messagebox.showerror("Missing sshpass", "The tool 'sshpass' is not installed. Please install it with:\n\nbrew install hudochenkov/sshpass/sshpass")
        return False
    except Exception as e:
        print(f"SSH connection failed: {e}")
        return False

def transfer_file(hostname, username, password, local_path, remote_path="/home/admin/"):
    file_name = os.path.basename(local_path)
    destination = f"{username}@{hostname}:{remote_path}/{file_name}"

    print(f"Transferring '{file_name}' to {hostname}...")
    scp_cmd = [
        "sshpass", "-p", password,
        "scp", local_path, destination
    ]
    result = subprocess.run(scp_cmd)
    return result.returncode == 0, f"{remote_path}/{file_name}"

def main():
    creds = ask_for_credentials()
    if not creds:
        messagebox.showinfo("Cancelled", "No host information entered.")
        return

    hostname, username, password = creds

    if not password:
        messagebox.showwarning("Missing Password", "Password is required.")
        return

    if not test_ssh_connection(hostname, username, password):
        return

    # File Picker
    file_path = filedialog.askopenfilename(title="Select a file to send to the Pi")
    if not file_path:
        messagebox.showinfo("Cancelled", "No file selected.")
        return

    success, remote_file_path = transfer_file(hostname, username, password, file_path)
    if success:
        messagebox.showinfo("Success", f"File transferred successfully to:\n{remote_file_path}")
    else:
        messagebox.showerror("Transfer Failed", "Something went wrong during file transfer.")

if __name__ == "__main__":
    main()
