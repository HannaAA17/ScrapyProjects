import scrapy


class WhiskySpiderSpider(scrapy.Spider):
    name = 'whisky_spider'
    allowed_domains = ['www.whiskyshop.com']
    start_urls = ['https://www.whiskyshop.com/scotch-whisky?item_availability=In+Stock']

    
    def parse(self, response):
        '''
        <a 
            href="https://www.whiskyshop.com/dalmore-12-year-old-sherry-cask" 
            class="product photo product-item-photo" tabindex="-1" 
            data-id="26106" data-name="Dalmore 12 Year Old Sherry Cask Select" 
            data-price="71" data-category="Scotch Whisky" 
            data-list="Scotch Whisky" 
            data-brand="The Dalmore" 
            data-quantity="1" 
            data-dimension10="In stock" 
            data-store="The Whisky Shop" 
            data-position="1" 
            data-event="productClick" 
            data-attributes="[]"
        >
            <span class="product-image-container product-image-container-8286">
                <span class="product-image-wrapper">
                    <img 
                        class="product-image-photo" 
                        src="https://cdn.whiskyshop.com/media/catalog/product/cache/50f391de93cd48dd70ebbdc71e96a683/d/a/dalmore_12yo_sherrycaskselect_ps.jpg" 
                        loading="lazy" 
                        width="400" 
                        height="480" 
                        alt="Dalmore 12 Year Old Sherry Cask Select"
                    >
                </span>
            </span>
        </a>
        '''
        
        keys = [
            'data-id', 'data-name', 'data-category', 'data-brand',
            'data-price', 'data-store', 'href'
        ]
        
        yield from ({
            **{k.lstrip('data-') : prod.attrib[k] for k in keys},
            'image':prod.css('img::attr(src)').extract_first()
        } for prod in response.css('a[data-id]'))

        next_page = response.css('a.action.next::attr(href)').extract_first()

        if next_page:
            yield response.follow(next_page, callback=self.parse) 



