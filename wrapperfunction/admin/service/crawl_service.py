from io import BytesIO
import json
import re
from urllib.parse import urljoin
import requests

from bs4 import BeautifulSoup
from fastapi import HTTPException, UploadFile
import validators
import execjs


from wrapperfunction.document_intelligence.service.document_intelligence_service import inline_read_scanned_pdf
from wrapperfunction.core import config
from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings, IndexingType
from wrapperfunction.admin.service.blob_service import append_blob, upload_files_to_blob
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
        en_data, data, response = crawl_site(
            url.link, main_lang= url.settings, cookies=url.cookies, headers=url.headers, payload=url.payload
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
                upload_files_to_blob(files=[UploadFile(file=BytesIO(response.content), filename=get_page_title(url.link), headers=response.headers)], container_name=settings.containerName, subfolder_name=config.SUBFOLDER_NAME+'_pdf')
                settings.deep = False
            else:
                if en_data is None:
                    site_data = {
                    "url": url.link,
                    "title": get_page_title(url.link, data),
                    "content": get_page_content(data, settings)
                }
                else:
                    site_data = {
                    "url": url.link,
                    "title": get_page_title(url.link, data),
                    "en_title": get_page_title(url.link, en_data),
                    "content": get_page_content(data, settings),
                    "en_content": get_page_content(en_data, settings),
                }
                

        json_data = json.dumps(site_data, ensure_ascii=False)
        blob_name = f"item_{process_text_name(url.link)}.json"
        append_blob(
            folder_name=config.SUBFOLDER_NAME,
            blob_name=blob_name,
            blob=json_data,
            container_name=settings.containerName,
            metadata_1=url.link,
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
            detail=f"Error while making a request to the site: {str(error)}",
        )


def crawl_site(
    url: str,
    main_lang:str,
    headers: dict,
    payload: dict,
    cookies: dict = {},
):
    cookies["user-agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    response = requestUrl(url, headers, payload, cookies)
    other_response = detect_languge_by_header(url, headers, payload, cookies, main_lang)
    if response.headers.get('Content-Type') == 'application/pdf':
        return inline_read_scanned_pdf(None, response.content), response
    else:
        return BeautifulSoup(other_response.text, "lxml"), BeautifulSoup(response.text, "lxml"), response

def detect_languge_by_header(
        url: str,
        headers: str,
        payload: str,
        cookies: dict,
        main_lang: str= "en"):
    
    if main_lang == "en":
        translateTo ='العربية'
    else:
        translateTo ='English'
    
    response = requestUrl(url, headers, payload, cookies)
    soup = BeautifulSoup(response.text, 'lxml')
    # Find the button tag containing the text "English"
    button_tag = soup.find('a', text= translateTo)

    # Extract the function name from the onclick attribute
    try:
        onclick_function = button_tag['onclick'].strip('()')
    except:
        onclick_function=None
    if onclick_function is None:
        other_url = button_tag['href']
        if validators.url(other_url):
            new_response = requestUrl(other_url, headers, payload, cookies)
            return new_response
    else:
        # Extract the JavaScript code
        script_tag = soup.find('script')
        js_code = script_tag.string
        if js_code is None:
            try:
                other_url = url.split('/')
                extracted_string = re.search(r"\('([^']*)'\)", onclick_function).group(1)
                if len(other_url)==3:
                    other_url.append(extracted_string)
                else:    
                    other_url.insert(3,extracted_string)
                other_url = "/".join(other_url)
                if validators.url(other_url):
                    new_response = requestUrl(other_url, headers, payload, cookies)
                else:
                    new_response = requestUrl(url, headers, payload, cookies)
            except:
                new_response = None
        else:
            # Create a JavaScript runtime environment
            ctx = execjs.compile(js_code)
            # Run the extracted function
            new_response = ctx.call(onclick_function)
        return new_response

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
        content = " ".join(
            set(
                element.text
                for element in data.select(", ".join(str(s) for s in settings.selectors))
            )
        )
        content = " ".join(re.sub("[\t\n]", " ", content).split()).strip()
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