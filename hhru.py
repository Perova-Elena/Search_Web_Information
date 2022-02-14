import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem      # Нужно для обработки результатов поиска (вакансия, зарплата, url...)


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&area=2&no_magic=true&ored_clusters=true&items_on_page=20&enable_snippets=true&salary=&text=тьютор']

    def parse(self, response: HtmlResponse):

        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()                  # Реализуем перелистывание страниц, .get() в отличие от .getall() возвращает один результат (ссылку на следующую страницу)
        if next_page:                                                                        # Если следующая страница существует, то:
            yield response.follow(next_page, self.parse)                                     # То переходи на новую страницу


        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()       # Получаем список ссылок на каждую вакансию (помним, что .xpath возвращает список! []
                                                                                                   # Метод .getall() позволил нам извлечь сами ссылки, а не список типа selrctor
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)           # Обходим каждую ссылку. Мы делаем это через обьект response (так делают чаще всего), чтобы делать переходы в рамках текущей сессии,как бы не выходя из нее, т.к. паук имитирует работу браузера
                                                                   # Метод callback вызывает функцию vacancy_parse, не дожидаясь пока цикл пройдет все ссылки, тем самым разделяя на данном этапе потоки
                                                                  # yield делает из функции генератор и возвращает не один результат как return, а серию результатов


    def vacancy_parse(self, response):                            #  Метод vacancy_parse будет обрабатывать уже ту страницу вакансии, на которую перешли
        name = response.xpath("//h1//text()").get()
        salary = response.xpath("//div[@data-qa='vacancy-salary']//text()").getall()       # Мы не будем здесь обрабатывать результаты, их мы будем обрабатывать отдельно в файле items.py
        url = response.url                                                           # Тут искать ссылку не надо, мы уже в ней находимся, достаточно применить метод .url к текущему запросу
        yield JobparserItem(name=name, salary=salary, url=url)
