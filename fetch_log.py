import paramiko
import sys

def fetch_logs():
    host = '8.215.23.17'
    port = 22
    username = 'root'
    password = 'N!colay_No1r.Ai@Agent#Secure'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port, username, password, timeout=30)
        # Ambil 200 baris terakhir sebelum error Buildozer
        stdin, stdout, stderr = ssh.exec_command('tail -n 250 /root/noir-agent/buildozer_final.log')
        
        logs = stdout.read().decode('utf-8', errors='ignore')
        print(logs)
        ssh.close()
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == "__main__":
    fetch_logs()
