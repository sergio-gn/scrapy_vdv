import scrapy
import csv
import os
from urllib.parse import urljoin
import requests

class MySpider(scrapy.Spider):
    name = 'my_spider'
    image_index = 1  # Class-level variable for image index
    
    def __init__(self, title_xpath=None, description_xpath=None, photo_url_xpath=None, output_file='output.csv', *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.title_xpath = title_xpath
        self.description_xpath = description_xpath
        self.photo_url_xpath = photo_url_xpath
        self.output_file = output_file
        self.image_folder = None  # Initialize image_folder to None

    def start_requests(self):
        self.image_folder = self.create_unique_folder('scraped_images')  # Create unique folder once
        yield from super().start_requests()

    def create_unique_folder(self, base_folder_name):
        if not os.path.exists(base_folder_name):
            os.makedirs(base_folder_name)
        return base_folder_name

    def parse(self, response):
        title = response.xpath(self.title_xpath).xpath('string()').get()
        description = response.xpath(self.description_xpath).xpath('string()').get()
        photo_url = response.xpath(self.photo_url_xpath).attrib.get('src')

        # Download and save the image
        if photo_url:
            image_url = urljoin(response.url, photo_url)
            image_filename = f"{MySpider.image_index}_image.png"  # Use class-level variable
            image_path = os.path.join(self.image_folder, image_filename)
            self.download_image(image_url, image_path)
            featured_image_url = f"https://verdeverdade.com.br/wp-content/uploads/2024/07/{image_filename}"
            MySpider.image_index += 1  # Increment class-level variable for next image
        else:
            featured_image_url = None

        # Write data to CSV
        with open(self.output_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([title, description, featured_image_url])

        self.log(f'Data saved to {self.output_file}')

    def download_image(self, url, path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            self.log(f"Failed to download image {url}: {e}")
