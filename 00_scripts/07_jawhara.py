# !pip install scrapy -q

# IMPORTS ######################################################################
import scrapy
import json

NAMING = 'jawhara'

# SPIDERS ######################################################################
class CategorySpider(scrapy.Spider):
    name = 'category_spider'
    allowed_domains = ['jawhara.online']

    start_urls = [
        'https://jawhara.online/ar/electronics/televisions.html?product_list_limit=10000',
        'https://jawhara.online/ar/electronics/audio-video.html?product_list_limit=10000',
        'https://jawhara.online/ar/electronics/watches.html?product_list_limit=10000',
        'https://jawhara.online/ar/home/home-appliances.html?product_list_limit=10000',
        'https://jawhara.online/ar/home/kitchen-appliances.html?product_list_limit=10000',
        'https://jawhara.online/ar/home/furniture-and-decoration.html?product_list_limit=10000',
        'https://jawhara.online/ar/home/kitchen-dining.html?product_list_limit=10000',
        'https://jawhara.online/ar/home/cooling-heating-devices.html?product_list_limit=10000',
        'https://jawhara.online/ar/home/travel-accessories.html?product_list_limit=10000',
        'https://jawhara.online/ar/beauty/personal-care.html?product_list_limit=10000',
        'https://jawhara.online/ar/beauty/hair-removal-devices.html?product_list_limit=10000',
        'https://jawhara.online/ar/beauty/hair-electronics.html?product_list_limit=10000',
        'https://jawhara.online/ar/baby-toys/children-s-activities.html?product_list_limit=10000',
        'https://jawhara.online/ar/baby-toys/training-video.html?product_list_limit=10000',
        'https://jawhara.online/ar/baby-toys/toys-games.html?product_list_limit=10000',
    ]


    def parse(self, response):
        category = ' > '.join(
            cat.strip()
            for cat in response.css('.breadcrumbs li + li').xpath('.//text()').getall()
            if cat.strip()
        )

        yield from response.follow_all(
            css='.product-item-photo > a',
            meta={'category':category},
            dont_filter=True,
            callback=self.parse_prod,
        )

        
    def parse_prod(self, response):
        '''Get Products Details'''

        item = {}

        price_box = response.css('.product-info-price div[data-role="priceBox"]')

        item['id'] = price_box.attrib['data-product-id']
        item['sku'] = response.css('form[data-product-sku]::attr(data-product-sku)').get('')
        item['title'] = response.css('h1.page-title > span::text').get('').strip()

        item['price'] = price_box.css('span[data-price-type="finalPrice"]::attr(data-price-amount)').get()
        item['price_old'] = price_box.css('span[data-price-type="oldPrice"]::attr(data-price-amount)').get('')

        item['category'] = response.meta.get('category')

        item['description'] = '\n'.join(
            ' '.join(line.split())
            for line in response.css('.product.attribute.description').xpath('.//text()').getall()
            if line.strip()
        )

        item['images_links'] = response.css('meta[property="og:image"]::attr(content)').getall()

        try:
            js = json.loads(
                response.xpath('//div[@class="product media"]/script[contains(text(), "mage/gallery/gallery")]/text()')
                .get('')
            )['[data-gallery-role=gallery-placeholder]']['mage/gallery/gallery']['data']
            
            item['images_links'].extend([img['img'] for img in js])
        except:
            ...

        item['prod_link'] = response.request.url
    
        yield item

# PIPELINES ####################################################################
from os.path import basename
from urllib.parse import urlparse

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline

class ImagesDownloader(FilesPipeline):

    @staticmethod
    def rename(id_, ndx, file_url):
        return f"{id_}_{ndx}.{basename(file_url.split('?')[0])}"

    def get_media_requests(self, item, info):
        '''Capture the download_links from the item'''
        adapter = ItemAdapter(item)
        for ndx, file_url in enumerate(adapter['images_links'], 1):
            yield scrapy.Request(
                file_url,
                meta={'image_name':self.rename(adapter['id'], ndx, file_url)}
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        '''Change the file_name'''
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
    # 'LOG_LEVEL': 'INFO', # CRITICAL, ERROR, WARNING, INFO, DEBUG
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

# COLAB-RUNNER #################################################################
# !python scraper.py