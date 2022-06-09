import scrapy, pickle, os, csv

import logging
from scrapy.utils.log import configure_logging 

class Ma3rofCsvSpiderSpider(scrapy.Spider):
    name = 'ma3rof_csv_spider'
    allowed_domains = ['maroof.sa']
    
    configure_logging(install_root_handler=False)
    
    logging.basicConfig(
        filename='log2.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def start_requests(self):
        
        # counter
        self.count = 0
        
        # load scraped
        if os.path.exists(self.pkl_in):
            with open(self.pkl_in, 'rb') as f:
                self.scraped_ids = pickle.load(f)
        else:
            self.scraped_ids = []
        
        with open(self.csv_in, 'r', encoding='utf-8-sig') as f:
            for business in csv.DictReader(f):
                # check if scraped
                if business['Id'] in self.scraped_ids:
                    continue
                # check if reached limit
                elif self.count >= int(self.MAX_COUNT):
                    break
                
                # scrape
                yield scrapy.Request(
                    # url
                    'https://maroof.sa' + business['Url'],
                    # json data
                    meta={'business_data':business},
                    # parse_func
                    callback=self.parse
                )

    def parse(self, response):
        '''
        business_data = {   
            "Id": 7855,
            "NameAr": "مندي ستيشن",
            "Name": "MANDY STATION",
            "DescriptionArSummary": "ألذ خروف لباني مندي ممكن تذوقه في الرياض ... متخصصون بطبخ المندي وبخيارات عدة... بأيدي سعودية طموحه ...",
            "TypeName": "مطبخ و مخبوزات",
            "MainImageUrl": "https://maroof.sa//app/businesses/Tmp/attachment_1988.jpg",
            "CRNumber": "1010506944",
            "ActiveStatus": 0,
            "StampImage": "/Content/Stamps/gold-logo.png",
            "Rating": "9.6",
            "RatingNum": "441",
            "Url": "/7855"
        }
        "//p[contains(text(),'البريد الإلكتروني ')]/following-sibling::p//text()"
        '''

        business_data = response.meta.get('business_data')
        
        # phone = response.xpath('//div[@class="social-row"]//a[contains(@href, "tel:")]/text()').extract_first().strip()
        # whats = response.xpath('//div[@class="social-row"]//a[contains(@href,"wa.me")]/@href').extract_first()

        email = response.xpath('//div[@class="social-row"]//a[contains(@href, "mailto:")]/text()').extract_first().strip()
        website = response.xpath('//div[@class="social-row"]//a[@id="websiteURLAnchor"]/@href').extract_first()
        instagram = response.xpath('//div[@class="social-row"]//a[contains(@href,"instagram.com")]/@href').extract_first()
        twitter = response.xpath('//div[@class="social-row"]//a[contains(@href,"twitter.com")]/@href').extract_first()
        
        # اسم المتجر، نوع النشاط، رقم معروف، الايميل، الموقع الالكتروني، الانستجرام، تويتر
        yield {
            'Id': business_data['Id'],
            'NameAr': business_data['NameAr'],
            'Name': business_data['Name'],
            # 'DescriptionArSummary': business_data['DescriptionArSummary'],
            'TypeName': business_data['TypeName'],
            # 'MainImageUrl': business_data['MainImageUrl'],
            # 'CRNumber': business_data['CRNumber'],
            # 'ActiveStatus': business_data['ActiveStatus'],
            # 'StampImage': business_data['StampImage'],
            # 'Rating': business_data['Rating'],
            # 'RatingNum': business_data['RatingNum'],
            # 'Url': business_data['Url'],
            # 'Phone':phone,
            # 'whatsapp':whats,
            'Email':  email,
            'Website': website,
            'Instgram': instagram,
            'Twiter': twitter,
        }

        self.scraped_ids.append(business_data['Id'])
        self.count += 1
    
    def closed(self, reason):
        with open(self.pkl_in, 'wb') as f:
            pickle.dump(self.scraped_ids, f)