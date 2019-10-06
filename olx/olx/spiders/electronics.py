from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request

class ElectronicsSpider(CrawlSpider):
    name = "electronics"
    allowed_domains = ["www.olx.com.pk"]
    start_urls = [
        'https://www.olx.com.pk/computers-accessories/',
        'https://www.olx.com.pk/tv-video-audio/',
        'https://www.olx.com.pk/games-entertainment/'
    ]

    rules = (
        Rule(LinkExtractor(allow=(), restrict_css=('.rui-3sH3b rui-23TLR rui-1zK8h',)),
             callback="parse_item",
             follow=True),)

    def parse_item(self, response):
        print('Processing..' + response.url)
        # item_links = response.css('.large > .detailsLink::attr(href)').extract()
        # for a in item_links:
        #     yield Request(a, callback=self.parse_detail_page)