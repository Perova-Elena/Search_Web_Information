from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lerua_scraper import settings
from lerua_scraper.spiders.leroymerlinru import LeroymerlinruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider, search='черепица')      # С помощью атрибута search мы делаем поиск по слову динамическим(задаваемым извне (из файла runner), а не в атрибутах класса (как было в проекте 6 урока с hhru))

    process.start()