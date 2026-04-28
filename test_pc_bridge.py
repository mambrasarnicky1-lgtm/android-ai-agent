import requests, os, base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
GATEWAY = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"

def encrypt(data):
    password = API_KEY.encode()
    salt = b'noir_sovereign_mesh_v18'
    key = PBKDF2(password, salt, dkLen=32, count=2000)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

def send_test():
    print("Testing PC Bridge...")
    cmd = "echo 'NOIR PC BRIDGE LINK ESTABLISHED'"
    encrypted = encrypt(cmd)
    
    resp = requests.post(f"{GATEWAY}/agent/command", headers={"Authorization": f"Bearer {API_KEY}"}, json={
        "target_device": "NOIR_PC_MASTER",
        "action": {"type": "pc_shell", "cmd": encrypted},
        "description": "PC Link Verification"
    })
    print(f"Status: {resp.status_code}")
    print(resp.text)

if __name__ == "__main__":
    send_test()
