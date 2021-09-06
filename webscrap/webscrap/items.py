# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WebscrapItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    count =     scrapy.Field()
    custnames = scrapy.Field()
    ratings = scrapy.Field()
    headings = scrapy.Field()
    # comment = scrapy.Field()
    dates = scrapy.Field()
    areas = scrapy.Field()
    custtypes = scrapy.Field()


