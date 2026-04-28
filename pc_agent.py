import os, time, json, subprocess, requests, base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from dotenv import load_dotenv

# Load env from workspace
load_dotenv()

# --- CONFIG ---
GATEWAY   = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY   = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID = "NOIR_PC_MASTER" # Unique ID for the PC
HEADERS   = {"Authorization": f"Bearer {API_KEY}"}

class SecureVault:
    @staticmethod
    def _get_key():
        password = API_KEY.encode()
        salt = b'noir_sovereign_mesh_v18'
        return PBKDF2(password, salt, dkLen=32, count=2000)

    @staticmethod
    def decrypt(encrypted_data: str):
        if not encrypted_data: return ""
        try:
            key = SecureVault._get_key()
            raw = base64.b64decode(encrypted_data)
            nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
        except: return ""

    @staticmethod
    def encrypt(data: str):
        key = SecureVault._get_key()
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

def pc_loop():
    print(f"[INIT] [NOIR PC BRIDGE] Initialized as {DEVICE_ID}")
    print(f"[LINK] [GATEWAY] {GATEWAY}")
    
    while True:
        try:
            # Poll for PC commands from Gateway
            resp = requests.get(f"{GATEWAY}/agent/poll", headers=HEADERS, params={"device_id": DEVICE_ID}, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                commands = data.get("commands", [])
                for cmd in commands:
                    action = cmd.get("action", {})
                    if action.get("type") == "pc_shell":
                        encrypted_cmd = action.get("cmd", "")
                        real_cmd = SecureVault.decrypt(encrypted_cmd)
                        
                        print(f"[*] Executing PC Command: {real_cmd}")
                        try:
                            result = subprocess.run(real_cmd, shell=True, capture_output=True, text=True, timeout=30)
                            output = (result.stdout + result.stderr).strip()
                            success = result.returncode == 0
                        except Exception as e:
                            output = str(e)
                            success = False
                            
                        # Post result
                        requests.post(f"{GATEWAY}/agent/result", headers=HEADERS, json={
                            "command_id": cmd.get("command_id"),
                            "device_id": DEVICE_ID,
                            "success": success,
                            "output": SecureVault.encrypt(output)
                        }, timeout=10)
            
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    pc_loop()
