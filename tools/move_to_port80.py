import paramiko, sys, os, time
from dotenv import load_dotenv
load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"

VPS_IP = os.environ.get("NOIR_VPS_IP")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
print("Connected")

def run(cmd, timeout=10):
    print(f"> {cmd}")
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode().strip()
        if out: print(f"  {out}")
        return out
    except Exception as e:
        print(f"  [Timeout or Error] {e}")
        return ""

# Kill all existing server processes
run("kill -9 $(pgrep -f 'server.py') 2>/dev/null; sleep 1")

# Update port to 80
run("sed -i 's/PORT = [0-9]*/PORT = 80/' /opt/noir-dashboard/server.py")

# Verify the port setting
run("grep 'PORT = ' /opt/noir-dashboard/server.py")

# Start server on port 80, fully detached
run("cd /opt/noir-dashboard && nohup python3 server.py > /var/log/noir-dashboard.log 2>&1 </dev/null &")
time.sleep(3)

# Verify locally
result = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:80/")
print(f"\nLocal test: HTTP {result}")

if result == "200":
    print(f"\nDashboard is running on port 80!")
    print(f"Try opening: http://{VPS_IP}/")
else:
    print("\nChecking logs...")
    run("tail -10 /var/log/noir-dashboard.log")

ssh.close()
