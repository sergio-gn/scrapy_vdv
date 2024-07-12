import scrapy
import csv

class MySpider(scrapy.Spider):
    name = 'my_spider'

    def __init__(self, title_xpath=None, description_xpath=None, photo_url_xpath=None, output_file='output.csv', *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.title_xpath = title_xpath
        self.description_xpath = description_xpath
        self.photo_url_xpath = photo_url_xpath
        self.output_file = output_file

    def parse(self, response):
        title = response.xpath(self.title_xpath).xpath('string()').get()
        description = response.xpath(self.description_xpath).xpath('string()').get()
        photo_url = response.xpath(self.photo_url_xpath).attrib.get('src')

        with open(self.output_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([title, description, photo_url])

        self.log(f'Data saved to {self.output_file}')
