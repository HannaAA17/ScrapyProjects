import scrapy, pickle, os, csv, json

import logging
from scrapy.utils.log import configure_logging 

class Ma3rofCsvSpiderSpider(scrapy.Spider):
    name = 'ma3rof_csv_spider'
    allowed_domains = ['maroof.sa']
    
    # with open('log2.txt', 'w') as f:
    #     ...
    #
    # configure_logging(install_root_handler=False)
    #
    # logging.basicConfig(
    #     filename='log2.txt',
    #     format='%(levelname)s: %(message)s',
    #     level=logging.INFO
    # )

    def start_requests(self):
        
        # # load scraped
        # if os.path.exists(self.json_in):
        #     with open(self.json_in, 'r', encoding='utf-8-sig') as f:
        #         self.scraped_ids = {business['Id'] for business in json.load(f)}
        # else:
        #     self.scraped_ids = set()

        with open(self.csv_in, 'r', encoding='utf-8-sig') as f:

            # counter
            count = 0

            for business in csv.DictReader(f):
                # # check if scraped
                # if business['Id'] in self.scraped_ids:
                #     continue
                
                # check if scraped
                if count < int(self.MIN_COUNT):
                    count+=1
                    continue
                
                # check if max
                elif count > int(self.MAX_COUNT):
                    break
                
                try: 
                    url='https://maroof.sa' + business['Url']
                except: 
                    continue
                
                # scrape
                yield scrapy.Request(
                    # url
                    url,
                    # json data
                    meta={'business_data':business},
                    # parse_func
                    callback=self.parse2
                )
                count+=1


    def parse2(self, response):
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
        
        try: phone = response.xpath('//div[@class="social-row"]//a[contains(@href, "tel:")]/text()').extract_first().strip()
        except: phone = ''

        try: whats = response.xpath('//div[@class="social-row"]//a[contains(@href,"wa.me")]/@href').extract_first()
        except: whats = ''

        try: email = response.xpath('//div[@class="social-row"]//a[contains(@href, "mailto:")]/text()').extract_first().strip()
        except: email = ''

        try: website = response.xpath('//div[@class="social-row"]//a[@id="websiteURLAnchor"]/@href').extract_first()
        except: website = ''

        try: instagram = response.xpath('//div[@class="social-row"]//a[contains(@href,"instagram.com")]/@href').extract_first()
        except: instagram = ''

        try: twitter = response.xpath('//div[@class="social-row"]//a[contains(@href,"twitter.com")]/@href').extract_first()
        except: twitter = ''

        
        # اسم المتجر، نوع النشاط، رقم معروف، الايميل، الموقع الالكتروني، الانستجرام، تويتر
        yield {
            'Id': business_data['Id'],
            'NameAr': business_data['NameAr'],
            'Name': business_data['Name'],
            'DescriptionArSummary': business_data['DescriptionArSummary'],
            'TypeName': business_data['TypeName'],
            'MainImageUrl': business_data['MainImageUrl'],
            'CRNumber': business_data['CRNumber'],
            'ActiveStatus': business_data['ActiveStatus'],
            'StampImage': business_data['StampImage'],
            'Rating': business_data['Rating'],
            'RatingNum': business_data['RatingNum'],
            'Url': business_data['Url'],
            'Phone': phone,
            'whatsapp': whats,
            'Email':  email,
            'Website': website,
            'Instgram': instagram,
            'Twiter': twitter,
        }

        # self.count += 1
    
    # def closed(self, reason):
    #     scraped = []
    #
    #     if os.path.exists(self.json_in):
    #         with open(self.json_in, 'r', encoding='utf-8-sig') as f1:
    #             scraped.extend(json.load(f1))
    #
    #     with open(self.json_out, 'r', encoding='utf-8-sig') as f2:
    #         scraped.extend(json.load(f2))
    #
    #     with open(self.json_in, 'w', encoding='utf-8-sig') as f1:
    #         json.dump(scraped, f1, indent=2, ensure_ascii=False)
    #
    #     with open(self.json_out, 'w', encoding='utf-8-sig') as f2:
    #         ...