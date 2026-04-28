import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('8.215.23.17', 22, 'root', 'N!colay_No1r.Ai@Agent#Secure', timeout=30)

print("Starting Dashboard container...")
stdin, stdout, stderr = ssh.exec_command('cd /root/noir-agent && docker compose up -d --build noir-dashboard 2>&1 | tail -15', timeout=180)
exit_code = stdout.channel.recv_exit_status()
print(stdout.read().decode('utf-8', errors='ignore'))
print(stderr.read().decode('utf-8', errors='ignore')[-300:])
print(f"Exit: {exit_code}")

print("\n=== Container Status ===")
stdin, stdout, stderr = ssh.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
print(stdout.read().decode())

ssh.close()
