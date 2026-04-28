import paramiko

def diagnose_vps():
    host = '8.215.23.17'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, 22, 'root', 'N!colay_No1r.Ai@Agent#Secure', timeout=30)
        
        # 1. Check Docker containers
        print("=== DOCKER CONTAINERS ===")
        stdin, stdout, stderr = ssh.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
        print(stdout.read().decode())
        
        # 2. Check if port 80 is listening
        print("=== PORT 80 STATUS ===")
        stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep -E ":80|:8080|:5000"')
        print(stdout.read().decode() or "No services on port 80/8080/5000\n")
        
        # 3. Check disk and memory
        print("=== DISK & MEMORY ===")
        stdin, stdout, stderr = ssh.exec_command('df -h / && echo "---" && free -m')
        print(stdout.read().decode())
        
        # 4. Check docker-compose file location
        print("=== DOCKER COMPOSE FILES ===")
        stdin, stdout, stderr = ssh.exec_command('find /root -name "docker-compose*" -type f 2>/dev/null')
        print(stdout.read().decode() or "No docker-compose files found\n")
        
        # 5. Try to restart services
        print("=== RESTARTING SERVICES ===")
        stdin, stdout, stderr = ssh.exec_command('cd /root/noir-agent && docker compose up -d --build 2>&1 | tail -20')
        exit_status = stdout.channel.recv_exit_status()
        print(stdout.read().decode())
        print(stderr.read().decode())
        print(f"Exit status: {exit_status}")
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_vps()
