import paramiko
import requests
import json

host = '8.215.23.17'
port = 22
username = 'root'
password = 'N!colay_No1r.Ai@Agent#Secure'

GATEWAY_URL = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"
API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"

def run_remote(cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, timeout=60)
        print(f"Executing on VPS: {cmd}")
        # Use exec_command with pty=True for commands that might buffer output
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # We don't want to wait for buildozer to finish completely synchronously if it takes 15 mins,
        # but for this script we will start it in the background using tmux or nohup
        # Or we can just run it and return the starting status.
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        ssh.close()
        return out if out else err
    except Exception as e:
        return f"SSH Error: {e}"

def set_learning_directive():
    print("=== SENDING AUTONOMOUS LEARNING DIRECTIVE ===")
    try:
        resp = requests.post(
            f"{GATEWAY_URL}/agent/command",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "target_device": "RESEARCHER_CORE",
                "action": {
                    "type": "set_learning_target", 
                    "target": "APK Architecture Hardening & Dashboard Security for HyperOS"
                },
                "description": "User Directive: Prepare and optimize APK and Dashboard structures."
            },
            timeout=10
        )
        print(f"Gateway Response: {resp.status_code}")
        print("Directive Sent: APK Architecture Hardening & Dashboard Security for HyperOS")
    except Exception as e:
        print(f"Failed to send directive: {e}")

def trigger_clean_build():
    print("\n=== TRIGGERING CLEAN APK BUILD ON VPS ===")
    # Create a background script on VPS to run buildozer, as it takes a long time.
    # We will log the output to build.log so the user can check it later.
    build_script = """
cat << 'EOF' > /root/noir-agent/run_build.sh
#!/bin/bash
cd /root/noir-agent
echo "Starting clean APK Build at $(date)" > build.log
# Ensure buildozer is installed and we accept licenses
yes | sdkmanager --licenses >> build.log 2>&1
buildozer android release >> build.log 2>&1
echo "Build Process Completed at $(date)" >> build.log
EOF
chmod +x /root/noir-agent/run_build.sh
nohup /root/noir-agent/run_build.sh > /dev/null 2>&1 &
echo "Background build process started. Logs are being written to /root/noir-agent/build.log"
"""
    res = run_remote(build_script)
    print(res)

if __name__ == "__main__":
    set_learning_directive()
    trigger_clean_build()
    print("\n=== ALL DIRECTIVES EXECUTED ===")
