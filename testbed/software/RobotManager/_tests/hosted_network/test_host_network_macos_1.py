import subprocess


def run_commands_with_sudo_password(sudo_password, commands):
    """
    Runs a list of commands using the provided sudo password.
    """
    try:
        for command in commands:
            full_command = f"echo {sudo_password} | sudo -S {command}"
            subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")


def create_mac_hotspot(interface, ssid, wifi_password, ip_range="192.168.1.1", subnet="255.255.255.0"):
    """
    Creates a Wi-Fi hotspot on macOS using the specified interface (e.g., USB Wi-Fi stick).
    """
    try:
        # Use AppleScript to create a popup asking for an administrator password
        applescript = (
            'tell app "System Events" to display dialog "Enter your macOS password to continue:" '
            'default answer "" with hidden answer buttons {"OK"} default button "OK"'
        )

        # Execute the AppleScript to get the user's password
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True, text=True, check=True
        )

        # Extract the password from the AppleScript response
        sudo_password = result.stdout.split("text returned:")[1].strip()

        # Commands to create hotspot
        commands = [
            f"networksetup -setairportnetwork {interface} {ssid} {wifi_password}",
            "defaults write /Library/Preferences/SystemConfiguration/com.apple.nat.plist Nat -bool true",
            "launchctl load -w /System/Library/LaunchDaemons/com.apple.InternetSharing.plist",
            f"ifconfig {interface} inet {ip_range} netmask {subnet} up"
        ]

        # Run the commands with the obtained password
        run_commands_with_sudo_password(sudo_password, commands)

        print(f"Wi-Fi Hotspot '{ssid}' created successfully with IP range {ip_range}/{subnet}")

    except subprocess.CalledProcessError as e:
        print(f"Error creating hotspot: {e}")


# Example usage:
create_mac_hotspot("en0", "MyMacHotspot", "MySecurePassword123")
