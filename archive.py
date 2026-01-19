import requests
from dotenv import load_dotenv
from dotenv import find_dotenv
import os

# Please only tiny websites, otherwise this might crassh


def archive(link):
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
            print(f'Successfully archived {link}!')
        else:
            print(f'Could not archive {link}!')
        print("Status Code:", r.status_code)
        print("Response JSON:", r.json())
    except:
        print(f'Could not archive {link}')
