import requests

def check_dashboard():
    url = "http://8.215.23.17"
    try:
        r = requests.get(url, timeout=10)
        print(f"Status Code: {r.status_code}")
        print(f"Content Type: {r.headers.get('Content-Type')}")
        print("\nFirst 500 characters of content:")
        print(r.text[:500])
    except Exception as e:
        print(f"Error connecting to dashboard: {e}")

if __name__ == "__main__":
    check_dashboard()
