import re
import uuid
from scrapy import Request
from scrapy.exceptions import IgnoreRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request

from wrapperfunction.core import config


class CustomDuplicateFilterMiddleware:
    def __init__(self, crawler):
        self.visited_urls = set()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if request.url in self.visited_urls:
            raise IgnoreRequest(f"Skipping duplicate URL: {request.url}")
        self.visited_urls.add(request.url)
        return None


class CrawlingPagesSpider(CrawlSpider):
    name = "eblapagecrawler"

    def __init__(self, urls=None, *args, **kwargs):
        super(CrawlingPagesSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.pop("start_urls", [])
        # self.start_urls = urls if urls else []
        self.results = []

    def parse(self, response):
        def remove_html_tags(text):
            tag_pattern = re.compile(r"<.*?>")
            cleaned_text = tag_pattern.sub("", text)

            cleaned_text = re.sub(r"[\n\t]", " ", cleaned_text)
            cleaned_text = " ".join(cleaned_text.split())
            return cleaned_text

        def get_title(url, title):
            title = remove_html_tags(title)
            if title == "":
                title = url.split("/")[-1]
            return title

        title = get_title(
            url=response.url, title=response.xpath("//head/title/text()").get()
        )

        yield {
            "url": response.url,
            "title": title,
            "body": title
            + "\n"
            + remove_html_tags(
                "\n".join(
                    response.xpath(
                        "//div[not(descendant::nav) and not(descendant::style) and not(descendant::script) and not(ancestor::header) and not(ancestor::footer)]//text()"
                    ).extract()
                )
            ),
        }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)


# crawl everything
class CrawlingSpider(CrawlSpider):

    name = "eblacrawler"
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.offsite.OffsiteMiddleware": None,
        },
        "FEEDS": {
            f"azure://{config.RERA_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{config.RERA_CONTAINER_NAME}/{config.RERA_SUBFOLDER_NAME}/{uuid.uuid4()}.json": {
                "format": "json"
            }
        },
    }

    def __init__(self, *args, **kwargs):
        super(CrawlingSpider, self).__init__(*args, **kwargs)

        self.start_urls = kwargs.pop("start_urls")[0].split(",")
        sub = "https://"
        self.allowed_domains = [x.replace(sub, "") for x in self.start_urls]
        sub = "www."
        self.allowed_domains = [x.replace(sub, "") for x in self.allowed_domains]

    rules = (Rule(LinkExtractor(), callback="parse_item", follow=True),)

    def _build_request(self, rule_index, link):
        return Request(
            url=link.url,
            callback=self._callback,
            cookies={"LangSwitcher_Setting": "ar-SA"},
            errback=self._errback,
            meta=dict(
                rule=rule_index,
                link_text=link.text,
            ),
        )

    def parse_item(self, response):
        def remove_html_tags(text):
            tag_pattern = re.compile(r"<.*?>")
            cleaned_text = tag_pattern.sub("", text)

            cleaned_text = re.sub(r"[\n\t]", " ", cleaned_text)
            cleaned_text = " ".join(cleaned_text.split())
            return cleaned_text

        def get_title(url, title):
            title = remove_html_tags(title)
            if title == "":
                title = url.split("/")[-1]
            return title

        document_links = response.xpath(
            '//a[contains(@href, ".pdf")]/@href | //a[contains(@data-pdf, ".pdf")]/@data-pdf'
        ).getall()  # '//a[contains(@data-pdf, ".pdf")]/@data-pdf'
        if document_links:
            for link in document_links:
                full_url = response.urljoin(link)
                # full_url = "https://www.km.qa"+link
                # pdf_response = requests.get(full_url)
                yield {
                    "pdf_url": full_url,
                    "title": full_url.split("/")[-1],
                }  # , "body": pdf_response.content}

        url = response.url
        ar_title = get_title(
            url=response.url, title=response.xpath("//head/title/text()").get()
        )
        ar_body = (
            ar_title
            + "\n"
            + remove_html_tags(
                "\n".join(
                    response.xpath(
                        "//div[not(descendant::nav) and not(descendant::style) and not(descendant::script) and not(ancestor::header) and not(ancestor::footer)]//text()"
                    ).extract()
                )
            )
        )
        yield {"url": url, "title": ar_title, "body": ar_body}

        for link in response.xpath("*//a/@href").getall():
            yield response.follow(link, self.parse)


"""
    def download_document(self, url,file_path):
        with open("./pdfs.txt", 'wb') as f:
            f.writelines(url)
        response = requests.get(url)
        path = url.split('/')[-1]
        path = file_path+"/"+path
        self.logger.info('Saving document %s', path)
        with open(path, 'wb') as f:
            f.write(response.content)
    
    def parse_english_version(self, response):
        # Extract data from the English version
        en_url = response.url
        en_title = self.parse_item.get_title(url=response.url,title=response.xpath('//head/title/text()').get())
        en_body= en_title+"\n"+self.parse_item.remove_html_tags('\n'.join(response.xpath("//div[not(descendant::nav) and not(descendant::style) and not(descendant::script) and not(ancestor::header) and not(ancestor::footer)]//text()").extract()))
        
        # Retrieve Arabic data from meta
        ar_url = response.meta['ar_url']
        ar_title = response.meta['ar_title']
        ar_body = response.meta['ar_body']

        yield {
            'ar_url': ar_url,
            'en_url': en_url,
            'ar_title': ar_title,
            'en_title': en_title,
            'ar_body': ar_body,
            'en_body': en_body
        }

    def parse_english_version_se(self, response):
        # Extract data from the English version
        driver = response.meta['driver']
        driver.execute_script(en_url[11:])
        driver.implicitly_wait(2)
        new_response = scrapy.http.HtmlResponse(url=driver.current_url, body=driver.page_source, encoding='utf-8')
        
        
        en_url = new_response.url
        en_title = self.parse_item.get_title(url=new_response.url,title=new_response.xpath('//head/title/text()').get())
        en_body= en_title+"\n"+self.parse_item.remove_html_tags('\n'.join(new_response.xpath("//div[not(descendant::nav) and not(descendant::style) and not(descendant::script) and not(ancestor::header) and not(ancestor::footer)]//text()").extract()))
        
        # Retrieve Arabic data from meta
        ar_url = response.meta['ar_url']
        ar_title = response.meta['ar_title']
        ar_body = response.meta['ar_body']

        yield {
            'ar_url': ar_url,
            'en_url': en_url,
            'ar_title': ar_title,
            'en_title': en_title,
            'ar_body': ar_body,
            'en_body': en_body
        }
        """
