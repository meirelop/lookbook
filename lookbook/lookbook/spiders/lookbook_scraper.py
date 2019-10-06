# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.request import Request
import datetime

class LookbookScraperSpider(scrapy.Spider):
    page = 1
    name = 'lookbook_scraper'
    allowed_domains = ['www.lookbook.nu']
    start_urls = ['http://www.lookbook.nu/united-states']

    def to_time(self, string):
        string = string.replace('day', 'days')
        string = string.replace('hour', 'hours')
        string = string.replace('minute', 'minutes')
        string = string.replace('ss', 's')

        parsed_s = [string.split()[:2]]
        time_dict = dict((fmt, float(amount)) for amount, fmt in parsed_s)
        dt = datetime.timedelta(**time_dict)
        past_time = datetime.datetime.now() - dt
        return past_time


    def parse_look(self, look):

        id = look.xpath("@data-look-id").extract()[0]
        full_id = look.xpath("//div[@id='look_%s']//div[@class='hype']/@data-look-url" % id).extract()[0].strip('/look/')
        img = look.xpath("//a[@id='photo_%s']/img/@src" % id).extract()[0]
        hypes = look.xpath("//div[@class='hype' and @data-look-id='%s']/div/text()" % id).extract()[0]
        country = look.xpath("//div[@id='look_%s']//a[starts-with(@data-page-track,'byline - country')]/text()" % id).extract()[0]
        hashtags = look.xpath("//div[@id='look_%s']/ul/li/a/text()" % id).extract()
        timeago = look.xpath("//div[@id='look_%s']//div[@class='look-info']/text()" % id).extract()[-1].strip()
        created = self.to_time(timeago)

        item = {
            'id': id,
            'full_id': full_id,
            'created': created,
            'country': country,
            'hashtags': hashtags,
            'hypes': hypes,
            'img_src': img,
        }

        print('\n')
        return item


    # def parse_page(self, response):
    #     # First, check if next page available, if found, yield request
    #     next_link = response.xpath(
    #         "//a[@class='page-link next-page']/@href").extract_first()
    #     if next_link:
    #         # If the website has strict policy, you should do more work here
    #         # Such as modifying HTTP headers
    #
    #         # concatenate url
    #         url = response.url
    #         next_link = url[:url.find('?')] + next_link
    #         yield Request(
    #             url=next_link,
    #             callback=self.parse_list_page
    #         )
    #
    #     # find product link and yield request back
    #     for req in self.parse(response):
    #         yield req


    def parse(self, response):
        print("Processing..." + response.url)
        look_xpath = "//div[starts-with(@id,'look_') and @class='look_v2']"
        for look in response.xpath(look_xpath):
            # print(look)
            yield self.parse_look(look)

        if self.page < 5:
            yield scrapy.Request(
                url='http://www.lookbook.nu/united-states?page=' + str(self.page),
                callback=self.parse)
        self.page += 1