import paramiko

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

print("=== NOIR SOVEREIGN FULL SYSTEM DIAGNOSTICS ===")

cmds = [
    ("1. CONTAINER STATUS", "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep noir"),
    ("2. DASHBOARD LOGS (Last 10)", "docker logs --tail 10 noir-dashboard"),
    ("3. BRAIN LOGS (Last 15)", "docker logs --tail 15 noir-brain"),
    ("4. HEALER LOGS (Last 10)", "docker logs --tail 10 noir-healer"),
    ("5. RESEARCHER LOGS (Last 10)", "docker logs --tail 10 noir-researcher"),
    ("6. TELEGRAM LOGS (Last 10)", "docker logs --tail 10 noir-telegram"),
    ("7. CPU/MEMORY USAGE", "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | grep noir")
]

for title, cmd in cmds:
    print(f"\n--- {title} ---")
    res = run_remote(cmd)
    if res:
        print(res)
    else:
        print("No output/data.")

print("\n=== DIAGNOSTICS COMPLETE ===")
