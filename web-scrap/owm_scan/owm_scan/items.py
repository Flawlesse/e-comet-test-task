# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OwmScanItem(scrapy.Item):
    city_id = scrapy.Field()
    city_name = scrapy.Field()
    city_code = scrapy.Field()
    temperature = scrapy.Field()
    windspeed = scrapy.Field()
    pressure = scrapy.Field()
