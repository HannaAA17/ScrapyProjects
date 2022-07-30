import scrapy
from scrapy_playwright.page import PageMethod

class PwspiderSpider(scrapy.Spider):
    name = 'pwspider'

    def start_requests(self):
        yield scrapy.Request(
            'https://shoppable-campaign-demo.netlify.app/#/',
            meta = dict(
                playwright = True,
                playwright_include_page = True,
                playwright_page_methods = [
                    PageMethod('wait_for_selector', 'div#productListing'),
                    PageMethod('wait_for_timeout', 5000),
                    PageMethod("screenshot", path="example.png", full_page=True),
                    # https://playwright.dev/python/docs/api/class-page
                ],
            )
        )

    def parse(self, response):
        for prod in response.css('div.card > div.row'):
            yield dict(
                image = prod.css('img[alt="Card image cap"]::attr(src)').get(),
                name = prod.css('h3.card-title::text').get(),
                description = prod.css('div.card-text > p::text').get(),
                price = prod.css('div.form-group > label::text').get(),
                size = ','.join(prod.css('select.form-control.option-select > option[value="[object Object]"]::text').getall()),
            )
