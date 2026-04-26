import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

host = '8.215.23.17'
port = 22
username = 'root'
password = 'N!colay_No1r.Ai@Agent#Secure'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(host, port, username, password, timeout=10)
    print('Connected to Build Server:', host)
    
    # Run build in background via nohup and yes
    build_cmd = "cd /root/noir-agent && nohup sh -c 'yes | buildozer android release' > buildozer.log 2>&1 &"
    print('Triggering APK build in background...')
    stdin, stdout, stderr = ssh.exec_command(build_cmd)
    print('Build triggered. You can monitor it on the VPS at /root/noir-agent/buildozer.log')
    ssh.close()
except Exception as e:
    print('Error:', e)
