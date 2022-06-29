
import scrapy

import json, pandas as pd

class ArScraperSpider(scrapy.Spider):
    name = 'ar_scraper'
    
    DOMAIN = 'makeupstationsa.com'
    allowed_domains = [DOMAIN]

    def start_requests(self):
        for page in range(1, 5): #219
            yield scrapy.Request(
                f'https://makeupstationsa.com/products?page={page}',
                callback=self.parse_page
            )
    
    def parse_page(self, response):
        yield from response.follow_all(
            css='div.product-item > a',
            callback=self.parse_prod
        )
    
    def parse_prod(self, response):
  
        def parse_categories(cats):
            return ' | '.join([cat['name'] for cat in cats])

        def parse_images(images_dict):
            images = []

            for img in images_dict:
                img_url = img['image']['full_size']
                images.append((img_url.split('/')[-1], img_url))
            
            return [img[0] for img in images], [img[1] for img in images]
        
        js = json.loads(response.xpath('//script[contains(text(), "var productObj")]/text()').re_first('productObj = ({.+});'))
        
        id = js['id']
        sku = js['sku']
        name = js['name']
        slug = js['slug']
        
        price = js['price']
        sale_price = js['sale_price'] or ''
        
        try: categories = parse_categories(js['categories'])
        except: categories = ''

        try: keywords = ' | '.join(js['keywords'])
        except: keywords = ''

        images_names, images_links =  parse_images(js['images'])

        short_description = js['short_description']
        
        try: description = js['seo']['description']
        except: description = ''

        description_html = js['description']

        html_url = js['html_url']

        yield dict(
            id=id, sku=sku, name=name, slug=slug,
            short_description=short_description, description=description,
            price=price, sale_price=sale_price,
            categories=categories, keywords=keywords,
            images_links=images_links,
            # description_html=description_html,
            html_url=html_url,
        )