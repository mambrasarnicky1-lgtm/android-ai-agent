import paramiko, os
from dotenv import load_dotenv
load_dotenv()

VPS_IP = os.environ.get("NOIR_VPS_IP")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS")

if not VPS_IP or not VPS_PASS:
    print("[ERROR] NOIR_VPS_IP or NOIR_VPS_PASS not found.")
    exit(1)

print("[1] Connecting to VPS...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)

print("[2] Executing Git deployment...")
commands = [
    "fuser -k 80/tcp || true",
    "cd /root/noir-agent && docker-compose down || true",
    "cd /root/noir-agent && git fetch --all && git reset --hard origin/main",
    "cd /root/noir-agent && docker-compose up -d --build"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"ERR: {err}")

ssh.close()
print("[SUCCESS] Fully Autonomous Deployment Completed!")
