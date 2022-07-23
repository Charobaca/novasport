# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NovasportItem(scrapy.Item):
    name = scrapy.Field()
    article = scrapy.Field()
    photos = scrapy.Field()
    weight = scrapy.Field()
    url = scrapy.Field()
