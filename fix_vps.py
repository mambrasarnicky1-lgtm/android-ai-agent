import paramiko
import sys

def run_ssh(cmd, desc=""):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('8.215.23.17', 22, 'root', 'N!colay_No1r.Ai@Agent#Secure', timeout=30)
    print(f"[EXEC] {desc}: {cmd[:80]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out: print(out[-500:])
    if err and 'warning' not in err.lower(): print(f"ERR: {err[-300:]}")
    print(f"Exit: {exit_code}\n")
    ssh.close()
    return out

# Step 1: Purge buildozer cache
run_ssh('rm -rf /root/noir-agent/.buildozer /root/noir-agent/bin', 'Purge buildozer')

# Step 2: Prune all Docker
run_ssh('docker system prune -af --volumes 2>&1 | tail -5', 'Prune Docker')

# Step 3: Check disk
run_ssh('df -h /', 'Check disk')

# Step 4: Pull latest code
run_ssh('cd /root/noir-agent && git fetch origin && git reset --hard origin/main 2>&1', 'Pull code')

# Step 5: Start ONLY dashboard container
run_ssh('cd /root/noir-agent && docker compose up -d --build noir-dashboard 2>&1 | tail -10', 'Start Dashboard')

# Step 6: Verify
run_ssh('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"', 'Verify')
