import pytest
import asyncio
import httpx
import time

# Test 10 parallel requests to the running server
@pytest.mark.asyncio
async def test_server_concurrent_requests():
    n_requests = 5
    users = [f"user_{i%10}" for i in range(n_requests)]
    messages = [f"Test message {i}" for i in range(n_requests)]

    async def send_chat(user_id, message):
        async with httpx.AsyncClient(timeout=10.0) as ac:
            response = await ac.post("http://localhost:8000/chat", json={"user_id": user_id, "message": message})
            assert response.status_code == 200
            assert "response" in response.json()
            return response.json()["response"]

    tasks = [send_chat(users[i], messages[i]) for i in range(n_requests)]
    results = await asyncio.gather(*tasks)
    assert len(results) == n_requests

@pytest.mark.asyncio
async def test_server_100_requests_per_minute():
    n_requests = 100
    users = [f"user_{i%10}" for i in range(n_requests)]
    messages = [f"Test message {i}" for i in range(n_requests)]
    interval = 60 / n_requests  # seconds between requests

    async def send_chat(user_id, message, delay):
        await asyncio.sleep(delay)
        async with httpx.AsyncClient(timeout=10.0) as ac:
            response = await ac.post("http://localhost:8000/chat", json={"user_id": user_id, "message": message})
            assert response.status_code == 200
            assert "response" in response.json()
            return response.json()["response"]

    tasks = [
        send_chat(users[i], messages[i], i * interval)
        for i in range(n_requests)
    ]
    start = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start

    assert len(results) == n_requests
    assert elapsed >= 60  # Should take at least 60 seconds