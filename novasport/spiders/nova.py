import scrapy
from novasport.items import NovasportItem


class NovaSpider(scrapy.Spider):
    name = 'nova'
    allowed_domains = ['novasport.ru']
    start_urls = ['http://novasport.ru/']

    def parse(self, response):
        categories = response.xpath(
            '//nav[@class="cbp-hrmenu"]/ul/*[position()<3]')

        for category in categories:
            subcategories = categories.xpath(
                './div[@class="cbp-hrsub"]/div[@class="cbp-hrsub-inner"]/div/ul/li/a/@href').getall()

            if len(subcategories) == 20:
                subcategories.pop(-1)

            for subcategory in subcategories:
                yield scrapy.Request(
                    url=f"https://novasport.ru{subcategories[0]}",
                    callback=self.process_subcategory,
                )

    def process_subcategory(self, response):
        products = response.xpath(
            '//div[@class="opt-ajax"]/div[@class="prod-item "]/div[@class="head"]/div[@class="name"]/a/@href').getall()

        for product in products:
            yield scrapy.Request(
                url=f"http://novasport.ru{product}",
                callback=self.process_product,
            )

        pagination = response.xpath(
            '//div[@class="paginator goods-paginator"]/ul/li/a[@class="icon next"]/@href').get()

        if not pagination == None:
            yield scrapy.Request(url=f"http://novasport.ru{pagination}", callback=self.process_subcategory)

    def process_product(self, response):
        items = NovasportItem()
        name = response.xpath('//div[@class="info"]/h1/text()').get()
        article = response.xpath(
            '//div[@class="info"]/div[@class="article"]/text()').get().split(" ")[1]
        selector = response.xpath('//select[@class="offer-select-rozn"]/*')
        product_variations = []

        if not selector == None:
            for item in selector[1:]:
                data_image = item.xpath('./@data-images').get()
                param = item.xpath('./text()').get()
                photos = response.xpath(
                    '//div[@class="b-wrap"]/div[@class="wrap"]/*')
                for photo_section in photos:
                    if data_image == photo_section.xpath('./@data-iid').get():
                        hrefs = photo_section.xpath(
                            './div[@class="col-l-7 col-d-7 hidden-m hidden-s wow fadeInUp "]/div[@class="product-thumbs text-center"]/a/@href').getall()
                        if not hrefs:
                            hrefs = photo_section.xpath(
                                './div/div[@class="product-img owl-carousel"]/a/@href').getall()
                        photo_urls = [
                            f'https://novasport.ru{href}' for href in hrefs]
                        product = {
                            "parameter": param,
                            "photo_urls": photo_urls
                        }
                        product_variations.append(product)

        if not selector:
            hrefs = response.xpath(
                '//div[@class="b-wrap"]/div[@class="wrap"]/div[@class="images active"]/div/div[@class="product-img owl-carousel"]/a/@href').getall()
            photo_url_single = [
                f'https://novasport.ru{href}' for href in hrefs]

        weight = response.xpath(
            '//*[contains(text(), "Вес")]  [not (contains(text(), "Вес пользователя"))]/../../div[@class="harval"]/text() | //*[contains(text(), "Вес нетто")]').get()

        if not product_variations == None:
            for product in product_variations:
                items['name'] = name
                items['article'] = f'{article} {product["parameter"]}'
                items['photos'] = product['photo_urls']
                items['weight'] = weight
                items['url'] = response.url

                yield items

        if not product_variations:
            items['name'] = name
            items['article'] = article
            items['photos'] = photo_url_single
            items['weight'] = weight
            items['url'] = response.url

            yield items
