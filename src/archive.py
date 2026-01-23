import os
import random
import time

import requests
from dotenv import load_dotenv


class Archiver:
    def __init__(self, max_retries: int = 10, debug: bool = False, max_requests_per_min: int = 12, cooldown_time: int = 180):
        load_dotenv()

        save_url = os.getenv("INTERNET_ARCHIVE_SPN2_URL")
        status_url = os.getenv("INTERNET_ARCHIVE_STATUS_CHECK_URL")
        access_key = os.getenv("INTERNET_ARCHIVE_ACCESS_KEY")
        secret_key = os.getenv("INTERNET_ARCHIVE_PRIVATE_KEY")

        if not save_url or not status_url or not access_key or not secret_key:
            raise ValueError("Missing environment variables")

        self.save_url = save_url
        self.status_url = status_url
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"LOW {access_key}:{secret_key}",
        }

        self.max_retries = max_retries
        self.debug = debug
        self.fails = 0
        self.requests_made = 0
        self.max_requests_per_min = max_requests_per_min
        self.cooldown_time = cooldown_time

    def _backoff(self):
        self.fails += 1
        if self.fails > self.max_retries:
            raise MaxRetriesExceeded(f"Exceeded {self.max_retries} retries")

        delay = (2 ** (self.fails - 1)) + random.random()
        print(
            f"Backing off for {delay:.1f}s (attempt {self.fails}/{self.max_retries})")
        time.sleep(delay)

    def _rate_limit(self):
        self.requests_made += 1

        if (self.requests_made >= self.max_requests_per_min):
            print(
                f"Stopping requests for {self.cooldown_time} seconds to avoid the rate limit...")
            time.sleep(self.cooldown_time)
            self.requests_made = 0

    def _request(self, method: str, url: str, **kwargs):
        while True:
            try:
                r = requests.request(
                    method, url, headers=self.headers, **kwargs)
                if r.ok:
                    self.fails = 0  # reset on success
                    return r

                if self.debug:
                    print(f"Status: {r.status_code}, Response: {r.text}")

                self._backoff()
            except requests.RequestException as e:
                print(f"Request error: {e}")
                self._backoff()

    def archive(self, link: str | dict) -> bool:
        if isinstance(link, str):
            payload = {"url": link}
        else:
            payload = link.copy()
            link = payload["url"]

        payload["capture_all"] = "1"

        print(f"Submitting {link}")

        r = self._request("POST", self.save_url, data=payload)
        job_id = r.json()["job_id"]
        status_url = self.status_url + job_id

        return status_url

    def check_status(self, status_url: str) -> bool:
        while True:
            print(f"Checking status of {status_url}")
            r = self._request("GET", status_url)
            response = r.json()

            if response["status"] == "success":
                print(f"Finished archiving {status_url}!")
                return True
            elif response["status"] == "pending":
                print("Still waiting on server to finish...")
                time.sleep(10 + 5 * random.random())
            else:
                print(f"Error archiving {status_url}: {response}")
                return False

    def archive_all(self, links: list[str | dict]) -> bool:
        success = True
        status_urls = []
        for link in links:
            self._rate_limit()
            try:
                self.fails = 0
                status_urls.append(self.archive(link))
            except MaxRetriesExceeded as e:
                print(f"Failed to archive {link}: {e}")
                success = False

        for status_url in status_urls:
            self._rate_limit()
            try:
                self.fails = 0
                success = self.check_status(status_url)

            except MaxRetriesExceeded as e:
                print(f"Failed to check the status of {status_url}: {e}")
                success = False

        return success


class MaxRetriesExceeded(Exception):
    pass
