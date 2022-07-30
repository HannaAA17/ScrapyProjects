# !pip install scrapy -q

# IMPORTS ######################################################################
import scrapy
import json

NAMING = 'soulhome'

# SPIDERS ######################################################################
class CategorySpider(scrapy.Spider):
    name = 'category_spider'

    allowed_domains = ['soulhome.app']
    
    def start_requests(self):
        yield scrapy.Request('https://soulhome.app/fetchProducts?limit=5000')
    
    def parse(self, response):
        js = json.loads(response.text)

        response = scrapy.Selector(text=js['html'], type='html')
        
        for prod in response.css('div.productTitle > a::attr(href)').getall():
            yield scrapy.Request(
                prod,
                callback=self.parse_prod,
            )

    def parse_prod(self, response):
        '''Get Products Details'''
        
        button = response.css('button[type="button"][data-id]')

        id_ = button.attrib['data-id']
        sku = button.attrib['data-code']

        title = button.attrib['data-name']
        
        old_price = response.css('span.discount::text').get('').strip()
        price = button.attrib['data-price']
        
        keywords = response.css('meta[name="keywords"]::attr(content)').get('').replace(',', ', ')

        short_desc = response.css('meta[name="description"]::attr(content)').get('')
        
        full_desc = '\n'.join(
            line.strip()
            for line in response.xpath('//div[@class="description-content-wrap"]//text()').getall()
            if line.strip()
        )

        # options = 

        images_links = response.css('a[data-fancybox]::attr(href)').getall()
        
        yield {
            'id':id_, 'sku':sku, 'title':title,
            'old_price':old_price, 'price':price,
            'keywords': keywords,
            'short_desc': short_desc, 'full_desc': full_desc,
            'images_links': images_links,
        }

# PIPELINES ####################################################################
from os.path import basename
from urllib.parse import urlparse

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline

class ImagesDownloader(FilesPipeline):
    
    def get_media_requests(self, item, info):
        '''Capture the download_links from the item'''
        adapter = ItemAdapter(item)
        for file_url in adapter['images_links']:
            yield scrapy.Request(file_url)

    def file_path(self, request, response=None, info=None, *, item=None):
        '''Change the file_name'''
        # Images/img.png
        # return basename(urlparse(request.url).path)
        # 'https://media.mapp.sa/20358/conversions/202205270553_89394-preview.jpg'.split('/', 3)
        return request.url.split('/', 3)[-1].replace('https://media.mapp.sa', '').replace('/conversions/', '_').replace('-preview', '').replace('/', '_')
    
    def item_completed(self, results, item, info):
        '''Edit the item with the downloaded files names'''
        file_paths = [x['path'] for ok, x in results if ok]
        
        if not file_paths:
            raise DropItem("Item contains no files")
        
        adapter = ItemAdapter(item)
        adapter['images_names'] = '\n'.join(file_paths)
        adapter['images_links'] = '\n'.join(adapter['images_links'])

        return item

# CRAWLERPROCESS ###############################################################
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess(settings={
    'BOT_NAME': NAMING,
    
    'ROBOTSTXT_OBEY': True,

    # 'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    # 
    # DEFAULT_REQUEST_HEADERS: {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #     'Accept-Language': 'en',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    # }

    # LOG_ENABLED: False,
    # LOG_FILE: None,
    # LOG_FILE_APPEND: False,
    # LOG_LEVEL: 'DEBUG' # CRITICAL, ERROR, WARNING, INFO, DEBUG

    'FEEDS': {
        f'{NAMING}.csv': {
            'format': 'csv',
            'encoding': 'utf-8-sig',
            'fields': None, # ['field1', 'field2', 'field3']
            'overwrite': True,
        },
    },
    
    'FILES_STORE': 'Images',
    
    'ITEM_PIPELINES': {
        ImagesDownloader: 1,
    },
})



process.crawl(CategorySpider)
process.start() # the script will block here until the crawling is finished

# SNIPPETS #####################################################################
# !rm -r -f Images
# 
# js = json.loads(response.xpath('//script[contains(text(), "var productObj")]/text()').re_first('productObj = ({.+});'))
# yield from response.follow_all(css='.nav-item:nth-child(n+2) > a', callback=self.parse_cat,)

# COLAB-RUNNER #################################################################
# !python scraper.py