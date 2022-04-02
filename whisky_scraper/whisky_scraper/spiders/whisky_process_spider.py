
import scrapy
from scrapy.crawler import CrawlerProcess

class WhiskySpider(scrapy.Spider):
    name = 'whisky_process_spider'

    def start_requests(self):
        yield scrapy.Request('https://www.thewhiskyexchange.com/c/40/single-malt-scotch-whisky?pg=1&psize=120')
    
    def parse(self, response):
        products = response.css('li.product-grid__item')
        for item in products:
            yield {
            'name':item.css('p.product-card__name::text').get(),
            'meta':item.css('p.product-card__meta::text').get(),
            'price':item.css('p.product-card__price::text').get(),
            }

        for x in range(2, 20):
            yield (scrapy.Request(
                f'https://www.thewhiskyexchange.com/c/40/single-malt-scotch-whisky?pg={x}&psize=120',
                callback=self.parse
            ))

process = CrawlerProcess(settings={
    "FEEDS": {
        "whisky_process_spider.json": {
            "format": "json"
        },
    },
})

process.crawl(WhiskySpider)
process.start() # the script will block here until the crawling is finished