
import scrapy, json


class ArScraperSpider(scrapy.Spider):
    name = 'ar_scraper'
    allowed_domains = ['smartshopping.sa']
    start_urls = ['http://smartshopping.sa/ar']

    def parse(self, response):
        '''Start requests from the main page'''
        
        # yield from response.follow_all(
        #     css='nav > ul.flexed > li > a',
        #     callback=self.parse_cat,
        # )

        for cat in response.css('.nav-item:nth-child(n+2) > a'):
            yield response.follow(
                cat.attrib['href'],
                meta={'category':cat.css('span::text').get()},
                callback=self.parse_cat,
            )

    def parse_cat(self, response):
        '''Parse Category and Pagination'''
        
        yield from response.follow_all(
            css='a[itemprop="url"]',
            meta=response.meta,
            callback=self.parse_prod,
        )
        
        next_page = response.xpath('//a[i[contains(@class, "lnr-chevron-right")]]/@href').get(None)
        
        if next_page:
            yield response.follow(next_page, meta=response.meta, callback=self.parse_cat)

    def parse_prod(self, response):
        '''Get Products Details'''
        
        id_ = response.css('input[name="product_id"]::attr(value)').get('')
        title = response.css('h1[itemprop="name"]::text').get('').strip()
        
        price = response.css('span[itemprop="price"]::text').get('').strip()
        
        category = response.meta.get('category', '')
        keywords = response.css('meta[name="keywords"]::attr(content)').get('').replace('،', '، ')

        short_desc = response.css('meta[name="description"]::attr(content)').get('')
        full_desc = '\n'.join(response.css('div#product_full_description span[lang="AR-SA"]::text').getall())

        images_links = ['https://smartshopping.sa'+img.rsplit('/', 1)[0] for img in response.css('img[itemprop="image"]::attr(src)').getall()]
        
        yield {
            'id':id_, 'title':title, 'price':price,
            'category': category, 'keywords': keywords,
            'short_desc': short_desc, 'full_desc': full_desc,
            'images_links': images_links,
        }