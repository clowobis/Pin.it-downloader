import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import system
import re
from datetime import datetime


def clear_console():
    system("cls")


def is_valid_pinterest_url(url):
    return "pinterest.com/pin/" in url or "https://pin.it/" in url


def get_original_pin_url(short_url):
    response = requests.get(short_url)
    if response.status_code != 200:
        print("Entered URL is invalid or not working.")
        return None
    soup = BeautifulSoup(response.content, "html.parser")
    href_link = soup.find("link", rel="alternate")['href']
    match = re.search('url=(.*?)&', href_link)
    if match:
        return match.group(1)
    return None


def fetch_page_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Entered URL is invalid or not working.")
        return None
    return response.content


def find_video_url(soup):
    video_tag = soup.find("video", class_="hwa kVc MIw L4E")
    if video_tag:
        video_url = video_tag['src']
        return video_url.replace("hls", "720p").replace("m3u8", "mp4")
    return None


def find_image_urls(soup):
    image_tags = soup.find_all("img", class_="hCL kVc L4E MIw")
    image_urls = []
    for img in image_tags:
        img_url = img.get('src')
        if img_url:
            image_urls.append(img_url)
    
    return image_urls


def download_file(url, filename):
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get('Content-Length', 0))
    progress = tqdm(response.iter_content(1024), f'Downloading {filename}', 
                    total=file_size, unit='B', unit_scale=True, unit_divisor=1024)
    with open(filename, 'wb') as file:
        for data in progress.iterable:
            file.write(data)
            progress.update(len(data))


def download_media(media_urls, file_prefix, extension):
    for i, url in enumerate(media_urls):
        filename = f"{file_prefix}_{i+1}_{datetime.now().strftime('%d_%m_%H_%M_%S')}.{extension}"
        download_file(url, filename)
        print(f"Downloaded: {filename}")

def main():
    clear_console()
    page_url = input("Enter page URL: ")

    if not is_valid_pinterest_url(page_url):
        print("Entered URL is invalid.")
        return

    if "https://pin.it/" in page_url:
        print("Extracting original pin link...")
        page_url = get_original_pin_url(page_url)
        if not page_url:
            return
            
    print("Fetching content from given URL...")
    page_content = fetch_page_content(page_url)
    if not page_content:
        return

    soup = BeautifulSoup(page_content, "html.parser")
    print("Fetched content successfully.")

    video_url = find_video_url(soup)
    if video_url:
        print("Downloading video now!")
        download_media([video_url], "video", "mp4")
    else:
        print("No video found on this page.")

    image_urls = find_image_urls(soup)
    if image_urls:
        print(f"Found {len(image_urls)} image(s). Downloading now!")
        download_media(image_urls, "image", "jpg")
    else:
        print("No images found on this page.")

if __name__ == "__main__":
    main()
