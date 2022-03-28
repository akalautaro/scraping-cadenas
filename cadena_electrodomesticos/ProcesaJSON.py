from datetime import datetime
import pandas as pd
import os
import logging as log
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import inspect

import importlib
spiders_module = importlib.import_module("cadena_electrodomesticos.spiders.cadena-electrodomesticos")

# os.environ['']
# https://www.google.com/search?q=how+to+use+script+to+import+my+project+settings+SCRAPY&sxsrf=APq-WBuMvS4_HmwIRhupq0wrqJzYTUbgkg%3A1648062091581&ei=i247YuKFI96G1sQP4cqcsAg&ved=0ahUKEwii96Tc9dz2AhVeg5UCHWElB4YQ4dUDCA8&uact=5&oq=how+to+use+script+to+import+my+project+settings+SCRAPY&gs_lcp=Cgdnd3Mtd2l6EAMyBQghEKABOgcIIxCwAxAnOgcIABBHELADOgQIIRAVSgQIQRgASgQIRhgAUDZYtQtgxQxoAXABeACAAYYBiAHHBpIBAzAuN5gBAKABAcgBCcABAQ&sclient=gws-wiz
# https://stackoverflow.com/questions/53080035/scrapy-how-can-i-load-the-project-level-settings-py-while-using-a-script-to-st
# https://docs.scrapy.org/en/latest/topics/practices.html?
# https://stackoverflow.com/questions/33094306/being-able-to-change-the-settings-while-running-scrapy-from-a-script

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

log.basicConfig(level=log.INFO,
                format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s',
                datefmt='%I:%M:%S %p',
                handlers=[
                    log.FileHandler(f'./data/TransformProcess-{datetime.now().strftime("%Y%m%d")}.log'),
                    log.StreamHandler()
                ])


def procesa_json(archivo_json: str):

    log.info('Comienza procesa_json')

    if 'fravega' in archivo_json.lower():
        log.info(f'TransformFravega {archivo_json}')
        filedir = BASE_PATH + r'\\data\\' + archivo_json
        log.info(filedir)
        df = pd.read_json(filedir, orient='records')
        # print(df)

        df['ean/modelo'] = df['ean/modelo'].fillna('ND').str.strip()
        df['cod_interno'] = df['cod_interno'].str.extract('([0-9]+)').astype(int)
        df['producto'] = df['producto'].fillna('ND').str.strip()
        df['marca'] = df['marca'].fillna('ND').str.strip()
        df['precio_online'] = df['precio_online'].str.replace(r'[^0-9]+', '', regex=True).astype(int)
        df['precio_cuotas'] = df['precio_cuotas'].fillna('ND')
        df['garantia'] = df['garantia'].fillna('ND')
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        df.to_csv('./data/FravegaDataset.csv', index=False)

    elif 'musimundo' in archivo_json.lower():
        log.info(f'TransformMusimundo {archivo_json}')
        filedir = BASE_PATH + r'\\data\\' + archivo_json
        log.info(filedir)

        print('Falta hacer Musimundo pillin')


def lista_ficheros(dirname):
    lista_ficheros = os.listdir(dirname)
    return lista_ficheros


def ejecuta_procesa_json(lista_ficheros):
    for fichero in lista_ficheros:
        if fichero.endswith('.json'):
            procesa_json(fichero)
        else:
            log.info(f'Filetype de {fichero} incorrecto. No se procesa.')


def check_if_exists():
    """
    Chequea si los archivos .json existen, si no existen ejecuta los spiders, si existen los mueve a Old y luego ejecuta
    los spiders. Como buena práctica para no appendear los json.
    :return:
    """
    pass


def run_spiders(spiders: list):
    # check if exists

    """ CARGAR MÚLTIPLES CONFIGURACIONES
    https://stackoverflow.com/questions/53080035/scrapy-how-can-i-load-the-project-level-settings-py-while-using-a-script-to-st
    """

    log.info('Se ejecutan los spiders')
    for spider in spiders:
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        log.info(f'Configuraciones de {spider} importadas')
        process.crawl(spider)
        log.info(f'Running: {spider}')
        log.info('Process started')
        process.start()
        log.info('Process finished')


def run_spider(spider):
    # check if exists

    """ CARGAR MÚLTIPLES CONFIGURACIONES
    https://stackoverflow.com/questions/53080035/scrapy-how-can-i-load-the-project-level-settings-py-while-using-a-script-to-st
    """

    log.info('Se ejecutan los spiders')
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    log.info(f'Configuraciones de {spider} importadas')
    process.crawl(spider)
    log.info(f'Running: {spider}')
    log.info('Process started')
    process.start()
    log.info('Process finished')


def get_spiders():
    spiders = []
    for name, obj in inspect.getmembers(spiders_module):
        try:
            if inspect.isclass(obj):
                spiders.append(obj.name)
        except (Exception,):
            pass

    run_spiders(spiders)

    # return spiders


if __name__ == "__main__":
    # Comprobar si existe el json correspondiente a cada spider:
    # - Si existe: borrar el archivo y ejecutar el spider
    # - Si no existe: ejecutar el spider
    # Luego transformar la data y hacer el append al csv

    # print(spiders.MusimundoSpider.name)

    # spiders = []
    # for name, obj in inspect.getmembers(spiders_module):
    #     try:
    #         if inspect.isclass(obj):
    #             spiders.append(obj.name)
    #     except (Exception,):
    #         pass

    # TODO: editar ordern funciones:
    # Extract
    # - Scraper: run_spiders() -> get_spiders() -> check_if_exists()
    # Transform
    # - Pandas: procesa_json() -> lista_ficheros() -> ejecuta_procesa_json()

    # get_spiders()
    run_spider('fravega-spider')
    run_spider('musimundo-spider')
