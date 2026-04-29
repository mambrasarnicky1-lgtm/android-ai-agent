import paramiko
import os

host = '8.215.23.17'
port = 22
username = 'root'
password = 'N!colay_No1r.Ai@Agent#Secure'

def run_remote(cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, timeout=60)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        ssh.close()
        return out if out else err
    except Exception as e:
        return f"SSH Error: {e}"

def upload_file(local_path, remote_path):
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
        sftp.close()
        transport.close()
        print(f"Uploaded: {local_path} -> {remote_path}")
    except Exception as e:
        print(f"Upload Error: {e}")

print("=== DEPLOYING FUTURISTIC DASHBOARD V20.1 ===")

# List of files to sync
files = [
    ('noir-ui/index.html', '/root/noir-agent/noir-ui/index.html'),
    ('noir-ui/css/style.css', '/root/noir-agent/noir-ui/css/style.css'),
    ('noir-ui/js/main.js', '/root/noir-agent/noir-ui/js/main.js'),
    ('noir-ui/web_server.py', '/root/noir-agent/noir-ui/web_server.py'),
]

for local, remote in files:
    full_local = os.path.join(r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent", local)
    upload_file(full_local, remote)

# Restart the dashboard container
print("Restarting noir-dashboard container...")
run_remote("docker restart noir-dashboard")

print("=== DEPLOYMENT COMPLETE ===")
