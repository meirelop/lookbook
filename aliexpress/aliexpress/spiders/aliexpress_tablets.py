# -*- coding: utf-8 -*-
import scrapy


class AliexpressTabletsSpider(scrapy.Spider):
    name = 'aliexpress_tablets'
    # allowed_domains = ['https://www.aliexpress.com']
    start_urls = ['https://www.aliexpress.com/']

    def parse(self, response):
        print("Processing..." + response.url)
        product_name = response.xpath('//span[@class="current-price"]').extract()
        title_name = response.xpath('//a[@class="item-title"]/text()').extract()
        row_data = zip(product_name, title_name)

        for item in row_data:
            scraped_info = {
                'page': response.url,
                'product_name': item[0],
                'title_name': item[1]
            }

            yield scraped_info