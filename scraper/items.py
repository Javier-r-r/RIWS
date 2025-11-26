import scrapy


class ScraperItem(scrapy.Item):
        """Item for product pages on scuffers.com

        Fields:
            - url: product page URL
            - title: product title
            - description: product description / short description
            - price: numeric price (float) when available
            - currency: currency code or symbol found (e.g. 'EUR' or '€')
            - images: list of image URLs
            - sku: product SKU or identifier
            - availability: availability string (e.g. 'InStock')
            - sizes: list of available sizes/variants
            - size: primary/selected size
        """

        url = scrapy.Field()
        title = scrapy.Field()
        description = scrapy.Field()
        price = scrapy.Field()
        currency = scrapy.Field()
        images = scrapy.Field()
        sku = scrapy.Field()
        availability = scrapy.Field()
        # sizes: list of available sizes/variants (if any)
        sizes = scrapy.Field()
        # size: primary size or first available size
        size = scrapy.Field()