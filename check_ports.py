import socket

def check_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((ip, port))
        print(f"Port {port} is OPEN")
        return True
    except:
        print(f"Port {port} is CLOSED")
        return False
    finally:
        s.close()

if __name__ == "__main__":
    ip = "8.215.23.17"
    check_port(ip, 80)
    check_port(ip, 8080)
    check_port(ip, 5000)
    check_port(ip, 22)
