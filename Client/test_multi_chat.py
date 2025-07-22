import asyncio
import httpx
import time
from datetime import datetime
import random
import argparse
import sys
from requests.auth import HTTPBasicAuth

BASE_URL = "http://127.0.0.1:8000"
# BASE_URL = "http://40.82.161.202:8000"

n_requests = 100
test_duration = 120

# Define a list of test users (userid, password)
test_users = [
    ("user_1", "123123"),
    ("user_2", "123123"),
    # ("testuser3", "testpass3"),
    # ("testuser4", "testpass4"),
    # ("testuser5", "testpass5"),
]

question_list = [
    "Who is Elara?",
    "Who is Barnaby?",
    "My name is Sander.",
    "What is my name?",
    "Where Elara lives?"
]

def parse_args():
    parser = argparse.ArgumentParser(description="Run FastAPI chat load test without pytest.")
    parser.add_argument("--log-to-file", action="store_true", help="Enable logging to file")
    parser.add_argument("--log-to-prompt", action="store_true", help="Enable logging to console")
    return parser.parse_args()

def get_auth(user_index):
    return HTTPBasicAuth(*test_users[user_index % len(test_users)])

async def send_chat(index, user_id, user_index, delay, log_to_prompt, log_to_file, lock, success_count):
    chat_api = f"{BASE_URL}/user/chat"
    history_api = f"{BASE_URL}/user/chat/history"
    await asyncio.sleep(delay)
    message = f"{random.choice(question_list)} {index}"
    try:
        async with httpx.AsyncClient(timeout=20.0) as ac:
            response = await ac.post(
                chat_api,
                json={"user_id": user_id, "message": message},
                auth=get_auth(user_index)
            )
            assert response.status_code == 200
            json_data = response.json()
            assert "response" in json_data
            async with lock:
                success_count["count"] += 1
            await asyncio.sleep(1)
            now = datetime.now()
            history_response = await ac.get(history_api, auth=get_auth(user_index))
            history = history_response.json().get("history", [])
            log_line = (
                f"{'*' * 30}\n"
                f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Request #{index + 1}/{n_requests}\n"
                f"User: {user_id}\n"
                f"Message: {message}\n"
                f"Response: {json_data['response']}\n"
                f"Prompt: {json_data.get('prompt', 'N/A')}\n"
                f"Full History: {history}\n"
                f"{'*' * 30}\n"
            )
            if log_to_prompt:
                print(log_line)
            if log_to_file:
                with open("test_log.txt", "a", encoding="utf-8") as f:
                    f.write(log_line + "\n")
            return json_data["response"]
    except Exception as e:
        error_log = f"[ERROR] Request #{index + 1} failed: {e}\n"
        print(error_log)
        if log_to_file:
            with open("test_log.txt", "a", encoding="utf-8") as f:
                f.write(error_log + "\n")
        return None

def main():
    args = parse_args()
    log_to_file = args.log_to_file
    log_to_prompt = args.log_to_prompt
    # Rotate through test users for each request
    users = [test_users[i % len(test_users)][0] for i in range(n_requests)]
    interval = test_duration / n_requests
    success_count = {"count": 0}
    lock = asyncio.Lock()
    response_times = []

    async def timed_send_chat(index, user_id, user_index, delay):
        t0 = time.time()
        result = await send_chat(index, user_id, user_index, delay, log_to_prompt, log_to_file, lock, success_count)
        t1 = time.time()
        response_times.append(t1 - t0)
        return result

    async def run_all():
        tasks = [
            timed_send_chat(i, users[i], i, i * interval)
            for i in range(n_requests)
        ]
        results = await asyncio.gather(*tasks)
        return results

    start_time = time.time()
    results = asyncio.run(run_all())
    elapsed = time.time() - start_time
    passed = success_count["count"]
    failed = n_requests - passed
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    summary = (
        f"\n✅ {passed} / {n_requests} requests succeeded.\n"
        f"❌ {failed} requests failed.\n"
        f"🕒 Total time elapsed: {elapsed:.2f} seconds\n"
        f"⏱️ Average response time: {avg_response_time:.2f} seconds\n"
    )
    if log_to_prompt:
        print(summary)
    if log_to_file:
        with open("test_log.txt", "a", encoding="utf-8") as f:
            f.write(summary + "\n")
    if failed > 5:
        print(f"❌Test failed❌: {failed} requests failed (allowed <= 5)")
    if elapsed < test_duration * 0.9:
        print(f"❌Test failed❌: elapsed time {elapsed:.2f}s is less than 90% of expected {test_duration}s")
    if failed <= 5 and elapsed >= test_duration * 0.9:
        print("✅Test passed!✅")

if __name__ == "__main__":
    main()
