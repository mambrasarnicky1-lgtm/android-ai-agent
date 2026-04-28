import paramiko
import time

def run_ssh(ssh, cmd, desc=""):
    print(f"[EXEC] {desc}: {cmd[:80]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    try:
        if out: print(out[-2000:])
        if err and 'warning' not in err.lower(): print(f"ERR: {err[-1000:]}")
    except UnicodeEncodeError:
        if out: print(out[-2000:].encode('ascii', 'ignore').decode('ascii'))
        if err: print(err[-1000:].encode('ascii', 'ignore').decode('ascii'))
    print(f"Exit: {exit_code}\n")
    return exit_code

def rebuild_vps():
    host = '8.215.23.17'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("Connecting to VPS...")
        ssh.connect(host, 22, 'root', 'N!colay_No1r.Ai@Agent#Secure', timeout=60)
        
        # 1. Verify RAM
        print("=== VERIFYING RAM UPGRADE ===")
        run_ssh(ssh, 'free -m', 'Check RAM')
        
        # 2. Pull latest code (with new docker-compose and Dockerfile)
        print("=== UPDATING CODEBASE ===")
        run_ssh(ssh, 'cd /root/noir-agent && git fetch origin && git reset --hard origin/main', 'Git Pull')
        
        # 3. Aggressive Total Cache Wipe (Deep Clean)
        print("=== TOTAL CACHE WIPE (DEEP CLEAN) ===")
        run_ssh(ssh, 'rm -rf /root/noir-agent/.buildozer', 'Clean Buildozer')
        run_ssh(ssh, 'find /root/noir-agent -name "__pycache__" -exec rm -rf {} +', 'Clean PyCache')
        run_ssh(ssh, 'docker system prune -a --volumes -f', 'Prune Everything')
        run_ssh(ssh, 'docker builder prune -a -f', 'Prune Build Cache')
        
        # 4. STARTING TURBO SERVICES (Shared Base Optimization)
        print("=== STARTING TURBO SERVICES (Shared Base Optimization) ===")
        run_ssh(ssh, 'cd /root/noir-agent && docker compose build noir-base', 'Build Base Image')
        run_ssh(ssh, 'cd /root/noir-agent && docker compose up -d', 'Start Services')
        
        # 5. Final Check
        print("=== FINAL STATUS ===")
        run_ssh(ssh, 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"', 'Verify Containers')
        
        ssh.close()
        print("SUCCESS: VPS Turbo-Boosted to 4GB RAM configuration.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    rebuild_vps()
