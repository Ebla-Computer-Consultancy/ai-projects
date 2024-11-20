import json
from scrapy import Request
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from wrapperfunction.admin.service.blob_service import append_blob
from wrapperfunction.core import config
from wrapperfunction.core.utls.helper import (
    get_title,
    process_text_name,
)


class CrawlingSpider(CrawlSpider):
    name = "crawler"
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.offsite.OffsiteMiddleware": None,
        },
        "DOWNLOAD_DELAY": 2,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    }

    def __init__(self, *args, **kwargs):
        super(CrawlingSpider, self).__init__(*args, **kwargs)

        self.start_urls = kwargs.get("start_urls")
        self.cookies = kwargs.get("cookies")
        self.headers = kwargs.get("headers")
        self.allowed_domains = [
            x.replace("https://", "").replace("www.", "").split("/")[0]
            for x in self.start_urls
        ]

    def _build_request(self, rule_index, link):
        return Request(
            url=link.url,
            callback=self._callback,
            cookies=self.cookies,
            headers=self.headers,
            errback=self._errback,
            meta=dict(
                rule=rule_index,
                link_text=link.text,
            ),
        )

    def parse_items(self, response):
        # crawling document link
        document_links = response.xpath(
            '//a[contains(@href, ".pdf")]/@href | //a[contains(@data-pdf, ".pdf")]/@data-pdf'
        ).getall()
        if document_links:
            for link in document_links:
                full_url = response.urljoin(link)
                blob_name = f"item_{process_text_name(full_url)}.json"
                data = {
                    "pdf_url": full_url,
                    "title": full_url.split("/")[-1],
                }
                data = json.dumps(data, ensure_ascii=False)
                append_blob(
                    folder_name=config.SUBFOLDER_NAME,
                    blob_name=blob_name,
                    blob=data,
                    metadata_1=full_url[:-1],
                    metadata_2=full_url,
                    metadata_3="crawled",
                    metadata_4="pdf",
                )

        # crawling page information
        url = response.url
        blob_name = f"item_{process_text_name(url)}.json"
        ar_title = get_title(
            url=response.url,
            title=response.xpath("//head/title/text()").get(),
        )
        ar_body = (
            ar_title
            + " ".join(
                "\n".join(
                    response.xpath(
                        "//body//*[not(self::script) and not(self::style) and not(self::link) and not(self::meta) and not(self::a)]/text()"
                    ).getall()
                ).split()
            ).strip()
        )
        data = {"url": url, "title": ar_title, "body": ar_body}
        data = json.dumps(data, ensure_ascii=False)
        append_blob(
            folder_name=config.SUBFOLDER_NAME,
            blob_name=blob_name,
            blob=data,
            metadata_1=url[:-1],
            metadata_2=url,
            metadata_3="crawled",
            metadata_4="link",
        )


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
