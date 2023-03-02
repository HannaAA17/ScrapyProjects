import json
import scrapy


# SPIDERS ######################################################################
class JobsSpider(scrapy.Spider):
    name = 'JobsSpider'
    allowed_domains = ['europa.eu']
    
        
    def __init__(self, *args, **kwargs):
        
        self.headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Windows"',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        }

        self.json_data = {
            'keywords': [],
            'skillUris': [],
            'sectorCodes': [],
            'locationCodes': [],
            'occupationUris': [],
            'euresFlagCodes': [],
            'resultsPerPage': 50,
            'requiredLanguages': [],
            'otherBenefitsCodes': [],
            'availableLanguages': [],
            'educationLevelCodes': [],
            'publicationPeriod': None,
            'positionOfferingCodes': [],
            'positionScheduleCodes': [],
            'requiredExperienceCodes': [],
            'sortSearch': 'MOST_RECENT',
            'sessionId': 'dpoqpreubkjxm7uq5r2k4m', # dpoqpreubkjxm7uq5r2k4m
        }

        super().__init__(*args, **kwargs)
        
        try:
            self.limit = int(kwargs.get('limit', 200))+1
        except:
            self.limit = 201
    
    
    def start_requests(self):

        yield scrapy.Request(
            'https://ec.europa.eu/eures/eures-apps/searchengine/page/common/security/profile',
            headers=self.headers, callback=self.parse
        )


    def parse(self, response):
        if not self.headers.get('X-XSRF-TOKEN', None):

            cookies = {
                ccits[0]: (None if len(ccits)!=2 else ccits[1])
                for ccs in response.headers.getlist('Set-Cookie')
                for cc in ccs.decode("utf-8").split('; ')
                for ccits in [cc.split('=', 2)]
            }

            self.headers['X-XSRF-TOKEN'] = cookies['XSRF-TOKEN']

        yield scrapy.Request(
            'https://ec.europa.eu/eures/eures-apps/searchengine/page/jv-search/search',
            method="POST", body=json.dumps({'page':1, **self.json_data}),
            headers=self.headers, callback=self.scrape_c
        )


    def scrape_c(self, response):
        js_r = json.loads(response.body)
        
        n_pages = (js_r['numberRecords']//50)+2
        
        for i in range(1, min([self.limit, 201, n_pages])):
            yield scrapy.Request(
                'https://ec.europa.eu/eures/eures-apps/searchengine/page/jv-search/search',
                method="POST", body=json.dumps({'page':i, **self.json_data}),
                headers=self.headers, callback=self.parse_job, dont_filter=True
            )


    def parse_job(self, response):
        '''Get job Details'''
        js_r = json.loads(response.body)
        yield from js_r['jvs']
