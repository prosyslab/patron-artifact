import requests
import os
from bs4 import BeautifulSoup
import re

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
FILE_DIR = os.path.dirname(FILE_PATH)
LIST_DIR = os.path.join(FILE_DIR, 'DebianBench', 'crawling_result')  
DEBIAN_URL = "https://packages.debian.org/bookworm/"

def get_debian_packages(url):
    response = requests.get(url)
    if response.status_code == 200:
        html = BeautifulSoup(response.content, 'html.parser')
        
        dl_tags = BeautifulSoup('\n'.join([str(line) for line in list(html.find_all('dl'))]), 'html.parser')
        package_list = dl_tags.find_all('a')
        package_names = [link.get_text() for link in package_list]
        return package_names
    else:
        print("Failed to retrieve the page. Status code:{} on {}".format(response.status_code, url))
        return None


def get_debian(url):
    response = requests.get(url)
    package_lists = dict()
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        dt_class = soup.find_all('dt')

        pattern = r'<dt><a href="([^"]+)/">([^<]+)</a></dt>'
        for dt in dt_class:
            matched = re.search(pattern, str(dt))
            if matched:
                link = url + matched.group(1)
                category = matched.group(2)
                package_lists[category] = []
                out_list = get_debian_packages(link + '/')
                if out_list is None:
                    continue    
                for package in out_list:
                    package = re.sub(r'\(.*\)', '', package)
                    if package == '':
                        continue
                    package_lists[category].append(package)
                package_lists[category] = list(set(package_lists[category]))

        return package_lists
    else:
        print("Failed to retrieve the page. Status code:",
              response.status_code)
        return None


debian_packages = get_debian(DEBIAN_URL)

if debian_packages:
    for category in debian_packages.keys():
        filename = category.replace(' ', '_').replace('/', '_').lower() + '.txt'
        if os.path.exists(os.path.join(LIST_DIR, filename)):
            os.remove(category)
        with open(os.path.join(LIST_DIR, filename), 'w') as f:
            for package in debian_packages[category]:
                f.write(package + '\n')
else:
    print("Failed to retrieve the list of packages.")
