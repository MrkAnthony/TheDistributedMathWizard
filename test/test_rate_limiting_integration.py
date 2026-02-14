import pytest
import requests
import time
import valkey
import uuid
import os
from concurrent.futures import ThreadPoolExecutor


BASE_URL = "http://localhost"


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset Valkey counters before each test"""
    client = valkey.Valkey(
        host=os.getenv("VALKEY_HOST", "localhost"),
        port=int(os.getenv("VALKEY_PORT", 6379))
    )
    client.flushdb()
    time.sleep(0.5)  # Brief pause to let NGINX rate limit window reset
    yield

    client.flushdb()


class TestLayer1_NGINX:
    """Test NGINX rate limiting (5 req/s with burst=10)"""

    def test_requests_within_limit_succeed(self):
        """Normal usage should work fine"""
        for _ in range(5):
            response = requests.get(f"{BASE_URL}/whoami")
            assert response.status_code == 200

    def test_exceeding_burst_returns_429(self):
        """Flooding should trigger NGINX 429"""
        responses = []

        # Send 20 requests as fast as possible (exceeds burst=10)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(requests.get, f"{BASE_URL}/whoami") for _ in range(20)]
            responses = [f.result() for f in futures]

        status_codes = [r.status_code for r in responses]

        # Some should succeed, some should be 429
        assert 200 in status_codes, "Some requests should succeed"
        assert 429 in status_codes or 503 in status_codes, "Some requests should be rate limited"

    def test_recovers_after_waiting(self):
        """After being limited, waiting should allow new requests"""
        # Trigger rate limit
        for _ in range(15):
            requests.get(f"{BASE_URL}/whoami")

        # Wait for limit to reset
        time.sleep(2)

        # Should work again
        response = requests.get(f"{BASE_URL}/whoami")
        assert response.status_code == 200


class TestLayer2_Valkey:
    """Test Flask-Limiter rate limiting (100 req/min)"""
    def test_under_limit_succeeds(self):
        """Requests under 100/min should work"""
        response = requests.post(f"{BASE_URL}/task", params={"a": 1, "b": 2, "operation": "add"})
        assert response.status_code in [202]

    def test_exceeding_100_per_minute_returns_429(self):
        """Exceeding 100 requests in a minute should trigger 429"""
        def make_request():
            return requests.post(f"{BASE_URL}/task", params={"a": 1, "b": 2, "operation": "add"}).status_code

    # Send 110 requests concurrently (fast, within one rate limit window)
        with ThreadPoolExecutor(max_workers=20) as executor:
            responses = list(executor.map(lambda _: make_request(), range(110)))

        success_count = responses.count(200) + responses.count(201) + responses.count(202)
        limited_count = responses.count(429)

        print(f"\nSuccess: {success_count}, Limited: {limited_count}")

        assert success_count <= 100, f"Should not exceed 100 successful requests, got {success_count}"
        assert limited_count > 0, "Should have some 429 responses"

    def test_verify_rate_limit_storage(self):
        """Verify Flask-Limiter is using Valkey, not memory"""
        client = valkey.Valkey(
            host=os.getenv("VALKEY_HOST", "localhost"),
            port=int(os.getenv("VALKEY_PORT", 6379))
        )
        # Clear first
        client.flushdb()

        # Make 5 requests
        for _ in range(5):
            requests.post(f"{BASE_URL}/task", params={"a": 1, "b": 2, "operation": "add"})

        # Check if any rate limit keys were created
        keys = client.keys("*")
        print(f"Keys in Valkey: {keys}")

        # If no keys, Flask-Limiter isn't using Valkey
        assert len(keys) > 0, "No keys found! Flask-Limiter is using MemoryStorage, not Valkey!"


class TestLayerInteraction:
    """Test that both layers work together"""
    def test_nginx_blocks_before_flask(self):
        """Fast flooding should be caught by NGINX, not Flask"""
        responses = []

        # Send requests extremely fast
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(requests.get, f"{BASE_URL}/whoami") for _ in range(50)]
            responses = [f.result() for f in futures]

        # Check that 429s came from NGINX (no response body or specific header)
        for r in responses:
            if r.status_code == 429:
                # NGINX 429 typically has empty or minimal body
                # Flask-Limiter 429 would have your custom response
                assert len(r.text) == 0 or "nginx" in r.headers.get("server", "").lower()