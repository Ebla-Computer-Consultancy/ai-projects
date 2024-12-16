import json
import re
from urllib.parse import urljoin
import requests

from bs4 import BeautifulSoup
from fastapi import HTTPException
import validators

from wrapperfunction.document_intelligence.service.document_intelligence_service import inline_read_scanned_pdf
from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings, IndexingType
from wrapperfunction.admin.service.blob_service import append_blob
from wrapperfunction.core import config
from wrapperfunction.core.config import SUBFOLDER_NAME
from wrapperfunction.core.utls.helper import process_text_name

global allow_domains
allow_domains = set()
global crawled_sites
crawled_sites = set()
base_url = ""


def crawl_urls(urls: list[CrawlRequestUrls], settings: CrawlSettings):
    for url in urls:
        if validators.url(url.link):
            start_with = url.link.split('//')[0]
            domain_name = url.link.replace("https://", "").replace("http://", "").split("/")[0]
            
            global base_url
            base_url = start_with + '//' + domain_name

            allow_domains.add(domain_name)
            orchestrator_function(url, url.settings if url.settings else settings)

        else:
            raise HTTPException(status_code=400, detail="The URL was invalid.")
    return "crawled successfully"


def orchestrator_function(
    url: CrawlRequestUrls,
    settings: CrawlSettings,
):
    try:
        data, response = crawl_site(
            url.link, cookies=url.cookies, headers=url.headers, payload=url.payload
        )
        if settings.mediaCrawling:
            relevant_text, imgs_links = get_page_media_with_topics(data, settings.topics)
            site_data = {
                "ref_url": base_url,
                "url": url.link,
                "content": relevant_text,
                "images_urls": imgs_links
            }
        else:
            if response.headers.get('Content-Type') == 'application/pdf': 
                site_data = {
                    "url": url.link,
                    "title": get_page_title(url.link),
                    "content": data,
                }
                settings.deep = False
            else:
                site_data = {
                    "url": url.link,
                    "title": get_page_title(url.link, data),
                    "content": get_page_content(data, settings),
                }
                

        json_data = json.dumps(site_data, ensure_ascii=False)
        blob_name = f"item_{process_text_name(url.link)}.json"
        append_blob(
            folder_name=SUBFOLDER_NAME,
            blob_name=blob_name,
            blob=json_data,
            container_name=settings.containerName,
            metadata_1=url.link[:-1],
            metadata_2=url.link,
            metadata_3=IndexingType.CRAWLED.value,
            metadata_4="link",
        )
        crawled_sites.add(url.link)
        if settings.deep:
            collect_urls(data, url, settings)

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Error while making a request to the site: {error.__cause__}",
        )


def crawl_site(
    url: str,
    headers: dict,
    payload: dict,
    cookies: dict = {},
):
    cookies["user-agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    response = requestUrl(url, headers, payload, cookies)
    if response.headers.get('Content-Type') == 'application/pdf':
        return inline_read_scanned_pdf(None, response.content), response
    else:
        return BeautifulSoup(response.text, "lxml"), response


def requestUrl(
    url: str,
    headers: dict,
    payload: dict,
    cookies: dict,
):
    return requests.get(
        url,
        allow_redirects=False,
        verify=False,
        cookies=cookies,
        headers=headers,
        data=payload,
    )


# Extracts the page title.
def get_page_title(link, data = None):
    try:
        if data and data.title:
            return data.title.string
        else:
            return link.split("/")[-1].split(".")[0]
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving the site title: {error.__cause__}",
        )


# Gets all of the URLs from the webpage.
def collect_urls(data, url, settings:CrawlSettings):
    try:
        url_elements = data.select("a[href]")
        for url_element in url_elements:
            absolute_url = (
                url_element["href"]
                if url_element["href"].startswith(('http', 'https'))
                else urljoin(base_url, url_element["href"])
            )
            if validators.url(absolute_url):
                if (
                    absolute_url
                    and absolute_url.replace("https://", "")
                    .replace("http://", "")
                    .split("/")[0]
                    in allow_domains
                    and absolute_url not in crawled_sites
                ):
                    site_link_data = CrawlRequestUrls
                    site_link_data.link = absolute_url
                    site_link_data.cookies = url.cookies
                    site_link_data.headers = url.headers
                    site_link_data.payload = url.payload
                    orchestrator_function(site_link_data, settings)

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving the URLs in the site: {error.__cause__}",
        )


# parse website content .
def get_page_content(data, settings: CrawlSettings):
    try:
        content = "".join(
            set(
                element.text
                for element in data.select(", ".join(str(s) for s in settings.selectors))
            )
        )
        content = " ".join(re.sub("[\t\n]", "", content).split()).strip()
        return content
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving the URLs in the site: {error.__cause__}",
        )
    

def get_page_media_with_topics(data, topics: list[str]):
    try:
        media_settings = config.ENTITY_SETTINGS.get("media_settings", {})
        target_p_classes = media_settings.get("p_class", [])
        target_img_classes = media_settings.get("img_class", [])

        # Extract relevant text
        relevant_texts = set()
        for p_class in target_p_classes:
            for div in data.find_all("div", class_=p_class):
                for p_tag in div.find_all("p"):
                    paragraph_text = p_tag.get_text(strip=True)
                    if any(topic.lower() in paragraph_text.lower() for topic in topics):
                        relevant_texts.add(paragraph_text)

        relevant_text = " ".join(
            re.sub(r"[\t\n]+", " ", text).strip() for text in relevant_texts
        )

        # Extract and validate image links
        imgs_links = set()
        for img_class in target_img_classes:
            for div in data.find_all("div", class_=img_class):
                for img_tag in div.find_all("img"):
                    src = img_tag.get("src")
                    if src:
                        img_url = urljoin(base_url, src)
                        if validators.url(img_url) and "logo" not in img_url.lower():
                            imgs_links.add(img_url)

        return relevant_text, list(imgs_links)
    
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Error while extracting media content and links: {error.__cause__}",
        )