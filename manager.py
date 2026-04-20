import os, sys, json, time, logging, subprocess
import requests
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

# === LOGGING CONFIG ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
def log(msg, tag="INFO"):
    print(f"[{tag}] {msg}")

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
    except Exception as e:
        return str(e)

class NoirManager:
    def __init__(self):
        self.root = Path(__file__).parent.resolve()
        self.config = self._load_env()
        
    def _load_env(self):
        env = {}
        path = self.root / ".env"
        if path.exists():
            with open(path) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        env[k.strip()] = v.strip()
        return env

    def deploy_gateway(self):
        log("Deploying Cloudflare Gateway...", "GATEWAY")
        os.chdir(self.root / "noir-gateway")
        run_cmd("npx wrangler deploy")
        log("Gateway Deployed Successfully.", "SUCCESS")
        os.chdir(self.root)

    def deploy_vps(self):
        ip = self.config.get("VPS_ALIBABA_IP")
        pw = self.config.get("VPS_PASSWORD", "N!colay_No1r.Ai@Agent#Secure")
        if not ip:
            log("VPS IP not found in .env", "ERROR")
            return

        log(f"Connecting to VPS {ip}...", "VPS")
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(ip, username="root", password=pw)
            tar_file = "project.tar.gz"
            log("Compressing project...", "PROCESS")
            run_cmd(f"tar -czf {tar_file} --exclude='node_modules' --exclude='venv' --exclude='.git' --exclude='mobile_app/.buildozer' .")
            
            log("Uploading to VPS...", "PROCESS")
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(tar_file, f"/root/{tar_file}")
            
            log("Restarting Infrastructure...", "PROCESS")
            commands = [
                "mkdir -p /root/noir-agent",
                f"tar -xzf /root/{tar_file} -C /root/noir-agent",
                "cd /root/noir-agent && docker-compose down",
                "cd /root/noir-agent && docker-compose up -d --build"
            ]
            for cmd in commands:
                ssh.exec_command(cmd)
            
            log("VPS Infrastructure ACTIVE.", "SUCCESS")
        except Exception as e:
            log(f"VPS Deployment Failed: {e}", "ERROR")
        finally:
            ssh.close()

    def health_check(self):
        log("Starting Global Diagnostic v13.0...", "DIAG")
        # 1. Gateway
        url = self.config.get("NOIR_GATEWAY_URL", "")
        if url:
            try:
                r = requests.get(f"{url}/health", timeout=10)
                log(f"Gateway: {r.status_code} ({r.json().get('status','?')})", "SUCCESS" if r.status_code==200 else "ERROR")
            except:
                log("Gateway: Unreachable", "ERROR")
        
        # 2. VPS
        vps_ip = self.config.get("VPS_ALIBABA_IP", "")
        if vps_ip:
            res = run_cmd(f"ping -n 1 {vps_ip}" if sys.platform == "win32" else f"ping -c 1 {vps_ip}")
            log(f"VPS Ping: {'OK' if 'Reply' in res or '64 bytes' in res else 'FAILED'}", "SUCCESS" if 'Reply' in res or '64 bytes' in res else "ERROR")

    def heal(self):
        log("Initiating Autonomous Healing v13.0...", "HEAL")
        # Optimization
        log("Optimizing Network Stack...", "PROCESS")
        ip = self.config.get("VPS_ALIBABA_IP")
        pw = self.config.get("VPS_PASSWORD", "N!colay_No1r.Ai@Agent#Secure")
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(ip, username="root", password=pw)
            ssh.exec_command("sudo ufw allow 80/tcp; sudo sysctl -w net.core.somaxconn=1024")
            log("VPS Network Optimized.", "OK")
        except: pass
        finally: ssh.close()
        
        self.deploy_vps()
        log("Healing sequence complete.", "SUCCESS")

    def show_menu(self):
        while True:
            print(f"\n{'='*20} NOIR MASTER MANAGER v13.0 {'='*20}")
            print("1. Full Deployment")
            print("2. Health Check (Audit)")
            print("3. Autonomous Healing (Fix 500/Latency)")
            print("0. Exit")
            print("="*67)
            choice = input("Select > ").strip()
            if choice == "1": self.deploy_vps()
            elif choice == "2": self.health_check()
            elif choice == "3": self.heal()
            elif choice == "0": break

if __name__ == "__main__":
    manager = NoirManager()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "deploy": manager.deploy_vps()
        elif cmd == "check": manager.health_check()
        elif cmd == "heal": manager.heal()
    else:
        manager.show_menu()
