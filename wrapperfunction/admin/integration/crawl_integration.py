import json
from wrapperfunction.admin.integration.storage_connector import upload_file_to_azure
import wrapperfunction.core.config as config
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


AZURE_STORAGE_CONNECTION_STRING = config.STORAGE_CONNECTION
BLOB_CONTAINER_NAME = config.BLOB_CONTAINER_NAME
SUBFOLDER_NAME = config.SUBFOLDER_NAME


def get_all_Links_in_urls(urls: list):
    try:
        media_settings = config.ENTITY_SETTINGS.get("media_settings",{})
        # Extract the list of web URLs and target classes
        web_urls = media_settings.get("web_urls", [])
        target_classes = media_settings.get("a_class", [])
        
        # Initialize a list to store the links
        news_links_list = []

        # Iterate over the provided URLs
        for url in urls:
            # If the URL is not in the list of web URLs in the config, skip it
            if url not in web_urls:
                print(f"URL {url} is not in the configured web URLs. Skipping.")
                continue

            # Fetch and parse the HTML content of the URL
            response = requests.get(url)
            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")

            # Initialize a list to store links for the current URL
            links = []

            # Search for <div> elements with the specified classes
            for div_class in target_classes:
                divs = soup.find_all("div", class_=div_class)

                # Within each <div>, find all <a> tags and retrieve their href attributes
                for div in divs:
                    for link in div.find_all("a", href=True):
                        href = link["href"]
                        if "#" not in href:
                            # If href is relative, convert it to an absolute URL
                            absolute_href = urljoin(url, href) if not href.startswith(url) else href
                            if absolute_href not in links:
                                links.append(absolute_href)                       

            # Add the URL and its links to the final JSON structure
            news_links_list.append({
                "url": url,
                "links": links
            })

        return news_links_list

    except Exception as e:
        return f"ERROR getting links: {str(e)}"

def save_media_with_topics(news_links: list, topics: list, container_name: str, connection_string: str):
    try:
        media_settings = config.ENTITY_SETTINGS.get("media_settings",{})
        # Extract target classes for p and img
        target_p_classes = media_settings.get("p_class", [])
        target_img_classes = media_settings.get("img_class", [])

        for entry in news_links:
            url = entry["url"]
            links = entry["links"]

            for link in links:
                print(f"\nProcessing Link from {url}: {link}\n\n")
                response = requests.get(link)
                html_content = response.content

                soup = BeautifulSoup(html_content, "html.parser")

                # Initialize sets to store unique texts and filtered image links
                relevant_texts = set()
                filtered_imgs_links = set()

                # Find div elements with specified p_class and extract unique paragraphs
                for p_class in target_p_classes:
                    for div in soup.find_all("div", class_=p_class):
                        for p_tag in div.find_all("p"):
                            paragraph_text = p_tag.get_text(strip=True)
                            if any(topic in paragraph_text for topic in topics):
                                relevant_texts.add(paragraph_text)

                # Find div elements with specified img_class and extract unique image URLs
                for img_class in target_img_classes:
                    for div in soup.find_all("div", class_=img_class):
                        for img_tag in div.find_all("img"):
                            img_url = img_tag.get("src")
                            print(f"url:{img_url}\n")
                            if img_url:
                                #TODO edit logo
                                if "logo" not in img_url and is_valid_url(img_url, url):
                                    if str(img_url).endswith(tuple([".png",".PNG",".JPG",".jpg",".jpeg",".JPEG"])): 
                                        # Convert to absolute URL if it's relative
                                        absolute_img_url = img_url if img_url.startswith('https') else urljoin(url, img_url)
                                        filtered_imgs_links.add(absolute_img_url)
                                else:
                                    print(f"NOT Valid IMG_URL:{img_url}")
                print(f"IMGS:\n{filtered_imgs_links}")
                if relevant_texts:
                    # Prepare JSON data to store in Azure Blob
                    content_data = {
                        "ref_url": url,
                        "url": link,
                        "content": "\n".join(relevant_texts),
                        "images_urls": list(filtered_imgs_links)
                    }

                    # Convert JSON data to string for upload
                    json_content = json.dumps(content_data, ensure_ascii=False)
                    
                    # Create the JSON filename
                    link_filename = f"{link.replace('https://', '').replace('/', '_')}"
                    folder_name = f"{url.replace('https://', '').replace('/', '_')}"
                    blob_name = f"{folder_name}/{link_filename}.json"
                    
                    # Upload the JSON to Azure Blob Storage
                    upload_file_to_azure(json_content, container_name, blob_name, connection_string)

    except Exception as e:
        print(f"ERROR Saving Results: {str(e)}")
        
def is_valid_url(img_url, base_url):
    try:
        # Combine with base URL if img_url is relative
        absolute_url = urljoin(base_url, img_url)
        if img_url.startswith(('http', 'https')):
            absolute_url = img_url

        # Parse and validate URL format
        parsed_url = urlparse(absolute_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False

        # Send a HEAD request to check if the URL is reachable
        response = requests.head(absolute_url, allow_redirects=True)
        if response.status_code == 200:
            return True
        return False

    except Exception as e:
        print(f"Error checking URL {img_url}: {e}")
        return False
