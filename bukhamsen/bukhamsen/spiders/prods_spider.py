import scrapy
import pickle, pandas as pd

from bukhamsen.new_id_sku import id_sku

df_list = []
all_images = []
# finished = []

class ProdsSpiderSpider(scrapy.Spider):
    name = 'prods_spider'
    allowed_domains = ['bukhamsen.com']

    def start_requests(self):
        for id_, sku in id_sku:
            yield scrapy.Request(
                'https://bukhamsen.com/?p=' + str(id_),
                callback=self.parse, meta={'id_':id_, 'sku':sku}
            )

    def parse(self, response):

        link = response.css('link[rel="canonical"]::attr(href)').get()

        images = [
            (img.split('?')[0], img.split('?')[0].replace('https://i0.wp.com/bukhamsen.com/wp-content/uploads/', '').replace('/','_').strip(' /'))
            for img in response.css('div.woocommerce-product-gallery__image > a::attr(href)').getall()
        ]

        category = ' > '.join(
            cat.strip()
            for cat in response.css('.woocommerce-breadcrumb a::text').getall()
        )

        name = response.css('h1.product-title::text').get(default='').strip()

        old_price = response.css('p.price > del > span > bdi::text').get(default='').strip()

        new_price = (
            response.css('p.price > ins > span > bdi::text') or 
            response.css('p.price > span > bdi::text')
        ).get(default='').strip()

        short_description = '\n'.join(
            ' '.join(item.replace(':', ' : ').split())
            for item in response.css('div.product-short-description *::text').getall()
            if item.strip()
        )

        brand = response.css('span[itemprop="brand"] > a::text').get(default='').strip()

        description = (
            '\n'.join(
                key.strip() + ' : ' + value.strip()
                for key, value in zip(
                    response.css('#tab-description table > tbody > tr > td:nth-of-type(1)::text').getall(),
                    response.css('#tab-description table > tbody > tr > td:nth-of-type(2)::text').getall(),
                )
                if key.strip() and value.strip()
            ) or '\n'.join(
                ' '.join(item.replace(':', ' : ').split())
                for item in response.css('#tab-description *::text').getall()
                if item.strip()
            )
        )

        df_list.append(dict(
            id = response.meta.get('id_'), sku = response.meta.get('sku'), name = name,

            old_price = old_price, new_price = new_price,

            short_description = short_description, description = description,

            category = category, brand = brand,

            images_names = '\n'.join(img[1] for img in images),

            link = link,
            images_links = '\n'.join(img[0] for img in images),
        ))

        all_images.extend(images)
        # finished.append(response.meta.get('id_'))
    
    def closed(self, reason):
        pd.DataFrame(df_list).to_excel('bukhamsen_prods.xlsx', encoding='utf-8-sig', index=False)
        with open('bukhamsen_images.pkl', 'wb') as f: pickle.dump(all_images, f)