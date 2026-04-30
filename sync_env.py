import paramiko
import os

host = '8.215.23.17'
user = 'root'
pwd  = 'N!colay_No1r.Ai@Agent#Secure'
local_env = '.env'
remote_env = '/root/noir-agent/.env'

def upload_env():
    try:
        print(f"[*] Connecting to {host}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=pwd)
        
        print(f"[*] Uploading {local_env} to {remote_env}...")
        sftp = ssh.open_sftp()
        sftp.put(local_env, remote_env)
        sftp.close()
        
        print("[*] Restarting dashboard container to apply changes...")
        ssh.exec_command("docker restart noir-dashboard")
        
        print("[+] Success! GROQ_API_KEY updated and services restarted.")
        ssh.close()
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    upload_env()
