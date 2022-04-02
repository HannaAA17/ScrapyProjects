import scrapy


class WhiskySpiderSpider(scrapy.Spider):
    name = 'whisky_spider'
    allowed_domains = ['www.whiskyshop.com']
    start_urls = ['https://www.whiskyshop.com/scotch-whisky?item_availability=In+Stock']

    
    def parse(self, response):
        
        keys = [
            'data-id', 'data-name', 'data-category', 'data-brand',
            'data-price', 'data-store', 'href'
        ]
        
        yield from ({
            **{k.lstrip('data-'):prod.attrib[k] for k in keys},
            'image':prod.css('img::attr(src)').extract_first()
        } for prod in response.css('a[data-id]'))

        next_page = response.css('a.action.next::attr(href)').extract_first()

        if next_page:
            yield response.follow(next_page, callback=self.parse) 



