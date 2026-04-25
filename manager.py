import os, sys, shutil, json, time, subprocess
from dotenv import load_dotenv
import paramiko
from scp import SCPClient
import requests

load_dotenv()
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class NoirManager:
    def __init__(self):
        self.vps_ip = os.environ.get("NOIR_VPS_IP")
        self.vps_user = os.environ.get("NOIR_VPS_USER", "root")
        self.vps_pass = os.environ.get("NOIR_VPS_PASS")
        self.remote_path = "/root/noir-agent"
        
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _connect(self):
        try:
            self.ssh.connect(self.vps_ip, username=self.vps_user, password=self.vps_pass, timeout=15)
            return True
        except Exception as e:
            print(f"[ERROR] SSH Connection Failed: {e}")
            return False

    def _run_remote(self, cmd):
        print(f"[REMOTE] Executing: {cmd}")
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        if out: print(f"  [OUT] {out}")
        if err: print(f"  [ERR] {err}")
        return out, err

    def deploy_vps(self):
        print("[PROCESS] Syncing to VPS (v17.2.2 OMEGA-FIX)...")
        if not self._connect(): return
        
        try:
            # Sync files via SCP
            with SCPClient(self.ssh.get_transport()) as scp:
                print("[SCP] Uploading project files...")
                for item in os.listdir("."):
                    if item in [".git", "venv", ".buildozer", "node_modules", "__pycache__", "bin", "archive"]: continue
                    if item == "noir-gateway":
                        # Upload gateway but skip node_modules
                        temp_sync = os.path.join(os.getcwd(), "gateway_sync_tmp")
                        shutil.rmtree(temp_sync, ignore_errors=True)
                        shutil.copytree("noir-gateway", temp_sync, ignore=shutil.ignore_patterns("node_modules", ".wrangler"))
                        scp.put(temp_sync, remote_path=os.path.join(self.remote_path, "noir-gateway"), recursive=True)
                        shutil.rmtree(temp_sync, ignore_errors=True)
                        continue
                    scp.put(item, remote_path=self.remote_path, recursive=True)
            
            self._run_remote("fuser -k 80/tcp || true")
            self._run_remote(f"cd {self.remote_path} && docker-compose down || true")
            print("[PROCESS] Starting All Neural Services in Docker (v17.2.2)...")
            self._run_remote(f"cd {self.remote_path} && docker-compose up -d --build")
            
            self.notify_telegram("🖤 *Noir Sovereign v17.2.2 Active*\nSemua layanan neural di VPS telah dideploy dan diaktifkan.")
            print("[SUCCESS] v17.2.2 OMEGA-FIX DEPLOYED.")
        except Exception as e:
            print(f"[ERROR] Deployment failed: {e}")
        finally:
            self.ssh.close()

    def gateway_deploy(self):
        print("[PROCESS] Deploying Cloudflare Gateway...")
        subprocess.run(["npm", "run", "deploy"], cwd="noir-gateway", shell=True)

    def notify_telegram(self, message):
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not token or not chat_id: return
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        except: pass

    def build_apk(self):
        print("[PROCESS] STARTING REMOTE SOVEREIGN BUILD (v17.2.2)...")
        if not self._connect(): return
        
        try:
            with SCPClient(self.ssh.get_transport()) as scp:
                print("[SYNC] Uploading mobile_app source...")
                scp.put("mobile_app", remote_path=self.remote_path, recursive=True)
                scp.put("buildozer.spec", remote_path=f"{self.remote_path}/buildozer.spec")

            print("[BUILD] Executing Buildozer on VPS...")
            self._run_remote(f"cd {self.remote_path} && buildozer -v android debug")
            
            local_bin = "bin"
            os.makedirs(local_bin, exist_ok=True)
            with SCPClient(self.ssh.get_transport()) as scp:
                print("[SYNC] Downloading APK...")
                scp.get(f"{self.remote_path}/bin/*.apk", local_path=local_bin)
            
            print(f"[SUCCESS] APK downloaded to: {local_bin}")
            self.notify_telegram("📦 *Sovereign Build Complete*\nAPK v17.2.2 telah berhasil dibangun di VPS.")
        except Exception as e:
            print(f"[ERROR] Build failed: {e}")
        finally:
            self.ssh.close()

    def total_purge(self):
        print("[PROCESS] INITIATING TOTAL SYSTEM PURGE...")
        shutil.rmtree("noir-gateway/.wrangler", ignore_errors=True)
        shutil.rmtree("mobile_app/.buildozer", ignore_errors=True)
        shutil.rmtree("bin", ignore_errors=True)
        
        if self._connect():
            self._run_remote(f"cd {self.remote_path} && find . -type d -name '__pycache__' -exec rm -rf {{}} +")
            self._run_remote(f"cd {self.remote_path} && rm -rf mobile_app/.buildozer bin")
            self._run_remote("docker system prune -f")
            self.ssh.close()
        print("[SUCCESS] Total Purge Complete.")

if __name__ == "__main__":
    manager = NoirManager()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "deploy": manager.deploy_vps()
        elif cmd == "build-apk": manager.build_apk()
        elif cmd == "total-purge": manager.total_purge()
        elif cmd == "gateway": manager.gateway_deploy()
    else:
        print("Usage: python manager.py [deploy|build-apk|total-purge|gateway]")
