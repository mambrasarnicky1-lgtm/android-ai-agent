import paramiko
import os

# VPS CONFIG
VPS_IP = "8.215.23.17"
VPS_USER = "root"
VPS_PASS = "N!colay_No1r.Ai@Agent#Secure"
REMOTE_DIR = "/opt/noir-dashboard/"

# LOCAL FILES
LOCAL_SERVER = "noir-ui/web_server.py"
LOCAL_UI = "noir-ui/index.html"

def deploy():
    print(f"Deploying NOIR DIRECT BRIDGE v12.0 to {VPS_IP}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        print("Connected!")

        print("Installing system dependencies...")
        ssh.exec_command("apt update && apt install -y python3-fastapi python3-uvicorn lsof sqlite3")

        print("Cleaning up existing services...")
        ssh.exec_command("fuser -k 80/tcp || true")

        print("Uploading server and UI...")
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_SERVER, REMOTE_DIR + "server.py")
        sftp.put(LOCAL_UI, REMOTE_DIR + "index.html")
        sftp.close()

        print("Launching v12.0 Direct Bridge...")
        ssh.exec_command(f"cd {REMOTE_DIR} && nohup python3 -m uvicorn server:app --host 0.0.0.0 --port 80 > /var/log/noir-bridge.log 2>&1 &")

        import time
        time.sleep(3)
        print("SUCCESS! System is now DIRECT-LINKED.")
        ssh.close()
    except Exception as e:
        print(f"Deployment Failed: {e}")

if __name__ == "__main__":
    deploy()
