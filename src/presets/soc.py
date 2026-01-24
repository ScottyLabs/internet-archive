import re

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://enr-apps.as.cmu.edu/assets/SOC/"


def get_outlinks():
    r = requests.get(url, verify=False)
    soc_files = re.findall(r'href="([^"]*\.\w+)"', r.text)

    return [
        {"url": url},
        *[{"url": url + file} for file in soc_files],
    ]

print(get_outlinks())