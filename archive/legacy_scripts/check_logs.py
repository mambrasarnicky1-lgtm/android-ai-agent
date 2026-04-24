import paramiko, os, sys
from dotenv import load_dotenv

load_dotenv(r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\.env")
sys.stdout.reconfigure(encoding='utf-8')

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect(os.environ['NOIR_VPS_IP'], username='root', password=os.environ['NOIR_VPS_PASS'])

_, stdout, _ = s.exec_command('docker logs noir-brain --tail 25')
print("=== BRAIN LOGS ===")
print(stdout.read().decode('utf-8', errors='replace'))

_, stdout, _ = s.exec_command('docker logs noir-telegram --tail 15')
print("=== TELEGRAM LOGS ===")
print(stdout.read().decode('utf-8', errors='replace'))

s.close()
