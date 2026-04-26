import paramiko
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

host = '8.215.23.17'
port = 22
username = 'root'
password = 'N!colay_No1r.Ai@Agent#Secure'

def run():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port, username, password, timeout=30, banner_timeout=60)
        print('Connected to', host)
        
        # 1. Update VPS code and restart docker
        print('[1/2] Updating VPS Dashboard and restarting Docker...')
        deploy_cmd = 'cd /root/noir-agent && git fetch origin && git reset --hard origin/main && docker compose down && docker compose up --build -d'
        stdin, stdout, stderr = ssh.exec_command(deploy_cmd)
        for line in iter(stdout.readline, ''):
            print(line, end='', flush=True)
            
        # 2. Trigger Buildozer
        print('\n[2/2] Triggering APK Buildozer...')
        build_cmd = "cd /root/noir-agent && nohup sh -c 'yes | buildozer android release' > buildozer_final.log 2>&1 &"
        ssh.exec_command(build_cmd)
        print('APK Build triggered successfully! Monitoring is active at /root/noir-agent/buildozer_final.log')
        
        ssh.close()
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    for _ in range(3):
        try:
            run()
            break
        except Exception as e:
            print("Retry after error:", e)
            time.sleep(2)
