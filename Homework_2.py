# Вначале импортируем необходимые библиотеки
import requests
from bs4 import BeautifulSoup as bS
import pandas as pd
import re

# Далее задаем заголовок и параметры для get запроса
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
url = 'https://hh.ru/search/vacancy'
params = {'items_on_page': '20',
              'text': 'Big Data',
              'page': '0'}

total_pages = 100

vacancies = []     # Задаем пустой список, куда будем складывать подошедшие нам вакансии

# Далее идет цикл, перебирающий все страницы:
for page in range(0, total_pages+1):
    params['page'] = page          # Присваиваем новой странице текущий номер, чтобы каждый раз запрос шел на новую страницу

    response = requests.get(url, params=params, headers=headers)   # Сам запрос к страницам с вакансиями на hh.ru
    dom = bS(response.text, 'html.parser')        # Загружаем полученный текст ответа в обьект BeautifilSoup

    vacancies_list = dom.find_all('div', {'class': 'vacancy-serp-item vacancy-serp-item_redesigned'})  # Создаем список вакансий
                                           # в качестве атрибута берем тег разделов страницы <div> с соответствующим классом

# Далее делаем цикл, перебирающий все вакансии по созданному списку:
    for vacancy in vacancies_list:
        vacancy_data = {} # Создаем пустой словарь для записи данных по нужной нам вакансии

        name = vacancy.find('a', {'data-qa': "vacancy-serp__vacancy-title"}).getText().replace(u'\xa0', u' ')  # выбираем имя вакансии и обрабатываем его, чтобы нормально читалось

        link = vacancy.find('a', {'data-qa': "vacancy-serp__vacancy-title"}).get('href') #выбираем ссылку на вакансию

# Далее обрабатываем так же поле - зарплата, с учетом того, что она может быть и не указана:
        try:
             salary = vacancy.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"}).getText().replace(u'\xa0', u'').replace(u'\u202f', u'')
        except:
             salary = None

        if salary == None:
            min_salary = None
            max_salary = None
            currency = None
        else:
            salary_prep1 = re.sub('–', '', salary)          # убираем прочерки из зарплаты
            salary_prep2 = re.split(r'\s+', salary_prep1)   # разбиваем по пробелам (варианты(где ?-величина зарплаты): от ? валюта, до ? валюта, ? ? валюта)
            if salary_prep2[0] == 'от':
                min_salary = salary_prep2[1]
                max_salary = None
            elif salary_prep2[0] == 'до':
                min_salary = None
                max_salary = salary_prep2[1]
            else:                                       # Если отсутствуют слова "от" и "до"
                min_salary = salary_prep2[0]
                max_salary = salary_prep2[1]

            currency = salary_prep2[2]             # Валюта (третья позиция после разбиения на пробелы)

        try:                                            # выгружаем название работодателя, если он указан
             employer = vacancy.find('div', {'class': "vacancy-serp-item__meta-info-company"}).getText().replace(u'\xa0', u' ')
        except:
             employer = None
# Далее записываем полученную информацию в словарь vacancy_data
        vacancy_data['name'] = name
        vacancy_data['link'] = link
        vacancy_data['min_salary'] = min_salary
        vacancy_data['max_salary'] = max_salary
        vacancy_data['currency'] = currency
        vacancy_data['employer'] = employer
        vacancy_data['site_name'] = 'hh.ru'

# Далее пополняем конечный список вакансий, и идем на новый круг по перебору вакансий:
        vacancies.append(vacancy_data)

# Далее создаем датафрейм со всеми вакансиями, записыавем его в файл .csv:
df = pd.DataFrame(vacancies)
df.to_csv('vacancies.csv', encoding="utf-8-sig")
print (df.shape)
print (df.head())