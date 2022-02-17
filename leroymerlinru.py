import scrapy
from scrapy.http import HtmlResponse
from leroymerlinparser.items import LeruaScraperItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__()                                                                   # Сначала наследуем родительский конструктор класса, а потом на его базе строим свой
        self.start_urls = [f'https://leroymerlin.ru/search/?q={kwargs.get("search")}']       # Перенесли start_urls в конструктор класса, чтобы задавать слово для поиска динамически(извне, т.е. из файла runner, а не из кода паука)
                                                                                             # {} - скобки делают строку динамической, kwargs это все что пришло в конструктор класса, включая search, который мы извлечем после выполнения process.crawl(LeroymerlinruSpider, search='слово')
    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()     # Настраиваем перелистывание страниц (по кнопке "Следующая")
        if next_page:                                                                       # Пока кнопка есть выполни переход:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='product-name']")                             # Обратим внимание, мы не извлекаем здесь конечную ссылку @href и не применяем метод .getall(), а извлекаем весь тег а целиком т.к. паук чаще всего может сам доходить до ссылок
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):                                           # Функция по загрузке данных о товаре
        loader = ItemLoader(item=LeruaScraperItem(), response=response)                    # Формируем item
        loader.add_value('url', response.url)
        loader.add_xpath('_id', '//div[@class="product-detailed-page"]/@data-product-id')
        loader.add_xpath('name', '//div[@class="product-detailed-page"]/@data-product-name')
        loader.add_xpath('price', '//div[@class="product-detailed-page"]/@data-product-price')
        loader.add_xpath('photos', '//img[@alt="product image"]/@src')
        loader.add_xpath('chars_key', '//dt//text()')
        loader.add_xpath('chars_value', '//dd//text()')
        yield loader.load_item()