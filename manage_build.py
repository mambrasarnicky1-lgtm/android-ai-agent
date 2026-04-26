import paramiko
import time
import sys

def manage_build():
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

        # 1. Check processes
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep buildozer | grep -v grep')
        procs = stdout.read().decode().strip()
        if procs:
            print(f"ALIVE: Buildozer processes found:\n{procs}")
        else:
            print("DEAD: No buildozer processes running.")

        # 2. Check log size and content
        stdin, stdout, stderr = ssh.exec_command('ls -lh /root/noir-agent/buildozer_final.log')
        print(f"Log Info: {stdout.read().decode().strip()}")
        
        stdin, stdout, stderr = ssh.exec_command('tail -n 20 /root/noir-agent/buildozer_final.log')
        print(f"Log Tail:\n{stdout.read().decode()}")

        # 3. Trigger if dead
        if not procs:
            print("Triggering NEW build...")
            # Use sh -c to ensure background execution works with nohup
            cmd = "cd /root/noir-agent && nohup sh -c 'yes | buildozer android release' > buildozer_final.log 2>&1 &"
            ssh.exec_command(cmd)
            time.sleep(2)
            print("Checking if build started...")
            stdin, stdout, stderr = ssh.exec_command('ps aux | grep buildozer | grep -v grep')
            print(stdout.read().decode())
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    manage_build()
