import paramiko

def stop_and_clean():
    host = '8.215.23.17'
    port = 22
    username = 'root'
    password = 'N!colay_No1r.Ai@Agent#Secure'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        ssh.connect(host, port, username, password, timeout=30, banner_timeout=90)
        print("CONNECTED!")

        print("Stopping Buildozer processes...")
        ssh.exec_command('pkill -9 buildozer; pkill -9 python3; pkill -9 java; pkill -9 gradle')
        
        print("Cleaning up caches...")
        ssh.exec_command('rm -rf /root/noir-agent/.buildozer')
        ssh.exec_command('rm -rf /root/noir-agent/bin/*')
        ssh.exec_command('docker system prune -f')
        
        print("Restarting Dashboard (without build load)...")
        ssh.exec_command('cd /root/noir-agent && docker compose up -d noir-dashboard')
        
        print("CLEANUP COMPLETE. VPS Build Stopped.")
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    stop_and_clean()
