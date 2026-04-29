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

print("=== CHECKING NOIR-BRAIN LOGS ===")
res = run_remote("docker logs --tail 20 noir-brain")
print(res)
print("=== END LOGS ===")
