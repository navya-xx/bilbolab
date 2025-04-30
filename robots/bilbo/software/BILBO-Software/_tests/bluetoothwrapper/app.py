from flask import Flask, jsonify, request, render_template
import subprocess

app = Flask(__name__)

def get_paired_devices():
    # Retrieve paired devices via bluetoothctl
    result = subprocess.run(['bluetoothctl', 'paired-devices'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    devices = []
    for line in lines:
        parts = line.split(' ', 2)
        if len(parts) >= 3:
            mac = parts[1]
            name = parts[2]
            # Check connection status
            info = subprocess.run(['bluetoothctl', 'info', mac], capture_output=True, text=True)
            connected = any('Connected: yes' in l for l in info.stdout.splitlines())
            devices.append({'mac': mac, 'name': name, 'connected': connected})
    return devices


def remove_device(mac):
    subprocess.run(['bluetoothctl', 'remove', mac])


def scan_devices():
    # Use hcitool to scan for devices with names
    result = subprocess.run(['hcitool', 'scan'], capture_output=True, text=True)
    # Skip header line
    lines = result.stdout.splitlines()[1:]
    devices = []
    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            mac, name = parts
            devices.append({'mac': mac, 'name': name})
    return devices


def pair_device(mac):
    print(f"Try to pair device with MAC: {mac}...")
    # Execute pairing, trusting, and connecting
    cmds = f'pair {mac}\ntrust {mac}\nconnect {mac}\n'
    p = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(cmds)
    return out + err


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/paired')
def api_paired():
    devices = get_paired_devices()
    return jsonify(devices)


@app.route('/api/remove', methods=['POST'])
def api_remove():
    mac = request.get_json().get('mac')
    remove_device(mac)
    return jsonify({'status': 'success'})


@app.route('/api/scan')
def api_scan():
    devices = scan_devices()
    return jsonify(devices)


@app.route('/api/pair', methods=['POST'])
def api_pair():
    mac = request.get_json().get('mac')
    output = pair_device(mac)
    return jsonify({'status': 'success', 'output': output})


if __name__ == '__main__':
    # Ensure this runs with appropriate privileges
    app.run(host='0.0.0.0', port=8000)