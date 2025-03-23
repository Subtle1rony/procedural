import os
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import requests
from urllib.parse import urlparse

# Set up the browser driver (e.g., Brave)
brave_path = r'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
# chromedriver = "/chromedriver"
options = webdriver.ChromeOptions()
options.binary_location = brave_path
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")

# Create downloads directory if it doesn't exist
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

driver = webdriver.Chrome(options=options)

webpage_url = "http://threedscans.com/"    

def scrape_and_save_list():
    # Send a GET request to the webpage
    driver.get(webpage_url)

    # Wait for 5 seconds to ensure the page has fully loaded
    time.sleep(15)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    links = []
    for article in soup.find_all('article'):
        for section in article.find_all('section'):
            for a_tag in section.find_all('a'):
                href = a_tag.get('href')
                if href:
                    links.append(href)

    # print(links)

    with open('links.json', 'w') as f:
        json.dump(links, f, indent=4)

def download_file(url, filename):
    """
    Download a file from URL and save it to the downloads directory
    Returns True if successful, False otherwise
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def download_files():
    with open('links.json', 'r') as f:
        links = json.load(f)

    for link in links:
        try:
            print(f"Processing: {link}")
            # Navigate to the URL
            driver.get(link)
            time.sleep(5)  # Wait for page to load

            # Parse HTML content
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the download link
            download_div = soup.find('div', class_='stlDL')
            if download_div:
                download_link = download_div.find('a')['href']
                print(f"Found download link: {download_link}")
                
                # Extract filename from URL
                filename = os.path.basename(urlparse(download_link).path)
                if not filename:
                    filename = f"model_{int(time.time())}.stl"
                
                # Check if file already exists
                if os.path.exists(os.path.join(DOWNLOADS_DIR, filename)):
                    print(f"File {filename} already exists, skipping...")
                    continue
                
                # Download the file
                if download_file(download_link, filename):
                    print(f"Successfully downloaded: {filename}")
                else:
                    print(f"Failed to download: {filename}")
            else:
                print(f"No download link found for: {link}")
                
        except Exception as e:
            print(f"Error processing {link}: {str(e)}")
            continue

if __name__ == '__main__':
    # scrape_and_save_list()
    download_files()




