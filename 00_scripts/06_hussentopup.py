# !pip install scrapy -q

# IMPORTS ######################################################################
import scrapy
import json

NAMING = 'hussentopup'

# SPIDERS ######################################################################
class CategorySpider(scrapy.Spider):
    name = 'category_spider'
    allowed_domains = ['hussentopup.com']

    def start_requests(self):
        yield scrapy.Request(
            'https://hussentopup.com/index.php?route=product/catalog&limit=10000',
            callback=self.parse_sub_cat
        )

    def parse(self, response):
        for cat in response.css('ul > .flyout-menu-item > a.collapse-toggle::attr(href)').getall():
            yield response.follow(
                cat+'?limit=20000',
                # callback=self.parse_cat
                callback=self.parse_sub_cat
            )
    
    def parse_cat(self, response):
        yield from response.follow_all(
            css='div.refine-item > a',
            callback=self.parse_sub_cat
        )
    
    def parse_sub_cat(self, response):
        '''Request Categories and Products'''
        
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
                    'model':prod.css('span.stat-2 > span:nth-of-type(2)::text').get('').strip(),
                    'name':prod.css('div.name > a::text').get('').strip(),
                    'price':prod.css('span.price-new, span.price-normal').css('::text').get('').strip(),
                    'price_old':prod.css('span.price-old::text').get('').strip(),
                    'prod_link':prod.css('div.name > a::attr(href)').get(''),
                    'category':category,
                },
                dont_filter=True,
                callback=self.parse_prod,
            )
        
    def parse_prod(self, response):
        '''Get Products Details'''

        images_links = response.css('img[data-largeimg]::attr(data-largeimg)').getall()
        
        description = '\n'.join(
            ' '.join(line.split())
            for line in response.css('head > meta[property="og:description"]::attr(content)').get('').split('\n')
        )

        yield {
            'id': response.meta['id_'],
            'model': response.meta['model'],
            'title': response.meta['name'],
            'price': response.meta['price'],
            'price_old': response.meta['price_old'],
            'category':response.meta['category'],
            'description':description,
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