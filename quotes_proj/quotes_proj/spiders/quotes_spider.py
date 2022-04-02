
import scrapy

class QuotesSpiderSpider(scrapy.Spider):
    name = 'quotes_spider'
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.xpath('//div[@class="quote"]'):
            yield {
                'text':quote.xpath('.//*[@class="text"]/text()').get().strip(u'\u201c\u201d'), #strip unicode chars u'\u201c\u201d
                'author':quote.xpath('.//*[@class="author"]/text()').get().strip(),
                'about':quote.xpath('.//a[@href]/@href').get().strip(),
                'tags':quote.xpath('.//*[@class="tag"]/text()').getall(),
            }
        
        next_page_url = response.urljoin(response.xpath('.//li[@class="next"]/a/@href').get())
        
        yield scrapy.Request(next_page_url, callback=self.parse)