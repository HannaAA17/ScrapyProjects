# !pip install scrapy -q

# IMPORTS ######################################################################
import scrapy
import pickle
from os.path import basename

NAMING = 'gso_org'

df_list = []
# all_images = []

# SPIDERS ######################################################################
class CategorySpider(scrapy.Spider):
    name = 'category_spider'
    allowed_domains = ['gso.org.sa']

    with open('/content/drive/MyDrive/gso_org_links.pkl', 'rb') as f:
        start_urls = ['https://www.gso.org.sa' + link for link in pickle.load(f)]# [:10]


    def parse(self, response):
        '''Get Products Details'''
        
        item = {}
        
        # Product Details
        for h_sel in response.xpath('//h3[text()="Product Details"]/../following-sibling::div//label'):
            item[h_sel.xpath('./text()').get('').strip()] = ' '.join(
                item.strip()
                for item in h_sel.xpath('./following-sibling::div[1]/span//text()').getall()
                if item.strip()
            )
        
        # Product Models
        models = response.xpath('//h3[text()="Product Models"]/../following-sibling::div//td[@data-label="Model Number"]')

        item['Models'] = '\n'.join(model.xpath('./text()').get('').strip() for model in models)

        # for ndx, model_sel in enumerate(models, 1):
        #     item[f'Model_{ndx}'] = model_sel.xpath('./text()').get('').strip()
        #     item[f'Model_{ndx}_Notes'] = model_sel.xpath('./following-sibling::td/text()').get('').strip()
        
        # Product Images
        item['images_links'] = [
            'https://www.gso.org.sa' + link
            for link in response.css('#lightbox .carousel-item > img::attr(src)').getall()
        ]

        # item['images_names'] = [basename(response.request.url)+str(ndx+1)+'.jpeg' for ndx, img in enumerate(item['images_links'])]
        #
        # all_images.extend(zip(item['images_names'], item['images_links']))

        item['images_links'] = '\n'.join(item['images_links'])
        # item['images_names'] = '\n'.join(item['images_names'])        
        
        # Product Link
        item['prod_link'] = response.request.url
        
        df_list.append(item)

        yield item
    
    def closed(self, reason):
        with open('df_list.pkl', 'wb') as f:
            pickle.dump(df_list, f)

        # with open('all_images.pkl', 'wb') as f:
        #     pickle.dump(all_images, f)

# CRAWLERPROCESS ###############################################################
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess(settings={
    'BOT_NAME': NAMING,
    'ROBOTSTXT_OBEY': False,
    'LOG_LEVEL': 'INFO', # CRITICAL, ERROR, WARNING, INFO, DEBUG
    'FEEDS': {
        f'{NAMING}.csv': {
            'format': 'csv',
            'encoding': 'utf-8-sig',
            'fields': None, # ['field1', 'field2', 'field3']
            'overwrite': True,
        },
    },
    # 'FILES_STORE': 'Images',
    # 'ITEM_PIPELINES': {
    #     ImagesDownloader: 1,
    # },
})


process.crawl(CategorySpider)
process.start() # the script will block here until the crawling is finished

# SNIPPETS #####################################################################
# !rm -r -f Images

# COLAB-RUNNER #################################################################
# !python scraper.py