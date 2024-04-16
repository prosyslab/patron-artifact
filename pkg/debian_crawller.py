import requests
from bs4 import BeautifulSoup
import re


def get_debian_packages(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        package_links = soup.find_all('a')

        package_names = [link.get_text() for link in package_links]

        return package_names
    else:
        print("Failed to retrieve the page. Status code:",
              response.status_code)
        return None


def get_debian(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        dt_class = soup.find_all('dt')

        target_urls = [
            url + re.findall(r'href="([^"]*)"', str(dt))[0] for dt in dt_class
        ]

        package_lists = [get_debian_packages(target) for target in target_urls]

        return package_lists
    else:
        print("Failed to retrieve the page. Status code:",
              response.status_code)
        return None


debian_url = "https://packages.debian.org/bookworm/"

debian_packages = get_debian(debian_url)

if debian_packages:
    debian_packages = [
        re.sub(r'\(.*\)', '', x) for xs in debian_packages for x in xs
    ]
    filtered_packages = set([x for x in debian_packages if x != ''])

    with open('debian_packages.txt', 'w') as f:
        for package in filtered_packages:
            f.write(f"{package}\n")
else:
    print("Failed to retrieve the list of packages.")
