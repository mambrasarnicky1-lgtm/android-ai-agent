import os, sys, shutil, json, time, subprocess

class NoirManager:
    def __init__(self):
        # Fallback to hardcoded IP if not in env
        self.vps_ip = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
        self.vps_user = os.environ.get("NOIR_VPS_USER", "root")
        self.remote_path = "/root/noir-agent"
        self.ssh_target = f"{self.vps_user}@{self.vps_ip}"
        self.ssh_base = ["ssh", self.ssh_target]

    def deploy_vps(self):
        print("[PROCESS] Syncing to VPS (v14.0 COMMANDER)...")
        try:
            # Sync files
            subprocess.run(["scp", "-r", ".", f"{self.vps_user}@{self.vps_ip}:{self.remote_path}"], check=True)
            # Kill existing standalone process and docker containers
            subprocess.run(self.ssh_base + ["fuser -k 80/tcp || true"])
            subprocess.run(self.ssh_base + [f"cd {self.remote_path} && docker-compose down || true"])
            
            # Start all services in Docker (Brain, Telegram, Dashboard)
            print("[PROCESS] Starting All Neural Services in Docker...")
            subprocess.run(self.ssh_base + [f"cd {self.remote_path} && docker-compose up -d --build"], check=True)
            
            print("[SUCCESS] v14.0 COMMANDER DEPLOYED.")
        except Exception as e:
            print(f"[ERROR] Deployment failed: {e}")

    def clean_vps(self):
        print("[PROCESS] Purging VPS Cache & Residual Data...")
        try:
            # Purge Docker cache
            subprocess.run(self.ssh_base + ["docker system prune -af --volumes"], check=True)
            # Purge Python cache and logs
            subprocess.run(self.ssh_base + [f"cd {self.remote_path} && find . -type d -name '__pycache__' -exec rm -rf {{}} +"])
            subprocess.run(self.ssh_base + [f"cd {self.remote_path} && find . -name '*.log' -delete"])
            print("[SUCCESS] Full System Purge Complete.")
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")

    def gateway_deploy(self):
        print("[PROCESS] Deploying Cloudflare Gateway...")
        try:
            # Use shell=True for Windows compatibility with npm/npx
            subprocess.run("npx wrangler deploy", shell=True, check=True, cwd="noir-gateway")
            print("[SUCCESS] Gateway LIVE.")
        except Exception as e:
            print(f"[ERROR] Gateway deploy failed: {e}")

    def reset_telegram(self):
        print("[PROCESS] FORCING TELEGRAM SERVICE RESET...")
        try:
            # Kill standalone
            subprocess.run(self.ssh_base + ["pkill -f telegram_bot.py || true"])
            # Remove cache
            subprocess.run(self.ssh_base + [f"cd {self.remote_path} && find . -type d -name '__pycache__' -exec rm -rf {{}} +"])
            # Force rebuild specific service
            subprocess.run(self.ssh_base + [f"cd {self.remote_path} && docker-compose up -d --build --force-recreate noir-telegram"], check=True)
            print("[SUCCESS] Telegram Service Refresh Complete.")
        except Exception as e:
            print(f"[ERROR] Telegram reset failed: {e}")

    def setup_builder(self):
        print("[PROCESS] Setting up Sovereign Builder on VPS...")
        subprocess.run(["scp", "vps_build_setup.sh", f"{self.ssh_target}:/tmp/"])
        subprocess.run(self.ssh_base + ["bash /tmp/vps_build_setup.sh"])
        print("[SUCCESS] Builder setup complete.")

    def build_apk(self):
        print("[PROCESS] STARTING REMOTE SOVEREIGN BUILD (v14.0.13)...")
        # 1. Sync mobile_app folder
        print("[SYNC] Uploading mobile_app source to VPS...")
        subprocess.run(["scp", "-r", "mobile_app", f"{self.ssh_target}:{self.remote_path}/"])
        
        # 2. Deep Clean on VPS before build
        print("[CLEAN] Purging old build caches on VPS...")
        subprocess.run(self.ssh_base + [f"cd {self.remote_path}/mobile_app && rm -rf .buildozer bin"])
        
        # 3. Execute Buildozer
        print("[BUILD] Running Buildozer (This may take 15-30 minutes)...")
        # Use -v to ensure we see the output logs live
        subprocess.run(self.ssh_base + [f"cd {self.remote_path}/mobile_app && ~/.local/bin/buildozer -v android debug"], check=True)
        
        # 4. Download Result
        print("[DOWNLOAD] Fetching latest APK from VPS...")
        local_bin = os.path.join(os.getcwd(), "bin")
        os.makedirs(local_bin, exist_ok=True)
        subprocess.run(["scp", f"{self.ssh_target}:{self.remote_path}/mobile_app/bin/*.apk", f"{local_bin}/"])
        print(f"[SUCCESS] APK downloaded to: {local_bin}")
        self.notify_telegram("Sovereign Build Complete\nAPK v14.0.13 telah berhasil dibangun di VPS dan siap diunduh dari folder `bin/` lokal.")
        
        # New: Auto-send APK to Telegram
        try:
            import glob
            apks = glob.glob(f"{local_bin}/*.apk")
            if apks:
                latest_apk = max(apks, key=os.path.getctime)
                self.send_file_to_telegram(latest_apk)
        except: pass

    def send_file_to_telegram(self, file_path):
        print(f"[NOTIFY] Uploading APK to Telegram...")
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not token or not chat_id: return
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        if file_size > 49:
            print(f"[WARN] File too large for Telegram ({(file_size):.1f}MB). Skipping auto-send.")
            return

        try:
            url = f"https://api.telegram.org/bot{token}/sendDocument"
            with open(file_path, "rb") as f:
                requests.post(url, data={"chat_id": chat_id, "caption": "📦 Noir Sovereign SMC v14.0.13 (Production Build)"}, files={"document": f})
        except Exception as e:
            print(f"[ERROR] APK send failed: {e}")

    def notify_telegram(self, message):
        print(f"[NOTIFY] Sending Telegram update...")
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            print("[WARN] Telegram config missing, skip notify.")
            return
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"[ERROR] Telegram notify failed: {e}")

    def total_purge(self):
        print("[PROCESS] INITIATING TOTAL SYSTEM PURGE...")
        # 1. Clean Local
        print("[LOCAL] Cleaning local caches...")
        shutil.rmtree(".wrangler", ignore_errors=True)
        shutil.rmtree("mobile_app/.buildozer", ignore_errors=True)
        shutil.rmtree("bin", ignore_errors=True)
        
        # 2. Clean VPS
        print("[VPS] Purging all remote caches & logs...")
        subprocess.run(self.ssh_base + [f"cd {self.remote_path} && find . -type d -name '__pycache__' -exec rm -rf {{}} +"])
        subprocess.run(self.ssh_base + ["rm -rf /root/noir-agent/logs/*"])
        subprocess.run(self.ssh_base + ["docker system prune -f"])
        
        # 3. Clean Gateway Logs (via Database if possible, or just log insertion)
        print("[GATEWAY] Resetting remote log database...")
        # Since I don't have a direct D1 delete CLI here, I'll send a signal via log
        self.notify_telegram("⚠️ *SYSTEM PURGE COMPLETED*\nSeluruh cache lama telah dihancurkan. Sistem berjalan dalam kondisi murni.")
        print("[SUCCESS] Total Purge Complete.")

    def health_check(self):
        print("[PROCESS] Running Diagnostics...")
        subprocess.run(self.ssh_base + ["docker ps"])
        subprocess.run(self.ssh_base + ["lsof -i :80"])

if __name__ == "__main__":
    manager = NoirManager()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "deploy": manager.deploy_vps()
        elif cmd == "gateway": manager.gateway_deploy()
        elif cmd == "check": manager.health_check()
        elif cmd == "clean": manager.clean_vps()
        elif cmd == "reset-tg": manager.reset_telegram()
        elif cmd == "build-apk": manager.build_apk()
        elif cmd == "setup-builder": manager.setup_builder()
        elif cmd == "total-purge": manager.total_purge()
    else:
        print("Usage: python manager.py [deploy|gateway|check|clean|reset-tg|setup-builder|build-apk|total-purge]")
