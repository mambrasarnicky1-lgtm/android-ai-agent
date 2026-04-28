import requests, os, base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
GATEWAY = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"

def decrypt(encrypted_data):
    if not encrypted_data: return ""
    password = API_KEY.encode()
    salt = b'noir_sovereign_mesh_v18'
    key = PBKDF2(password, salt, dkLen=32, count=2000)
    raw = base64.b64decode(encrypted_data)
    nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

def fetch():
    print("Fetching Latest Results via Summary...")
    r = requests.get(f"{GATEWAY}/agent/summary", headers={"Authorization": f"Bearer {API_KEY}"})
    try:
        data = r.json()
        results = data.get("commands", [])
    except:
        print(f"Error: Non-JSON response: {r.text}")
        return
    
    for res in results[:5]:
        dev = "UNKNOWN" # Device ID not in summary command list, but result might have it
        out = res.get("result")
        print(f"Command ID: {res.get('id')} | Status: {res.get('status')}")
        if not out:
            print("Output: [Pending/No Result]")
            print("-" * 20)
            continue
        
        try:
            data = json.loads(out) if isinstance(out, str) else out
            print(f"Device: {data.get('device_id')}")
            if data.get("output"):
                print(f"Output (Encrypted): {data['output'][:50]}...")
                dec = decrypt(data['output'])
                print(f"Decrypted: {dec}")
        except:
            print(f"Result Data: {out}")
        print("-" * 20)

if __name__ == "__main__":
    import json
    fetch()
