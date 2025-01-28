from locust import task, run_single_user
from locust.contrib.fasthttp import FastHttpUser  # Use FastHttpUser for better performance
from insert_product import login


class Checkout(FastHttpUser):
    # Define the host URL
    host = "http://127.0.0.1:5000"
    
    # Default headers mimicking Chrome
    default_headers = {
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "DNT": "1",
        "Sec-GPC": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    }

    def __init__(self, environment):
        super().__init__(environment)
        self.username = "test123"
        self.password = "test123"

        # Log in and retrieve the token
        cookies = login(self.username, self.password)
        if cookies and "token" in cookies:
            self.token = cookies.get("token")
        else:
            raise ValueError("Login failed: Token not retrieved")

    @task
    def checkout_task(self):
        # Define headers for the checkout request
        headers = {
            **self.default_headers,  # Include default headers
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Cookie": f"token={self.token}",
            "Referer": f"{self.host}/cart",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

        # Perform the checkout request
        with self.client.get("/checkout", headers=headers, catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Checkout failed with status code {resp.status_code}")


if __name__ == "__main__":
    run_single_user(Checkout)
