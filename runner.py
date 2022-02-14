# Данный файл мы создаем сами вручную, он никак не связан с конкретным проектом (в него мы будем подставлять своих пауков)
# Файл running нужен, чтобы корректно управлять запуском и отладкой проекта, т.к. без него не получится делать отладку
# через команду терминала - scrapy crawl [имя паука] (так сложно искать ошибки во время отладки)

# Здесь видно какое взаимодействие происходит, когда мы вызываем метод crawl через терминал,результат мы получим
# тот же, с тем лишь исключением, что теперь мы сможем запускать процесс в режиме отладки, т.е. можно теперь
# ставить breakpoint и делать промежуточную отладку, смотреть промежуточные результаты запросов и т.п.


# Импортируем классы из библиотеки scrapy для управления процессами:
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

# Импортируем настройки и класс конкретно своего паука:
from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider

# А теперь начинаем связывать все эти классы в логику между собой:
if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)     # извлекаем те глобальные настройки, которые мы делали вручную для своего паука в файле settings.py

    process = CrawlerProcess(settings=crawler_settings)      # Передаем настройки в экземпляр класса процесса
    process.crawl(HhruSpider)                                # Вызываемм сам процесс паука с hh.ru методом crawl
    process.crawl(SjruSpider)                                # Вызываемм сам процесс паука с superjob.ru методом crawl

    process.start()                                          # Запускаем процесс




