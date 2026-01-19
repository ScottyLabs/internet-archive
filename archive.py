import requests
from dotenv import load_dotenv
from dotenv import find_dotenv
import os
import time
import random


def print_debug(r):
    print("Status Code:", r.status_code)
    print("Response JSON:", r.json())

# Please only tiny websites, otherwise this might crash
# Will return true if it was successsful, otherwise will return false


def archive(link, debug):
    # Starts system clock
    start = time.time()

    # Loads in the ACCESS_KEY AND SECRET_KEY
    load_dotenv()

    url = os.getenv('INTERNET_ARCHIVE_SPN2_URL')
    ACCESS_KEY = os.getenv('INTERNET_ARCHIVE_ACCESS_KEY')
    SECRET_KEY = os.getenv('INTERNET_ARCHIVE_PRIVATE_KEY')

    if not url or not ACCESS_KEY or not SECRET_KEY:
        print("Error: Missing environment variables.")
        return

    headers = {'Accept': 'application/json',
               'Authorization': f'LOW {ACCESS_KEY}:{SECRET_KEY}'}

    # Ensures that the command is done properly
    cleaned_link = link

    # if not link.startswith('http'):
    #     cleaned_link = 'https://' + link

    if link[-1] != '/':
        cleaned_link += '/'

    payload = {'url': cleaned_link,
               'capture_outlinks': '1', 'capture_all': '1'}

    try:
        r = requests.post(url, data=payload, headers=headers)
        if r.ok:
            job_id = r.json()["job_id"]

            url = os.getenv('INTERNET_ARCHIVE_STATUS_CHECK_URL') + job_id

            # continue looping until we get successful or fail
            while True:
                print(f'Archiving {link} ... ({time.time() - start:.1f}s)')

                if debug:
                    print_debug(r)

                try:
                    r = requests.get(url, headers=headers)

                    was_successful = False

                    if r.ok:
                        response = r.json()

                        if response['status'] == 'success':
                            print(
                                f'Finished archiving {link}! ({time.time() - start:.1f}s)')
                            was_successful = True

                        elif response['status'] == 'pending':
                            pass
                        # something went wrong with the request, abort
                        else:
                            print(f"Error occured while archiving {link}!")
                            print_debug(r)

                    if was_successful:
                        if debug:
                            print_debug(r)
                        return True

                except:
                    print("Could not access server!")
                    if debug:
                        print_debug
                    return False

                # pause time, wait a random time (20,25) so it seems like process is random
                # also so we don't hit a rate limit, change numbers here if we think we hit a rate limit
                pause_time = 20 + 5 * random.random()

                time.sleep(pause_time)

        else:
            print(f'Could not archive {link}!')
            if debug:
                print_debug(r)

    except Exception as e:
        print(f'Could not archive {link}!')
        print('Error: ', e)
        if debug:
            print("Status Code:", r.status_code)
            print("Response JSON:", r.json())

    return False
