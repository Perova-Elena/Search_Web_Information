# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):                                                              # Создадим конструктор класса и пропишем там соединение с базой данных, чтобы обратиться к ней единожды, а не обращаться каждый раз заново
        client = MongoClient('127.0.0.1', 27017)
        client.drop_database('vacancies1402')
        self.mongobase = client.vacancies1402

    def process_hhru_salary(dirty_salary):      # Обработка зарплаты c hh.ru
        if dirty_salary[0] == 'от ':
            min_salary = dirty_salary[1]
        if dirty_salary[0] == 'до ':
            min_salary = None
            max_salary = dirty_salary[1]
        if 'от ' in dirty_salary and 'до ' not in dirty_salary:
            min_salary = dirty_salary[1]
            max_salary = None
        if ' до ' in dirty_salary:
            max_salary = dirty_salary[3]
        if dirty_salary[0] == 'з/п не указана':
            min_salary = None
            max_salary = None
            currency = None
        if 'руб.' in dirty_salary:
            currency = 'руб.'
        elif 'USD' in dirty_salary:
            currency = 'USD'
        return min_salary, max_salary, currency

    def process_sjru_salary(dirty_salary):       # Обработка зарплаты c superjob.ru
        min_salary, max_salary, currency = None, None, 'руб'
        if dirty_salary[0] == 'от':
            min_salary = int(''.join(filter(str.isdigit, dirty_salary[2].replace('\xa0', ''))))
        elif dirty_salary[0] == 'до':
            max_salary = int(''.join(filter(str.isdigit, dirty_salary[2].replace('\xa0', ''))))
        elif len(dirty_salary) > 3:
            min_salary = int(''.join(filter(str.isdigit, dirty_salary[0].replace('\xa0', ''))))
            max_salary = int(''.join(filter(str.isdigit, dirty_salary[4].replace('\xa0', ''))))
        else:
            currency = None
        return min_salary, max_salary, currency


    def process_item(self, item, spider):
        if spider.name == 'hhru':
            salary = self.process_hhru_salary(item.get('salary'))
        else:
            salary = self.process_sjru_salary(item.get('salary'))
        item['min_salary'], item['min_salary'], item['currency'] = salary
        del item['salary']                                                     # Удаляем промежуточную "грязную" зарплату (которая была до обработки)
        collection = self.mongobase[spider.name]                               # Очень удобный подход, при котором item-ы сортируются в нужную коллекцию по имени паука, это нужно, когда пауков несколько и данные могут прилетать то от одного, то от другого паука
        collection.insert_one(item)                                            # Добавляем обработанные данные в коллекцию
        return item

