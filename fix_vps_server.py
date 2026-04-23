import paramiko, time, os
from dotenv import load_dotenv
load_dotenv()

def setup_vps_server():
    host = os.environ.get("NOIR_VPS_IP")
    port = 22
    username = os.environ.get("NOIR_VPS_USER", "root")
    password = os.environ.get("NOIR_VPS_PASS")
    
    if not host or not password:
        print("[ERROR] Credentials missing")
        return

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("Connecting to VPS...")
        ssh.connect(host, port, username, password, timeout=5)
        
        print("Killing old python processes...")
        ssh.exec_command("pkill -9 python3; pkill -9 uvicorn")
        time.sleep(2) # Wait for processes to die
        
        print("Starting simple HTTP server on port 8888...")
        ssh.exec_command("cd /root/noir-agent/noir-ui && nohup python3 -m http.server 8888 > fallback.log 2>&1 &")
        time.sleep(3) # Wait for server to bind port
        
        print("Verifying port 8888 is listening...")
        stdin, stdout, stderr = ssh.exec_command("netstat -tulpn | grep 8888")
        result = stdout.read().decode().strip()
        if result:
            print(f"Port 8888 is ACTIVE:\n{result}")
        else:
            print("Port 8888 is NOT listening. Server failed to start.")
            
        ssh.close()
    except Exception as e:
        print(f"Operation Failed: {e}")

if __name__ == "__main__":
    setup_vps_server()
