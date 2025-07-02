import os
import subprocess
import re
import sys
import signal
import time

running = True

def signal_handler(signum, frame):
    global running
    print("Received termination signal. Exiting gracefully...")
    running = False

def get_kasa_status(username, password, host):
    cmd = [
        'kasa',
        '--username', username,
        '--password', password,
        '--host', host,
        'state'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"kasa CLI error: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout

def parse_status(output):
    data = {}

    patterns = {
        'device_state': r'Device state:\s+(True|False)',
        'current_consumption': r'Current consumption \(current_consumption\):\s+([\d\.]+) W',
        'current': r'Current \(current\):\s+([\d\.]+) A',
        'voltage': r'Voltage \(voltage\):\s+([\d\.]+) V',
        'consumption_today': r"Today's consumption \(consumption_today\):\s+([\d\.]+) kWh",
        'consumption_this_month': r"This month's consumption \(consumption_this_month\):\s+([\d\.]+) kWh",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            if key == 'device_state':
                data[key] = 1 if match.group(1) == 'True' else 0
            else:
                data[key] = float(match.group(1))
        else:
            data[key] = None

    return data

def send_to_zabbix(server, hostname, data):
    lines = []
    key_map = {
        'device_state': 'tapo.device_state',
        'current_consumption': 'tapo.current_consumption',
        'current': 'tapo.current',
        'voltage': 'tapo.voltage',
        'consumption_today': 'tapo.consumption_today',
        'consumption_this_month': 'tapo.consumption_this_month',
    }

    for field, key in key_map.items():
        value = data.get(field)
        if value is not None:
            lines.append(f"{hostname} {key} {value}")

    if not lines:
        print("No data to send to Zabbix", file=sys.stderr)
        return

    zabbix_input = "\n".join(lines)
    print("Sending to Zabbix:")
    print(zabbix_input)

    cmd = ['zabbix_sender', '-z', server, '-i', "-" ]
    proc = subprocess.run(cmd, input=zabbix_input, text=True, capture_output=True)
    if proc.returncode != 0:
        print(f"zabbix_sender error: {proc.stderr}", file=sys.stderr)
        return
    print(f"zabbix_sender output: {proc.stdout.strip()}")

def main():
    username = os.getenv('TAPO_USER')
    password = os.getenv('TAPO_PASSWORD')
    plug_ip = os.getenv('PLUG_IP')
    zabbix_server = os.getenv('ZABBIX_SERVER')
    zabbix_hostname = os.getenv('ZABBIX_HOSTNAME')

    required_vars = {
        'TAPO_USER': username,
        'TAPO_PASSWORD': password,
        'PLUG_IP': plug_ip,
        'ZABBIX_SERVER': zabbix_server,
        'ZABBIX_HOSTNAME': zabbix_hostname,
    }
    missing = [k for k,v in required_vars.items() if not v]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        return

    output = get_kasa_status(username, password, plug_ip)
    if not output:
        print("Failed to get kasa status", file=sys.stderr)
        return
    data = parse_status(output)
    send_to_zabbix(zabbix_server, zabbix_hostname, data)

if __name__ == '__main__':
    INTERVAL = int(os.getenv('RUN_INTERVAL', '300'))
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while running:
        try:
            main()
        except Exception as e:
            print(f"Error during main execution: {e}", file=sys.stderr)
        if not running:
            break
        time.sleep(INTERVAL)

