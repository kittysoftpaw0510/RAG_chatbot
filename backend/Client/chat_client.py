import requests
import getpass
from requests.auth import HTTPBasicAuth

BASE_URL = "http://127.0.0.1:8000"
# BASE_URL = "http://40.82.161.202:8000"

def authenticate():
    print("=== Chat Client Login ===")
    while True:
        user_id = input("User ID: ").strip()
        password = getpass.getpass("Password: ")
        try:
            res = requests.get(f"{BASE_URL}/user/auth/check", auth=HTTPBasicAuth(user_id, password))
            if res.status_code == 200 and res.json().get("success"):
                print("✅ Authentication successful!\n")
                return user_id, password
            else:
                print("❌ Incorrect username or password. Please try again.\n")
        except Exception as e:
            print(f"❌ Error connecting to server: {e}\n")

def print_history(auth):
    history_api = f"{BASE_URL}/user/chat/history"
    try:
        res = requests.get(history_api, auth=auth)
        print("*" * 10)
        if res.status_code == 200:
            history = res.json().get("history", [])
            print("\n--- User Message History ---")
            for i, msg in enumerate(history, 1):
                print(f"{i}: {msg}")
            print("----------------------------\n")
        else:
            print("Failed to fetch history.")
    except Exception as e:
        print(f"Error fetching history: {e}")

def chat():
    chat_api = f"{BASE_URL}/user/chat"

    # Authenticate user first
    user_id, password = authenticate()
    auth = HTTPBasicAuth(user_id, password)
    
    print("Chat started! Type 'exit' or 'quit' to end the session.")
    print("-" * 50)
    
    while True:
        msg = input("You: ")
        if msg.lower() in ("exit", "quit"): 
            print("Goodbye!")
            break
        try:
            res = requests.post(chat_api, json={"user_id": user_id, "message": msg}, auth=auth)
            
            if res.status_code == 200:
                response_data = res.json()
                print_history(auth)
                print("Prompt: ", response_data.get("prompt", ""))
                print("*" * 10)
                print("🤖 Predict:", response_data.get("response", ""))
            else:
                try:
                    error_data = res.json()
                    print(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Error: HTTP {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == "__main__":
    chat()