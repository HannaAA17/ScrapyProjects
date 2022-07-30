# !pip install scrapy -q

# IMPORTS ######################################################################
import scrapy
import json

NAMING = 'homyonline'

# SPIDERS ######################################################################
class CategorySpider(scrapy.Spider):
    name = 'category_spider'

    allowed_domains = ['homyonline.com']
    
    def start_requests(self):
        for cat in ['392', '410', '414', '419', '698']:
            yield scrapy.Request(
                f'https://www.homyonline.com/index.php?route=product/category&path={cat}&limit=10000'
            )
    
    def parse(self, response):
        '''Request Categories and Products'''

        # make new category requests
        yield from response.follow_all(
            css='div.refine-item > a',
            callback=self.parse
        )

        # get category breadcrumbs
        category = ' > '.join(
            cat.strip()
            for cat in response.css('ul.breadcrumb > li:not(:first-child) > a::text').getall()
        )

        # make products requsts
        for prod in response.css('div.product-thumb > div.caption'):
            yield response.follow(
                prod.css('div.name > a::attr(href)').get(),
                meta={
                    'id_':prod.css('a[data-product_id]::attr(data-product_id)').get('').strip(),
                    'name':prod.css('div.name > a::text').get('').strip(),
                    'price':prod.css('span.price-new, span.price-normal').css('::text').get('').strip(),
                    'price_old':prod.css('span.price-old::text').get('').strip(),
                    'prod_link':prod.css('div.name > a::attr(href)').get(''),
                    'category':category,
                },
                callback=self.parse_prod,
            )
        
    def parse_prod(self, response):
        '''Get Products Details'''

        images_links = response.css('img[data-largeimg]::attr(data-largeimg)').getall()
        
        brand = response.css('li.product-manufacturer > a::text').get('')
        model = response.css('li.product-model > span::text').get('')
        weight = response.css('li.product-weight > span::text').get('')
        dimension = response.css('li.product-dimension > span::text').get('')

        description = '\n'.join(
            ' '.join(line.split())
            for line in response.css('head > meta[property="og:description"]::attr(content)').get('').split('\n')
        )

        yield {
            'id': response.meta['id_'],
            'title': response.meta['name'],
            'price': response.meta['price'],
            'price_old': response.meta['price_old'],
            'category':response.meta['category'],
            'description':description,
            'brand': brand,
            'model': model,
            'weight': weight,
            'dimension': dimension,
            'images_links':images_links,
            'prod_link': response.meta['prod_link'],
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
        return basename(urlparse(request.url).path)
        # 'https://media.mapp.sa/20358/conversions/202205270553_89394-preview.jpg'.split('/', 3)
        # request.url.split('/', 3)[-1].replace('https://media.mapp.sa', '').replace('/conversions/', '_').replace('-preview', '').replace('/', '_')
        # return request.meta.get('image_name')
    
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
    
    'ROBOTSTXT_OBEY': False,
    # 'COOKIES_ENABLED': True,

    # 'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    # 
    # 'DEFAULT_REQUEST_HEADERS': {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #     'Accept-Language': 'en',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    # }

    # 'LOG_ENABLED': False,
    # 'LOG_FILE': None,
    # 'LOG_FILE_APPEND': False,
    'LOG_LEVEL': 'INFO', # CRITICAL, ERROR, WARNING, INFO, DEBUG

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