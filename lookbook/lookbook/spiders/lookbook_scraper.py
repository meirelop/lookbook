# -*- coding: utf-8 -*-
import scrapy


class LookbookScraperSpider(scrapy.Spider):
    name = 'lookbook_scraper'
    allowed_domains = ['www.lookbook.nu']
    start_urls = ['http://www.lookbook.nu/united-states']


    def parse(self, response):
        print("Processing..." + response.url)
        # product_name = response.xpath("//div[@class='look_v2']/div[@class='look-meta']/a[@class='title']/text()").extract()
        # title_name = response.xpath('//a[@class="item-title"]/text()').extract()
        # country = response.xpath("//ul[@id='country_collections']/li/a[@href]")
        look_id = response.xpath("//div[@class='look-meta']/a/@href").extract()
        look_img = response.xpath("//div[@class='look_photo']/a/img/@src").extract()
        hypes = response.xpath("//div[@class='hypes-count']/text()").extract()
        just_id = response.xpath("//div[@class='look_v2']/@data-look-id").extract()

        # tags = response.xpath("//div[@class='look_v2']/ul[@class='hashtags']/li/a/text()").extract()
        tags = []

        aas = "//div[@data-look-id='%s']/ul/li" % just_id

        for li in response.xpath(aas):
            # li.xpath('//li/text()').extract()
            tags.append(li.xpath("/a/text()").extract())

        row_data = zip(look_id, look_img, hypes, tags)

        for item in row_data:
            scraped_info = {
                'page': response.url,
                'look_id': item[0],
                'look_img': item[1],
                'hypes': item[2],
                'tags': item[3]
            }

            yield scraped_info


    # def parse(self, response):
    #     for look in response.xpath('//li[starts-with(@id,"look_")]'):
    #         yield self.parse_look(look)