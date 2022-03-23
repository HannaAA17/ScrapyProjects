import scrapy


class DronesSpiderSpider(scrapy.Spider):
    name = 'drones_spider'
    allowed_domains = ['jessops.com/drones']
    start_urls = ['http://jessops.com/drones']

    def parse(self, response):

        yield from [{
            'name':product.css('a::text').get(),
            'price':product.css('p.price.larger::text').get().replace(',','')
        } for product in response.css('div.details-pricing')]

