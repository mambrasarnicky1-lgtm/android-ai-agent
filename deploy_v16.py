import paramiko
import os

def deploy():
    host = "8.215.23.17"
    port = 22
    username = "root"
    password = "N!colay_No1r.Ai@Agent#Secure"
    
    files_to_upload = [
        ('noir-ui/index.html', '/root/noir-agent/noir-ui/index.html'),
        ('noir-ui/web_server.py', '/root/noir-agent/noir-ui/web_server.py'),
        ('.env', '/root/noir-agent/.env')
    ]
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        
        sftp = ssh.open_sftp()
        for local_path, remote_path in files_to_upload:
            if os.path.exists(local_path):
                print(f"Uploading {local_path} to {remote_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"Warning: {local_path} not found locally.")
        sftp.close()
        
        print("Synchronizing VPS Environment and restarting server...")
        ssh.exec_command('fuser -k 80/tcp || true')
        ssh.exec_command('pkill -f web_server.py || true')
        
        # Start the new v16 server
        ssh.exec_command('cd /root/noir-agent/noir-ui && nohup python3 web_server.py > server.log 2>&1 &')
        
        print("v16.0.00 ELITE VPS Deployment successful!")
        ssh.close()
    except Exception as e:
        print(f"Error during deployment: {e}")

if __name__ == "__main__":
    deploy()
