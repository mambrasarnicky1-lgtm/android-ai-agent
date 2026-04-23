import paramiko, os
from dotenv import load_dotenv
load_dotenv()

def check_vps():
    host = os.environ.get("NOIR_VPS_IP")
    username = os.environ.get("NOIR_VPS_USER", "root")
    password = os.environ.get("NOIR_VPS_PASS")

    if not host or not password:
        print("[ERROR] Credentials missing in .env")
        return

    print(f"Connecting to {host}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)
        print("Connected! Running diagnostics...")

        commands = [
            "netstat -tulpn | grep -E '80|8888|8000|5000'",
            "ps aux | grep python",
            "cat /root/noir-agent/noir-ui/server.log | tail -n 10"
        ]

        for cmd in commands:
            print(f"\n--- [ {cmd} ] ---")
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
            print("STDOUT:", stdout.read().decode().strip())
            print("STDERR:", stderr.read().decode().strip())

        ssh.close()
        print("\nDiagnostics complete.")
    except Exception as e:
        print(f"Failed to connect or execute: {e}")

if __name__ == "__main__":
    check_vps()
