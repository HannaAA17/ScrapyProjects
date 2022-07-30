
import scrapy

class CountriesSpider(scrapy.Spider):
    name = 'countries'
    allowed_domains = ['www.worldometers.info']
    start_urls = ['https://www.worldometers.info/world-population/population-by-country/']
    
    def parse(self, response):
        
        # for country in response.css('#example2 > tbody > tr > td > a'):
        #     yield {
        #         'name':country.css('::text').get(),
        #         'link': response.urljoin(country.css('::attr(href)').get())
        #     }
        
        for country in response.xpath("//td/a"):
            name = country.xpath(".//text()").get()
            link = country.xpath(".//@href").get()

            # absolute_url = f"https://www.worldometers.info{link}"
            # absolute_url = response.urljoin(link)
            # yield scrapy.Request(url=absolute_url)
            
            yield response.follow(url=link, callback=self.parse_country, meta={'country_name': name})
    
    def parse_country(self, response):
        name = response.request.meta['country_name']
        rows = response.xpath("(//table[@class='table table-striped table-bordered table-hover table-condensed table-list'])[1]/tbody/tr")
        for row in rows:
            year = row.xpath(".//td[1]/text()").get()
            population = row.xpath(".//td[2]/strong/text()").get()
            yield {
                'country_name': name,
                'year': year,
                'population': population
            }