import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ProdsIdsSpider(CrawlSpider):
    name = 'prods_ids'
    allowed_domains = ['bukhamsen.com']
    start_urls = ['http://bukhamsen.com/']

    rules = (
        Rule(
            LinkExtractor(
                allow=r'product-category/',
                deny=['min_price', 'max_price', 'orderby', 'per_page', 'shop_view', 'add-to-cart', '_wpnonce', 'add_to_wishlist'],
            ),
            callback='parse_item',
            follow=True,
        ),
    )

    def parse_item(self, response):
        for item in response.xpath('//*[@data-product_sku and @data-product_id]'):
            yield {
                'id':item.attrib['data-product_id'],
                'sku':item.attrib['data-product_sku'],
            }