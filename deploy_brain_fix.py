import subprocess
import paramiko

host = '8.215.23.17'
port = 22
username = 'root'
password = 'N!colay_No1r.Ai@Agent#Secure'

def run_local(cmd):
    print(f"Local: {cmd}")
    subprocess.run(cmd, shell=True)

def run_remote(cmd):
    print(f"Remote: {cmd}")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, timeout=60)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        ssh.close()
        res = out if out else err
        print(res)
        return res
    except Exception as e:
        print(f"SSH Error: {e}")
        return str(e)

print("=== DEPLOYING FINAL V20 SINGULARITY FIX ===")

# 1. Local Git Operations
run_local("git rm -f noir-vps/perpetual_evolution.py")
run_local("git add docker-compose.yml")
run_local('git commit -m "fix: Purge obsolete perpetual_evolution module, isolate pure Brain core"')
run_local("git push origin main")

# 2. VPS Operations
run_remote("cd /root/noir-agent && git fetch --all")
run_remote("cd /root/noir-agent && git reset --hard origin/main")

# 3. Restart the Brain Container manually (because docker-compose is broken on VPS)
brain_cmd = (
    "docker rm -f noir-brain && "
    "docker run -d --name noir-brain "
    "--network noir-agent_noir-net "
    "-v /root/noir-agent/.env:/app/.env "
    "-v /root/noir-agent/noir-vps:/app/noir-vps "
    "-v /root/noir-agent/knowledge:/app/knowledge "
    "-v /root/noir-agent/logs:/app/logs "
    "-e PYTHONPATH=/app/noir-vps:/app "
    "--restart always "
    "noir-agent-base:latest "
    "python noir-vps/brain.py"
)
run_remote(brain_cmd)

print("\n=== FINAL DEPLOYMENT COMPLETE ===")
