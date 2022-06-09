import scrapy

import logging
from scrapy.utils.log import configure_logging 

# MAX_COUNT = 200
# BASE_URL = 'https://maroof.sa/'

id_cat = dict([
	(14, 'تسويق إلكتروني'), (16, 'تصوير'), (23, 'مطبخ و مخبوزات'), (24, 'حلول إلكترونية'),
	(25, 'خدمات أكاديمية'), (26, 'مستلزمات المرأة'), (34, 'تصميم وطباعة'), (35, 'تخطيط مناسبات وحفلات'),
	(39, 'كوافيرة و تجميل'), (41, 'إلكترونيات واكسسورات'), (45, 'أخرى'), (47, 'السيارات'),
	(48, 'العقارات'), (49, 'أثاث وديكور'), (51, 'الحرف والصناعات اليدوية'),
])

def make_url(cat_id, page=0):
    return (
        'https://maroof.sa/BusinessType/MoreBusinessList'
        f'?businessTypeId={cat_id}&pageNumber={page}'
        '&sortProperty=BestRating&desc=true'
    )

class Ma3rofSpiderSpider(scrapy.Spider):
    name = 'ma3rof_spider'
    allowed_domains = ['maroof.sa']
    
    configure_logging(install_root_handler=False)
    
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def start_requests(self):
        for cat_id in id_cat:
            yield scrapy.Request(
                make_url(cat_id),
                meta={'cat_id':cat_id},
                callback=self.parse
            )

    def parse(self, response):
        cat_id = response.meta.get('cat_id')
        
        if response.text != '':
            data = response.json()

            for business in data['Businesses']:
                # yield scrapy.Request(
                    # f"{BASE_URL}{business['Id']}",
                yield response.follow(
                    business['Url'],
                    meta={'business_data':business,},
                    callback=self.parse_item
                )

            current_count = data['PageNumber'] * data['Size']
            total_count = data['Count']

            # if min(current_count, total_count, MAX_COUNT) == current_count:
            if min(current_count, total_count, int(self.MAX_COUNT)) == current_count:
                yield scrapy.Request(
                    make_url(cat_id, data['PageNumber']+1),
                    meta={'cat_id':cat_id},
                    callback=self.parse
                )

    def parse_item(self, response):
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
    
    def close(spider, reason):
        ...