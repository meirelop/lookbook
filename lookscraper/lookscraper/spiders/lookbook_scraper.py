# -*- coding: utf-8 -*-
import scrapy
import datetime
from dateutil.relativedelta import relativedelta
import math
from ..items import LookbookItem


class LookbookScraperSpider(scrapy.Spider):
    PER_PAGE = 12
    INITIAL_PAGE = 1
    max_items = 100
    last_page = int(math.ceil(max_items/PER_PAGE))
    name = 'lookbook_scraper'
    # allowed_domains = ['www.lookbook.nu']
    start_urls = ['http://www.lookbook.nu/new']


    def to_time(self, string):
        string = string.replace('over', '')
        string = string.replace('year', 'years')
        string = string.replace('month', 'months')
        string = string.replace('week', 'weeks')
        string = string.replace('day', 'days')
        string = string.replace('hour', 'hours')
        string = string.replace('minute', 'minutes')
        string = string.replace('ss', 's')

        parsed_s = [string.split()[:2]]
        time_dict = dict((fmt, float(amount)) for amount, fmt in parsed_s)
        if time_dict.get('months'):
            past_time = datetime.datetime.now() - relativedelta(months=time_dict['months'])
        elif time_dict.get('years'):
            past_time = datetime.datetime.now() - datetime.timedelta(days=time_dict['years'] * 365)
        else:
            dt = datetime.timedelta(**time_dict)
            past_time = datetime.datetime.now() - dt

        return past_time


    def parse_look(self, look):
        item = LookbookItem()

        id = look.xpath("@data-look-id").extract()[0]
        item['look_id'] = id
        item['full_id'] = look.xpath("//div[@id='look_%s']//div[@class='hype']/@data-look-url" % id).extract()[0].strip('/look/')
        item['img_url'] = look.xpath("//a[@id='photo_%s']/img/@src" % id).extract()[0].strip('//')
        item['hype'] = look.xpath("//div[@class='hype' and @data-look-id='%s']/div/text()" % id).extract()[0]
        item['country'] = look.xpath("//div[@id='look_%s']//a[starts-with(@data-page-track,'byline - country')]/text()" % id).extract()[0]
        hashtags_temp = look.xpath("//div[@id='look_%s']/ul/li/a/text()" % id).extract()
        item['hashtags'] = [tag.replace('#', '') for tag in hashtags_temp]
        timeago = look.xpath("//div[@id='look_%s']//div[@class='look-info']/text()" % id).extract()[-1].strip()
        item['created'] = self.to_time(timeago)

        print('\n')
        item.save()
        return item


    def parse_country(self, response, country_url):
        look_xpath = "//div[starts-with(@id,'look_') and @class='look_v2']"
        for look in response.xpath(look_xpath):
            yield self.parse_look(look)

        self.INITIAL_PAGE += 1
        if self.INITIAL_PAGE <= self.last_page:
            yield scrapy.Request(
                url=country_url + '?page=' + str(self.INITIAL_PAGE),
                callback=self.parse_country,
                cb_kwargs=dict(country_url=country_url))



    def parse(self, response):
        print("Processing..." + response.url)
        countries = response.xpath("//ul[@id='country_collections']/li/a/@href").extract()
        # countries = countries[0:1]
        # print('TOTAL COUNTRIES:', countries)
        for country in countries:
            print(country)
            request = scrapy.Request(url=country,
                                     callback=self.parse_country,
                                     cb_kwargs=dict(country_url=country))
            yield request