import os
import random
import time

import requests
from dotenv import load_dotenv


def print_debug(r):
    print("Status Code:", r.status_code)
    print("Response JSON:", r.json())


# Please only tiny websites, otherwise this might crash
# Returns true if it was successful, otherwise returns false
def archive(link, debug):
    # Starts system clock
    start = time.time()

    # Loads in the ACCESS_KEY AND SECRET_KEY
    load_dotenv()

    url = os.getenv("INTERNET_ARCHIVE_SPN2_URL")
    ACCESS_KEY = os.getenv("INTERNET_ARCHIVE_ACCESS_KEY")
    SECRET_KEY = os.getenv("INTERNET_ARCHIVE_PRIVATE_KEY")

    if not url or not ACCESS_KEY or not SECRET_KEY:
        print("Error: Missing environment variables.")
        return

    headers = {
        "Accept": "application/json",
        "Authorization": f"LOW {ACCESS_KEY}:{SECRET_KEY}",
    }

    payload = {"url": link, "capture_outlinks": "1", "capture_all": "1"}

    try:
        r = requests.post(url, data=payload, headers=headers)
        if r.ok:
            job_id = r.json()["job_id"]

            url = os.getenv("INTERNET_ARCHIVE_STATUS_CHECK_URL") + job_id

            # continue looping until we get successful or fail
            while True:
                print(f"Archiving {link} ... ({time.time() - start:.1f}s)")

                if debug:
                    print_debug(r)

                try:
                    r = requests.get(url, headers=headers)

                    if r.ok:
                        response = r.json()

                        if response["status"] == "success":
                            print(
                                f"Finished archiving {link}! ({time.time() - start:.1f}s)"
                            )
                            if debug:
                                print_debug(r)
                            return True

                        elif response["status"] == "pending":
                            pass
                        # something went wrong with the request, abort
                        else:
                            print(f"Error occured while archiving {link}!")
                            print_debug(r)
                            return False

                except Exception:
                    print("Could not access server!")
                    if debug:
                        print_debug(r)
                    return False

                # pause time, wait a random time (20,25) so it seems like process is random
                # also so we don't hit a rate limit, change numbers here if we think we hit a rate limit
                pause_time = 20 + 5 * random.random()

                time.sleep(pause_time)

        else:
            print(f"Could not archive {link}!")
            print_debug(r)

    except Exception as e:
        print(f"Could not archive {link}!")
        print("Error: ", e)

    return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Archive a website using the Internet Archive's Save Page Now 2 API"
    )
    parser.add_argument("url", help="URL to archive")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    success = archive(args.url, args.debug)
    exit(0 if success else 1)
