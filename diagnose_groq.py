import paramiko

host = '8.215.23.17'
user = 'root'
pwd  = 'N!colay_No1r.Ai@Agent#Secure'

def ssh(cmd):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, 22, user, pwd, timeout=15)
    _, o, e = c.exec_command(cmd, timeout=10)
    out = o.read().decode('utf-8','replace').strip()
    err = e.read().decode('utf-8','replace').strip()
    c.close()
    return out or err or "(empty)"

print("=== 1. GROQ KEY IN HOST .env ===")
print(ssh("grep GROQ /root/noir-agent/.env"))

print("\n=== 2. GROQ KEY INSIDE CONTAINER ===")
print(ssh("docker exec noir-dashboard grep GROQ /app/.env"))

print("\n=== 3. GROQ ENV VAR AT RUNTIME ===")
print(ssh('docker exec noir-dashboard python3 -c "import os; print(os.environ.get(\'GROQ_API_KEY\',\'NOT_SET\'))"'))

print("\n=== 4. DOTENV LOADING PATH ===")
print(ssh('docker exec noir-dashboard python3 -c "import os; from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(\'/app/noir-ui/web_server.py\'),\'..\',\'.env\')); print(os.environ.get(\'GROQ_API_KEY\',\'NOT_LOADED\'))"'))

print("\n=== 5. DOES _try_groq EXIST IN CODE? ===")
print(ssh("docker exec noir-dashboard grep -n _try_groq /app/noir-ui/web_server.py"))

print("\n=== 6. DOES brain_chat EXIST? ===")
print(ssh("docker exec noir-dashboard grep -n brain_chat /app/noir-ui/web_server.py"))

print("\n=== 7. CONTAINER LOGS (last 20 lines) ===")
print(ssh("docker logs noir-dashboard --tail 20"))
