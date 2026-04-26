import paramiko
import time

def total_rebuild():
    host = '8.215.23.17'
    port = 22
    username = 'root'
    password = 'N!colay_No1r.Ai@Agent#Secure'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        ssh.connect(host, port, username, password, timeout=30, banner_timeout=60)
        
        # 1. Total Purge
        print("[1/4] Purging caches (Buildozer, Docker, Logs)...")
        ssh.exec_command('rm -rf /root/noir-agent/.buildozer')
        ssh.exec_command('rm -rf /root/noir-agent/bin/*')
        ssh.exec_command('docker system prune -af')
        
        # 2. Update Code
        print("[2/4] Syncing latest code (v17.5.0)...")
        stdin, stdout, stderr = ssh.exec_command('cd /root/noir-agent && git fetch origin && git reset --hard origin/main')
        print(stdout.read().decode())
        
        # 3. Restart Services
        print("[3/4] Restarting Docker Services (Clean Build)...")
        ssh.exec_command('cd /root/noir-agent && docker compose down && docker compose up -d --build')
        
        # 4. Start APK Build
        print("[4/4] Starting CLEAN APK Buildozer (v17.5.0)...")
        # We use a dedicated shell script to avoid parsing issues
        build_script = "cd /root/noir-agent && nohup sh -c 'yes | buildozer android release' > buildozer_final.log 2>&1 &"
        ssh.exec_command(build_script)
        
        print("\nSUCCESS: Total Rebuild Initiated.")
        print("Monitor progress: tail -f /root/noir-agent/buildozer_final.log")
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    total_rebuild()
