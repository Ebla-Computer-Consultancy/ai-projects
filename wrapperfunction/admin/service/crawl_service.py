import re
import requests
import validators

from bs4 import BeautifulSoup
from fastapi import HTTPException

from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings

global allow_domains
allow_domains = set()
global crawled_sites
crawled_sites = set()


def crawl_urls(urls: list[str], settings: CrawlSettings):
    for url in urls:
        if validators.url(url.link):
            allow_domains.add(
                url.link.replace("https://", "").replace("http://", "").split("/")[0]
            )
            response = orchestrator_function(url, settings)

            return response
        else:
            raise HTTPException(status_code=400, detail="The URL was invalid.")


def orchestrator_function(
    url: CrawlRequestUrls,
    settings: CrawlSettings,
):
    try:
        data = crawl_site(
            url.link, cookies=url.cookies, headers=url.headers, payload=url.payload
        )
        site_data = {
            "title": get_page_title(url.link, data),
            "content": get_page_content(data, settings),
        }
        crawled_sites.add(url.link)
        if settings.deep:
            site_urls = get_all_urls(data)
            if len(site_urls):
                crawl_urls(site_urls, settings)

        return site_data

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
    response = requests.get(
        url,
        allow_redirects=False,
        verify=False,
        cookies=cookies,
        headers=headers,
        data=payload,
    )
    return BeautifulSoup(response.text, "lxml")


# Extracts the page title.
def get_page_title(link, data):
    try:
        if data and data.title:
            return data.title.string
        else:
            return link.split("/")[-1]
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving the site title: {error.__cause__}",
        )


# Gets all of the URLs from the webpage.
def get_all_urls(data):
    try:
        urls = set()
        url_elements = data.select("a[href]")
        for url_element in url_elements:
            url = url_element["href"]
            if "https://" in url or "http://" in url:
                if (
                    url.replace("https://", "").replace("http://", "").split("/")[0]
                    in allow_domains
                    and url not in crawled_sites
                ):
                    urls.add(url)
        return urls

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
                tag.text
                for tag in data.select(", ".join(str(s) for s in settings.selectors))
            )
        )
        content = " ".join(re.sub("[\t\n]", "", content).split()).strip()
        return content
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving the URLs in the site: {error.__cause__}",
        )
