# !pip install scrapy -q

# IMPORTS ######################################################################
import scrapy
import pandas as pd

NAMING = 'sls_saso_gov3_2'

# SPIDERS ######################################################################
class CategorySpider(scrapy.Spider):
    name = 'category_spider'
    allowed_domains = ['sls.saso.gov.sa']

    start_urls = pd.read_csv('sls_saso_gov3.csv').link.to_list()

    categs = {
        **{str(k):'Air Conditioner' for k in [1, 4]},
        **{str(k):'Lights Product' for k in [1121, 1122]},
        **{str(k):'WaterHeater' for k in range(43, 48)},
        **{str(k):'WashingMachine' for k in range(901, 907)},
        **{str(k):'ClothDryer' for k in [54, 55]},
        **{str(k):'Refrigerator' for k in range(1101, 1111)},
    }

    def parse(self, response):
        prod = {}
        prod['title'] = response.css('div.page-title > h1::text').get('').strip()
        prod['spn_class'] = response.css('#MainContent_spnClassification::text').get('').strip()
        prod['consumption'] = response.css('div.product-thumb__consumption > span::text').get('').strip()
        
        for li in response.css('ul.product-meta__fields li'):
            prod[li.xpath('./div[1]/text()').get('').strip()] = li.xpath('./div[2]/text()').get('').strip()
        
        prod['url'] = response.request.url
        
        prod['Main Category'] = self.categs.get(
            prod['url'].split('?')[-1].split('&')[1].split('=')[-1],
            ''
        )

        yield prod

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
})

process.crawl(CategorySpider)
process.start() # the script will block here until the crawling is finished

# COLAB-RUNNER #################################################################
# !python scraper.py