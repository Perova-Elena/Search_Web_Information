# Добавляем необходимые библиотеки
from pprint import pprint
from lxml import html   # Библиотека с парсером HTML XPath
import requests         # Библиотека для запросов
from pymongo import MongoClient    # Библиотека для создания базы MongoDB

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36'}   # Заголовок для корректного входа на сайт, источник chrome/version

client = MongoClient('127.0.0.1', 27017)    # порт базы данных MongoDB
db = client['news_db']                      # Создаем БД для новостей со странички lenta.ru
news_collection = db.news_collection        # Создаем коллекцию в нашей базе
news_collection.drop()                      # Очистим коллекцию, чтобы при новом выполнении данные не задваивались

# Далее создадим функцию для сбора новостей:
def get_news():
    url = 'https://lenta.ru/'    # Адрес главной страницы (как видим, параметров нет)
    response = requests.get(url, headers=headers)  # Делаем запрос к этой странице

    dom = html.fromstring(response.text)    # Переформатируем результат запроса в нужную форму для XPath
    items = dom.xpath('//div/a[contains(@class,"card-") and contains(@class,"_topnews")]')   # Для начала создаем список из однотипных разделов новостей
                 # и в дальнейшем будем работать с каждым разделом отдельно

 #   news_list = []      # Это будет список из словарей (каждый словарь - 1 новость)
# Далее запускаем цикл, который будет проходиться по каждому разделу и выбирать нужные нам вещи
    for i in items:
        title = i.xpath('.//*[contains(@class,"_title")]/text()')[0]   # Выбираем заголовок новости
        link = url + i.get('href')   # Выбираем ссылку на новость
        date = '.'.join([s for s in i.get('href').split('/') if s.isdigit()]) # выбираем дату
        source = 'lenta.ru'
        news = {
            'title': title,
            'link': link,
            'date': date,
            'source': source
        }                             # Создаем словарь для i-той новости
        news_collection.insert_one(news)     # Добавляем i-тый словарь с новостью в коллекцию БД

    return

get_news()      # Вызываем функцию по сбору новостей
# Выводим дркументы из полученной коллекции на экран:
for doc in news_collection.find({}):         # Метод .find достает все документы коллекции
    pprint(doc)