import paramiko

def fix_and_rebuild():
    host = '8.215.23.17'
    port = 22
    username = 'root'
    password = 'N!colay_No1r.Ai@Agent#Secure'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port, username, password, timeout=30)
        print("[1/2] Installing 'cmake' on VPS...")
        stdin, stdout, stderr = ssh.exec_command('apt-get update && apt-get install -y cmake')
        # Wait for installation to finish
        exit_status = stdout.channel.recv_exit_status()
        print(f"Install status: {exit_status}")
        
        print("[2/2] Restarting Buildozer Compilation...")
        build_script = "cd /root/noir-agent && nohup sh -c 'yes | buildozer android release' > buildozer_final.log 2>&1 &"
        ssh.exec_command(build_script)
        
        print("SUCCESS! Automatic repair applied and build restarted.")
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_and_rebuild()
