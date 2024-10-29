from scrapy import crawler
from scrapy.exceptions import IgnoreRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
import requests
import os

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

# crawle every thing
class CrawlingSpider(CrawlSpider):
    
    name = "eblacrawler"
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.offsite.OffsiteMiddleware': None,
           },
        }

    def __init__(self, *args, **kwargs): 
      super(CrawlingSpider, self).__init__(*args, **kwargs) 

      self.start_urls = kwargs.pop('start_urls')[0].split(',')
      # print("***************************************************")
      # print(self.start_urls)
      sub ="https://"
      self.allowed_domains = [x.replace(sub, '') for x in self.start_urls]
      sub ="www."
      self.allowed_domains = [x.replace(sub, '') for x in self.allowed_domains]
      # print(self.allowed_domains)
      # print("***************************************************")  

    rules = (        
        Rule(LinkExtractor(),callback="parse_item",follow=True),      
    )

    def parse_item(self,response):
        def remove_html_tags(text):
            tag_pattern = re.compile(r'<.*?>')
            cleaned_text = tag_pattern.sub('', text)

            cleaned_text = re.sub(r'[\n\t]', ' ', cleaned_text)
            cleaned_text = ' '.join(cleaned_text.split())
            return cleaned_text
        
        def get_title(url,title):
            title = remove_html_tags(title)
            if title == "":
                title = url.split("/")[-1]
            return title

        # document_links = response.xpath('//a[contains(@href, ".pdf")]/@href').getall()# //a[contains(@href, ".pdf")]/@href | //a[contains(@data-pdf, ".pdf")]/@data-pdf
        # print(f"1-----------------------{type(document_links)}------------------------------{len(document_links)}")
        # document_links.append( response.xpath('//a[contains(@href, ".pdf")]/@href').getall())
        # print(f"2-----------------------{type(document_links)}------------------------------{len(document_links)}")
        # for link in document_links:
        #    self.download_document(response.urljoin(link))
        yield {'url': response.url,
               'title': get_title(url=response.url,title=response.meta['link_text']),
               'body': remove_html_tags('\n'.join(response.xpath("//div[not(descendant::nav) and not(descendant::style) and not(descendant::script) and not(ancestor::header) and not(ancestor::footer)]//text()").extract()))
               }
        for link in response.xpath('*//a/@href').getall():
            yield response.follow(link, self.parse)
    def download_document(self, url):
        response = requests.get(url)
        feed_uri = self.settings.get('FEED_URI').split("/")[-1]
        path = url.split('/')[-1]
        file_path = "./export/docs/"+feed_uri[:-5]
        os.makedirs(file_path, exist_ok=True)
        path = file_path+"/"+path
        self.logger.info('Saving document %s', path)
        with open(path, 'wb') as f:
            f.write(response.content)