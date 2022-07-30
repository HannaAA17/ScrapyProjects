# !pip install scrapy -q

# IMPORTS ######################################################################
import scrapy
import json

NAMING = 'alkhunaizan'

# SPIDERS ######################################################################
class CategorySpider(scrapy.Spider):
    name = 'category_spider'

    allowed_domains = ['alkhunaizan.sa']
    
    def start_requests(self):
        yield scrapy.Request('https://alkhunaizan.sa/')
    
    def parse(self, response):
        for cat in response.css('a.item-title::attr(href)').getall():
            yield scrapy.Request(
                cat + '?p=1&product_list_limit=30',
                callback=self.parse_cat,
            )

    def parse_cat(self, response):
        for prod in response.css('a.product-item-link::attr(href)').getall():
            yield scrapy.Request(
                prod,
                callback=self.parse_prod,
            )
        
        next_page = response.css('a[title="Next"]::attr(href)').get()
        
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse_cat)

    def parse_prod(self, response):
        '''Get Products Details'''

        images_links = [
            img['full'] 
            for img in json.loads(
                response.css('div.product.media > script:nth-of-type(1)::text').get()
            )['[data-gallery-role=gallery-placeholder]']['mage/gallery/gallery']['data']
        ]

        categories = ' > '.join(
            cat 
            for cat in response.css(
                'div.breadcrumbs li.item:not(:first-child):not(:last-child) > a::attr(title)'
            ).getall()
        )

        title = response.css('span[itemprop="name"]::text').get('').strip()
        sku = response.css('div[itemprop="sku"]::text').get('').strip()
        model = response.css('div[itemprop="model"]::text').get('').strip()

        price_box = response.css('div[data-role="priceBox"]')
        id_ = price_box.attrib['data-product-id']
        price = price_box.css('span[data-price-type="finalPrice"]::attr(data-price-amount)').get()
        price_old = price_box.css('span[data-price-type="finalPrice"]::attr(oldPrice)').get('')

        short_description = response.css(
            'meta[property="og:description"]::attr(content)'
        ).get('').replace('&nbsp;', '').strip()

        description = '\n'.join(
            f'{td.attrib["data-th"].strip()}: {td.css("::text").get()}'
            for td in response.css('table#product-attribute-specs-table > tbody > tr > td')
        )

        yield {
            'id':id_, 'sku':sku, 'model':model,
            'title':title, 'categories':categories,
            'price_old':price_old, 'price':price,
            'short_description':short_description, 'description': description,
            'images_links': images_links,
        }

# PIPELINES ####################################################################
from os.path import basename
from urllib.parse import urlparse

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline

class ImagesDownloader(FilesPipeline):
    
    @staticmethod
    def rename(adapter, file_url, ndx):
        return f"{adapter['id']}_{adapter['sku']}_{ndx}.{file_url.split('?')[0].split('.')[-1]}"

    def get_media_requests(self, item, info):
        '''Capture the download_links from the item'''
        adapter = ItemAdapter(item)
        for ndx, file_url in enumerate(adapter['images_links'], 1):
            yield scrapy.Request(
                file_url,
                meta={'image_name':self.rename(adapter, file_url, ndx)}
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        '''Change the file_name'''
        # Images/img.png
        # return basename(urlparse(request.url).path)
        # 'https://media.mapp.sa/20358/conversions/202205270553_89394-preview.jpg'.split('/', 3)
        # request.url.split('/', 3)[-1].replace('https://media.mapp.sa', '').replace('/conversions/', '_').replace('-preview', '').replace('/', '_')
        return request.meta.get('image_name')
    
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