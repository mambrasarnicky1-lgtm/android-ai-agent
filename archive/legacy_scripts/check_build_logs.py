import paramiko, os
from dotenv import load_dotenv
load_dotenv()

VPS_IP = os.environ.get("NOIR_VPS_IP")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS")

def main():
    if not VPS_IP or not VPS_PASS:
        print("[ERROR] Credentials missing")
        return
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
    
    # Check for specific error logs in buildozer
    # The error usually happens in python3 build or requirements
    cmd = "find /root/noir-agent/mobile_app/.buildozer -name 'config.log' -exec tail -n 50 {} +"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    main()
