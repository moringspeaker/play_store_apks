import requests
from bs4 import BeautifulSoup
import json
import re

URL = 'https://proxy-tools.com/proxy/http'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
}
ip_list= []
r = requests.get(URL, headers=HEADERS)
soup =BeautifulSoup(r.text, 'lxml')
td_elements = soup.find_all('td', class_='text-monospace')
# Print the text content of each <td> element
for td in td_elements:
   ip = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', str(td))
   ip_list.append(ip)

filtered_list = [item for item in ip_list if item]

with open('ip_list.json', 'w') as file:
    json.dump(filtered_list, file, indent=4)