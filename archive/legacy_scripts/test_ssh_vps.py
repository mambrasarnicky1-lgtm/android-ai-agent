import paramiko, sys, os
from dotenv import load_dotenv
load_dotenv()

def test_ssh():
    host = os.environ.get("NOIR_VPS_IP")
    port = 22
    username = os.environ.get("NOIR_VPS_USER", "root")
    password = os.environ.get("NOIR_VPS_PASS")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {host}...")
        ssh.connect(host, port, username, password, timeout=5)
        print("SSH Connection Successful!")
        stdin, stdout, stderr = ssh.exec_command("echo 'SSH is alive'")
        print("Output:", stdout.read().decode().strip())
        ssh.close()
    except Exception as e:
        print(f"SSH Connection Failed: {e}")

if __name__ == "__main__":
    test_ssh()
