import paramiko, threading, time, select, os, socketserver
from pathlib import Path
from dotenv import load_dotenv

# Load env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

class ForwardServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel(
                "direct-tcpip",
                (self.chain_host, self.chain_port),
                self.request.getpeername(),
            )
        except Exception as e:
            print(f"Incoming request to {self.chain_host}:{self.chain_port} failed: {e}")
            return

        if chan is None:
            return

        try:
            while True:
                r, w, x = select.select([self.request, chan], [], [])
                if self.request in r:
                    data = self.request.recv(1024)
                    if len(data) == 0: break
                    chan.send(data)
                if chan in r:
                    data = chan.recv(1024)
                    if len(data) == 0: break
                    self.request.send(data)
        except Exception:
            pass
        finally:
            chan.close()
            self.request.close()

def start_tunnel(local_port, remote_host, remote_port, ssh_host, ssh_user, ssh_password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to SSH {ssh_host}...")
        client.connect(ssh_host, username=ssh_user, password=ssh_password)
        print(f"SSH Connected. Bridging localhost:{local_port} -> VPS:{remote_port}...")
        
        class SubHandler(Handler):
            chain_host = remote_host
            chain_port = remote_port
            ssh_transport = client.get_transport()

        server = ForwardServer(("127.0.0.1", local_port), SubHandler)
        server.serve_forever()
    except Exception as e:
        print(f"Tunnel Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    ssh_ip = os.environ.get("NOIR_VPS_IP")
    ssh_pass = os.environ.get("NOIR_VPS_PASS")
    if not ssh_ip or not ssh_pass:
        print("[ERROR] NOIR_VPS_IP or NOIR_VPS_PASS not found in environment.")
    else:
        start_tunnel(55555, "127.0.0.1", 8888, ssh_ip, "root", ssh_pass)
