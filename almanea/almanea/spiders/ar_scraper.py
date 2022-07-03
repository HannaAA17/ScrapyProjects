
import scrapy, json


class ArScraperSpider(scrapy.Spider):
    name = 'ar_scraper'
    allowed_domains = ['almanea.sa']
    start_urls = ['http://almanea.sa/ar']

    def parse(self, response):
        '''Start requests from the main page'''
        
        yield from response.follow_all(
            css='nav > ul.flexed > li > a',
            callback=self.parse_cat,
        )


    def parse_cat(self, response):
        '''Parse Category and Pagination'''
        
        yield from response.follow_all(
            css='div.product-slider > a.product-title',
            callback=self.parse_prod,
        )
        
        next_page = response.css('li.PagedList-skipToNext > a::attr(href)').get()
        
        if next_page:
            yield response.follow(next_page, callback=self.parse_cat)

    def parse_prod(self, response):
        '''Get Products Details'''
        
        try: category = ' > '.join(cat.strip() for cat in response.css('.breadcrumb li a::text').getall()[1:])
        except: category = ''

        images_links = response.css('div.product-gallery ul > li > a > img::attr(data-large)').getall()

        details_sel = response.css('div.product-detail')

        try: sub_det1 = {k:v for det in details_sel.css('small::text').get('').split(' / ') for k, v in [' '.join(det.split()).split(' : ')]}
        except: sub_det1 = {}

        title = details_sel.css('h1.title::text').get('').strip()

        price = details_sel.css('h1.price > b::text').get('').strip()
        price_old = details_sel.css('h1.price.old > b::text').get('').strip()

        details_dict = response.css('script[data-flix-brand]').attrib

        mpn = details_dict.get('data-flix-mpn', '')

        brand = details_dict.get('data-flix-brand', '')

        try: sub_det2 = {str(k):str(v) for sel in response.xpath('//tbody/tr[count(td) = 2]') for k,v in [sel.css('td::text').getall()]}
        except: sub_det2 = {}

        yield {
            'title':title, 'mpn':mpn, 'price':price, 'price_old':price_old, 
            'brand':brand, 'category':category, 'images_links':images_links,
            **sub_det1, **sub_det2
        }