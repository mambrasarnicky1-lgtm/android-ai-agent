import paramiko, time

host = '8.215.23.17'
port = 22
user = 'root'
pwd  = 'N!colay_No1r.Ai@Agent#Secure'

def ssh(cmd):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, port, user, pwd, timeout=30)
    _, o, e = c.exec_command(cmd)
    out = o.read().decode('utf-8','replace').strip()
    c.close()
    return out or e.read().decode('utf-8','replace').strip()

print("=== SYNCING VPS FOR SPA DASHBOARD ===")
print(ssh("cd /root/noir-agent && git fetch origin main && git reset --hard origin/main"))
print("Restarting dashboard...")
print(ssh("docker restart noir-dashboard"))
time.sleep(5)
print(ssh("docker ps --format 'table {{.Names}}\t{{.Status}}'"))
print("=== DONE ===")
