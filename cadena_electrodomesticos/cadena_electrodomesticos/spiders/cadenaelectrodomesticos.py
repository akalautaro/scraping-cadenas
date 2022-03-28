import scrapy
import time
from html_text import extract_text
from datetime import datetime
import pytz
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
import logging as log


# TODO: definir formato docstrings (https://realpython.com/documenting-python-code/)
class FravegaSpider(scrapy.Spider):
    """ Clase que define el spider para hacer web scraping en la web de Fravega.com.ar

    Attributes:
    name (str): nombre único del spider
    start_urls (:obj:`list` of :obj:`str`): lista de urls en los que se va a hacer scraping
    custom_settings (dict): diccionario con distintas configuraciones como el nombre y formato del archivo a exportar,
                            encoding, etc.
    """
    # scrapy crawl fravega-spider
    name = 'fravega-spider'
    start_urls = [
        'https://www.fravega.com/l/informatica/notebooks/',
        'https://www.fravega.com/l/climatizacion/ventilacion/',
        'https://www.fravega.com/l/climatizacion/aire-acondicionado/',
        'https://www.fravega.com/l/climatizacion/calefaccion-a-gas/',
        'https://www.fravega.com/l/lavado/lavarropas/',
        'https://www.fravega.com/l/celulares/celulares-liberados/',
        'https://www.fravega.com/l/cocina/',
        'https://www.fravega.com/l/?categorias=pequenos-electrodomesticos/cocina/tostadoras',
        'https://www.fravega.com/l/?keyword=cafetera%20de%20filtro',
        'https://www.fravega.com/l/pequenos-electrodomesticos/cocina/cafeteras-express/'
    ]
    custom_settings = {
        'FEED_URI': '../cadena_electrodomesticos/data/ProductosFravega.json',
        'FEED_FORMAT': 'json',
        'CONCURRENT_REQUESTS': 32,
        'MEMUSAGE_LIMIT_MB': 2048,
        'MEMUSAGE_NOTIFY_MAIL': ['example@gmail.com'],
        'ROBOTSTXT_OBEY': True,
        # 'DOWNLOAD_DELAY': 0.5,
        'FEED_EXPORT_ENCODING': 'UTF-8'
    }

    def parse(self, response, **kwargs):
        """ Recorre las urls contenidas en start_urls y extrae los links de todos los artículos de cada página.
        Se encarga de llamar a la función parse_prod() para cada url (que en este caso corresponde a un producto).

        Args:
            response: respuesta que devuelve el GET a la url
            **kwargs: por buena práctica

        Returns:
            llamada a la función parse_prod() como return parcial, al terminar de hacerlo con cada producto se llama a
            si misma para continuar en la siguiente página.
        """
        all_links = response.xpath('//div/ul[@class="SearchResultList-shopping-ui__sc-bsy0pv-0 Dszqt"]'
                                   '//li/article/a/@href').getall()
        for link in all_links:
            yield response.follow(link, callback=self.parse_prod, dont_filter=True,
                                  cb_kwargs={'url': response.urljoin(link)})

        next_page_button_link = response.xpath('//ul//li[@data-type="next"]//a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse)

    def parse_prod(self, response, **kwargs):
        """ Función encargada de extraer y volcar los datos de interés de cada producto en un json

        Args:
            response: response del GET hecho a la url el producto
            **kwargs: en este caso en el kwargs paso el link completo de la página del producto

        Returns:
            dict: diccionario con todos los datos que interesan del producto
        """
        link = kwargs['url']
        brand = response.xpath('//div[@data-test-id="product-info"]/a/@href').get()
        brand = brand.split('=')
        brand = brand[-1].upper()
        product = extract_text(response.xpath('//div[@data-test-id="product-info"]/h1/text()').get())
        ean = response.xpath('//li/div[@class="content"]//span[contains (text(), "Modelo")]'
                             '//following-sibling::span[@class="specValue"]/text()').get()
        code = extract_text(response.xpath('//div[@data-test-id="product-extended-description"]'
                                           '/div/p[@class="ExtendedDescription__DescriptionSubtitle-shopping-ui'
                                           '__sc-19p4e3l-3 goEeEa"]').get())

        online_price = response.xpath('//div[@data-test-id="price-wrapper"]/span/text()').get()
        # FIXME: No logré extraer las cuotas y el precio de las mismas.
        #  Ver preceding y follow sibling y armar el precio en cuotas
        #  quotes_price = extract_text(response.xpath('//span[@class=
        #  "InstallmentsData__InstallmentText-shopping-ui__sc-47y4o6-8 lnYjjs"]').get())
        quotes_price = None
        warranty = None

        bsas = pytz.timezone('America/Argentina/Buenos_Aires')
        timestamp = time.time()
        timestamp = datetime.fromtimestamp(timestamp, tz=bsas)

        yield {
            'ean/modelo': ean,
            'cod_interno': code,
            'marca': brand,
            'producto': product,
            'precio_online': online_price,
            'precio_cuotas': quotes_price,
            'garantia': warranty,
            'url': link,
            'timestamp': timestamp
        }


class MusimundoSpider(scrapy.Spider):
    """ Clase que define el spider para hacer web scraping en la web de Musimundo.com.ar

    Attributes:
    name (str): nombre único del spider
    start_urls (:obj:`list` of :obj:`str`): lista de urls en los que se va a hacer scraping
    custom_settings (dict): diccionario con distintas configuraciones como el nombre y formato del archivo a exportar,
                            encoding, etc.
    """
    # scrapy crawl musimundo-spider
    name = 'musimundo-spider'
    start_urls = [
        'https://www.musimundo.com/informatica/notebook/c/98',
        'https://www.musimundo.com/climatizacion/aire-acondicionado/c/21',
        'https://www.musimundo.com/electrohogar/lavarropas/c/147',
        'https://www.musimundo.com/electrohogar/cocinas/c/129',
        'https://www.musimundo.com/pequenos/cafeteras/c/202',
        'https://www.musimundo.com/pequenos/tostadoras/c/204',
        'https://www.musimundo.com/telefonia/telefonos-celulares/c/82',
        'https://www.musimundo.com/climatizacion/calefactores/c/23',
        'https://www.musimundo.com/climatizacion/ventiladores/c/22'
    ]
    custom_settings = {
        'FEED_URI': '../cadena_electrodomesticos/data/ProductosMusimundo.json',
        'FEED_FORMAT': 'json',
        'CONCURRENT_REQUESTS': 32,  # 32 peticiones a la vez como máx.
        'MEMUSAGE_LIMIT_MB': 2048,  # limitamos la ram que puede usar este spider. Muy útil si corre en un sv
        'MEMUSAGE_NOTIFY_MAIL': ['example@gmail.com'],  # envía si pasa mem
        'ROBOTSTXT_OBEY': True,  # siempre en True para mantener la ética y no nos metemos en líos
        # 'DOWNLOAD_DELAY': 0.5,
        'FEED_EXPORT_ENCODING': 'UTF-8'
    }

    def parse_prod(self, response, **kwargs):
        """ Función encargada de extraer y volcar los datos de interés de cada producto en un json

        Args:
            response: response del GET hecho a la url el producto
            **kwargs: en este caso en el kwargs paso el link completo de la página del producto

        Returns:
            dict: diccionario con todos los datos que interesan del producto
        """
        link = kwargs['url']
        brand = response.xpath('//div[@id="productPageDetailsId"]//div[@class="mus-pro-brand"]//span/text()').get()
        product = extract_text(response.xpath('//div[@id="productPageDetailsId"]'
                                              '//p[@class="mus-pro-name strong"]/text()').get())
        code = extract_text(response.xpath('//div[@id="productPageDetailsId"]//p[@class="mus-pro-code"]/text()').get())
        online_price = response.xpath('//div[@class="price-box-holder"]/div/p[@class="mus-pro-price"]'
                                      '//span[@class="mus-pro-price-number "]/span/text()').get()
        quotes_price = extract_text(response.xpath('//div[@class="mus-pro-quotes"]').get())
        warranty = response.xpath('//*[@id="fichaTecnica"]/div/table/tbody/tr//td[contains (text(), "Garantia")]'
                                  '//following-sibling::td/text()').get()
        ean = response.xpath('//div[@class="productDetailClass"]//td[contains (text(), "EAN")]'
                             '//following-sibling::td/text()').get()

        bsas = pytz.timezone('America/Argentina/Buenos_Aires')
        timestamp = time.time()
        timestamp = datetime.fromtimestamp(timestamp, tz=bsas)

        yield {
            'ean/modelo': ean,
            'cod_interno': code,
            'marca': brand,
            'producto': product,
            'precio_online': online_price,
            'precio_cuotas': quotes_price,
            'garantia': warranty,
            'url': link,
            'timestamp': timestamp
        }

    def parse(self, response, **kwargs):
        """ Recorre las urls contenidas en start_urls y extrae los links de todos los artículos de cada página.
        Se encarga de llamar a la función parse_prod() para cada url (que en este caso corresponde a un producto).

        Args:
            response: respuesta que devuelve el GET a la url
            **kwargs: por buena práctica

        Returns:
            llamada a la función parse_prod() como return parcial, al terminar de hacerlo con cada producto se llama a
            si misma para continuar en la siguiente página.
        """
        all_links = response.xpath('//div[@class="productListerGridItem"]//a/@href').getall()
        for link in all_links:
            yield response.follow(link, callback=self.parse_prod, dont_filter=True, cb_kwargs={'url': response.urljoin(link)})

        next_page_button_link = response.xpath('//div[@class="mus-bottom-paginator col span_12"]//ul[@class="pagination right"]//li[@class="next square not-border"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse)


if __name__ == "__main__":

    log.info('Comienza ejecución de los spiders')
    log.info('Importando configuraciones')
    settings = get_project_settings()
    log.info(f'RUNNING SPIDERS')
    runner = CrawlerRunner(settings)
    log.info('Process started')
    runner.crawl(FravegaSpider)
    runner.crawl(MusimundoSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    log.info('Process finished')
