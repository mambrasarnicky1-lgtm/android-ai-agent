import paramiko
import sys

def run_vps_build():
    host = '103.127.133.109'
    port = 22
    username = 'root'
    password = 'N!colay_No1r.Ai@Agent#Secure'

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)

        # Update buildozer.spec on VPS
        spec_content = """[app]
title = Noir SMC
package.name = noir_smc
package.domain = org.noir.agent
source.dir = mobile_app
source.include_exts = py,png,jpg,kv,atlas
version = 14.0.50
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,idna,chardet,pillow,pyjnius
orientation = portrait
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, WAKE_LOCK, SYSTEM_ALERT_WINDOW
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.private_storage = True
services = NoirService:service.py
android.skip_update = False
android.accept_sdk_license = True
android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
"""
        sftp = ssh.open_sftp()
        with sftp.file('/root/noir-agent/buildozer.spec', 'w') as f:
            f.write(spec_content)
        sftp.close()

        # Run build
        build_cmd = "cd /root/noir-agent && rm -rf .buildozer && yes | buildozer android release"
        print(f"Running command: {build_cmd}")
        
        # We use a long timeout or stream output
        stdin, stdout, stderr = ssh.exec_command(build_cmd, get_pty=True)
        
        for line in iter(stdout.readline, ""):
            print(line, end="")
            
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Build successful!")
        else:
            print(f"Build failed with status {exit_status}")
            print(stderr.read().decode())

        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_vps_build()
