
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class BestMoviesSpider(CrawlSpider):
    name = 'best_movies'
    allowed_domains = ['imdb.com']
    start_urls = ['https://www.imdb.com/search/title/?groups=top_250&sort=user_rating']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=('//h3[@class="lister-item-header"]/a')), callback='parse_item', follow=True),
        Rule(LinkExtractor(restrict_xpaths="(//a[@class='lister-page-next next-page'])[2]")),
        # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
        # Rule(LinkExtractor(deny=r'Items/'), callback='parse_item', follow=True),
        # Rule(LinkExtractor(restrict_css=('a.active')), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        item['name'] = response.xpath('//h1[@data-testid="hero-title-block__title"]/text()').get()
        item['IMDb RATING'] = response.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/span/text()').get()
        item['POPULARITY'] = response.xpath('//div[@data-testid="hero-rating-bar__popularity__score"]/text()').get()
        return item