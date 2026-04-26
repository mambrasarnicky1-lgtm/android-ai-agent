import paramiko
import sys

host = '8.215.23.17'
port = 22
username = 'root'
password = 'N!colay_No1r.Ai@Agent#Secure'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(host, port, username, password, timeout=20, banner_timeout=45)
    print("--- DOCKER STATUS ---")
    stdin, stdout, stderr = ssh.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
    print(stdout.read().decode())
    
    print("--- APK BUILD STATUS ---")
    stdin, stdout, stderr = ssh.exec_command('ls -lh /root/noir-agent/bin/ || echo "Bin directory not found"')
    print(stdout.read().decode())
    
    print("--- RECENT BUILD LOG ---")
    stdin, stdout, stderr = ssh.exec_command('tail -n 10 /root/noir-agent/buildozer.log')
    print(stdout.read().decode())
    
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
