import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from harborone.items import Article


class harboroneSpider(scrapy.Spider):
    name = 'harborone'
    start_urls = ['https://www.harborone.com/about-us/news']

    def parse(self, response):
        articles = response.xpath('//div[@class="news-overview"]')
        for article in articles:
            date = article.xpath('./div[@class="date"]/text()').get()
            link = article.xpath('./h5/a/@href').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3[@class="bronze"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[contains(@class,"content")][h3]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
