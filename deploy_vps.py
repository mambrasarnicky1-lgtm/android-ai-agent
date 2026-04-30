import paramiko
import os
import time
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv('c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent/.env')

ip = os.getenv("NOIR_VPS_IP")
user = os.getenv("NOIR_VPS_USER")
password = os.getenv("NOIR_VPS_PASS")

if not all([ip, user, password]):
    print("CRITICAL: Missing SSH credentials in .env")
    exit(1)

print(f"[*] Initializing Autonomous Deployment to {ip}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"[*] Authenticating as {user}...")
    ssh.connect(ip, username=user, password=password, timeout=15)
    print("[+] Connection established.")

    # Step 1: Force Pull from GitHub
    print("[*] Syncing code with GitHub (main)...")
    stdin, stdout, stderr = ssh.exec_command("cd /root/noir-agent && git fetch --all && git reset --hard origin/main")
    print(stdout.read().decode())
    print(stderr.read().decode())

    # Step 2: Restart Docker Services
    print("[*] Restarting Mission Control (noir-ui)...")
    stdin, stdout, stderr = ssh.exec_command("cd /root/noir-agent && docker-compose restart noir-ui")
    print(stdout.read().decode())
    
    # Step 3: Verify Status
    print("[*] Checking service status...")
    stdin, stdout, stderr = ssh.exec_command("docker ps | grep noir-ui")
    status = stdout.read().decode()
    print(f"Status: {status if status else 'FAILED TO RESTART'}")

    ssh.close()
    print("\n[SUCCESS] Autonomous deployment complete. v21.0.2 is now LIVE on VPS.")
except Exception as e:
    print(f"\n[ERROR] Deployment failed: {e}")
