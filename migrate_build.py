import paramiko
import subprocess

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

def run_local(cmd):
    print(f"Local: {cmd}")
    subprocess.run(cmd, shell=True)

print("=== MIGRATING BUILD TO GITHUB ACTIONS ===")

# 1. Kill VPS Buildozer process
print("Killing VPS buildozer processes...")
run_remote("pkill -f buildozer || true")
run_remote("pkill -f run_build.sh || true")

# 2. Push GitHub Actions Workflow
print("Triggering GitHub Action...")
run_local("git add .github/workflows/build.yml")
run_local('git commit -m "build: Migrate to GitHub Actions & Force pristine zero-state build (V20.1)"')
run_local("git push origin main")

print("=== MIGRATION COMPLETE ===")
