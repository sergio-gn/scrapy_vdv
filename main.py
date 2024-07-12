import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from my_spider import MySpider  # Ensure this is the correct import path for your spider
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ScrapyWorker(QThread):
    status_update = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, urls, title_xpath, description_xpath, photo_url_xpath, output_file):
        super().__init__()
        self.urls = urls
        self.title_xpath = title_xpath
        self.description_xpath = description_xpath
        self.photo_url_xpath = photo_url_xpath
        self.output_file = output_file

    def run(self):
        runner = CrawlerRunner()
        @inlineCallbacks
        def crawl():
            for url in self.urls:
                self.status_update.emit(f'Scraping URL: {url}')
                yield runner.crawl(MySpider, start_urls=[url], title_xpath=self.title_xpath, description_xpath=self.description_xpath, photo_url_xpath=self.photo_url_xpath, output_file=self.output_file)
            self.finished.emit()

        crawl()
        reactor.run(installSignalHandlers=False)

class ScrapyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Scrapy GUI')
        self.layout = QVBoxLayout()

        # URLs input
        self.urls_label = QLabel('Enter URLs (one per line):')
        self.layout.addWidget(self.urls_label)
        self.urls_input = QTextEdit(self)
        self.layout.addWidget(self.urls_input)

        # Title XPath
        self.title_label = QLabel('Enter Title XPath:')
        self.layout.addWidget(self.title_label)
        self.title_input = QLineEdit(self)
        self.layout.addWidget(self.title_input)

        # Description XPath
        self.description_label = QLabel('Enter Description XPath:')
        self.layout.addWidget(self.description_label)
        self.description_input = QLineEdit(self)
        self.layout.addWidget(self.description_input)

        # Photo URL XPath
        self.photo_url_label = QLabel('Enter Photo URL XPath:')
        self.layout.addWidget(self.photo_url_label)
        self.photo_url_input = QLineEdit(self)
        self.layout.addWidget(self.photo_url_input)

        # Output file selection
        self.output_button = QPushButton('Select Output File', self)
        self.output_button.clicked.connect(self.select_output_file)
        self.layout.addWidget(self.output_button)
        self.output_label = QLabel('No file selected', self)
        self.layout.addWidget(self.output_label)

        # Status label
        self.status_label = QLabel('Status: Ready', self)
        self.layout.addWidget(self.status_label)

        # Run button
        self.run_button = QPushButton('Run', self)
        self.run_button.clicked.connect(self.run_scraper)
        self.layout.addWidget(self.run_button)

        self.setLayout(self.layout)

    def select_output_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file:
            self.output_file = file
            self.output_label.setText(f'Selected: {file}')
            logger.info(f'Selected output file: {file}')

    def run_scraper(self):
        urls = self.urls_input.toPlainText().strip().split('\n')
        title_xpath = self.title_input.text()
        description_xpath = self.description_input.text()
        photo_url_xpath = self.photo_url_input.text()
        output_file = getattr(self, 'output_file', 'output.csv')
        logger.info(f'Starting scraper with URLs={urls}, title_xpath={title_xpath}, description_xpath={description_xpath}, photo_url_xpath={photo_url_xpath}, and output_file={output_file}')

        self.scrapy_worker = ScrapyWorker(urls, title_xpath, description_xpath, photo_url_xpath, output_file)
        self.scrapy_worker.status_update.connect(self.update_status)
        self.scrapy_worker.finished.connect(self.finished_scraping)
        self.scrapy_worker.start()

    def update_status(self, message):
        self.status_label.setText(f'Status: {message}')

    def finished_scraping(self):
        self.status_label.setText('Finished, you can close it now!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScrapyApp()
    ex.show()
    sys.exit(app.exec_())
