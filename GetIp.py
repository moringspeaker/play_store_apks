import requests
from bs4 import BeautifulSoup
import json
import re

URL = 'https://proxy-tools.com/proxy/http'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
}


def test_proxy(ip, port, test_url="https://httpbin.org/ip", timeout=5):
    """
    Test if a proxy is working.
    """
    proxies = {
        "http": f"http://{ip}:{port}",
        "https": f"http://{ip}:{port}"
    }

    try:
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pass

    return False


ip_list = []
r = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(r.text, 'lxml')
td_elements = soup.find_all('td', class_='text-monospace')
# Print the text content of each <td> element
for td in td_elements:
   ip = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', str(td))
   ip_list.append(ip)

filtered_list = [item for item in ip_list if item]

working_proxies = []
for ip in filtered_list:
    ip_address = ip[0]
    if test_proxy(ip_address, 80):
        working_proxies.append(ip[0])


with open('ip_list.json', 'w') as file:
    json.dump(filtered_list, file, indent=4)
