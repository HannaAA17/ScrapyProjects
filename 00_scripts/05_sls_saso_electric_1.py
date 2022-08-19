# !pip install scrapy -q

# IMPORTS ######################################################################
import scrapy
import pickle

NAMING = 'sls_saso_gov3'

# SPIDERS ######################################################################
class CategorySpider(scrapy.Spider):
    name = 'category_spider'
    allowed_domains = ['sls.saso.gov.sa']
    start_urls = ['https://sls.saso.gov.sa/Pages/ExploreElectric']

    save_req = []

    def parse(self, response):
        page = response.css('div.btn-group > .page_disabled::text').get('').strip()
        print('Page:', page)

        # page n - parse
        for prod in response.css('#product-list > div > a'):
            yield {
                'page':page, 
                'link':'https://sls.saso.gov.sa' + prod.attrib['href'].replace('.aspx', ''),
            }
        
        # check type
        if response.meta.get('action', '') == 'parse':
            return
        
        # get next pages
        pages = (
            response
            .css('div.btn-group > .page_disabled')
            .xpath('./following-sibling::*[text() != ">>" and text() != "Last"]/@id')
            .re('.*_(\d+)$')
        )

        # page n+1
        if len(pages) > 0:
            
            req = scrapy.FormRequest.from_response(
                response,
                formid = 'ctl01',
                formdata = {
                    '__EVENTTARGET':f'ctl00$MainContent$rptDevicesPager$ctl0{pages[0]}$lnkPage',
                    '__EVENTARGUMENT':'',
                },
                meta={
                    'action':'parse',
                },
                callback=self.parse,
            )
            self.save_req.append((pages[0], req))
            yield req

        # page n+2
        if len(pages) > 1:
            
            req = scrapy.FormRequest.from_response(
                response,
                formid = 'ctl01',
                formdata = {
                    '__EVENTTARGET':f'ctl00$MainContent$rptDevicesPager$ctl0{pages[1]}$lnkPage',
                    '__EVENTARGUMENT':'',
                },
                meta={
                    'action':'repeat'
                },
                callback=self.parse,
            )
            self.save_req.append((pages[1], req))
            yield req
    
    def closed(self, reason):
        with open('save_req.pkl', 'wb') as f:
            pickle.dump(self.save_req, f)

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