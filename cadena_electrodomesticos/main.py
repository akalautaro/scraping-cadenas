import os
from datetime import datetime
import inspect
import logging as log
import pandas as pd
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from cadena_electrodomesticos.spiders import cadenaelectrodomesticos as ce

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


fravega = ce.FravegaSpider
musimundo = ce.MusimundoSpider

# Scrapy logging
configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
# Mi logger
log.basicConfig(level=log.INFO,
                format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s',
                datefmt='%I:%M:%S %p',
                handlers=[
                    log.FileHandler(f'./data/TransformProcess-{datetime.now().strftime("%Y%m%d")}.log'),
                    log.StreamHandler()]
                )



def procesa_json():
    """ Función encargada de procesar el archivo.json que deriva de cada spider, leyéndolo, volcándolo en un DataFrame
    de Pandas y aplicándole las transformaciones necesarias para que quede un archivo consistente y de igual estructura
    luego de scrapear cada web.

    Returns:
        FravegaDataset (csv): Dataframe de Pandas con los datos de cada archivo_json exportado a archivo csv.
    """
    archivos_json = get_files()

    log.info('Comienza procesa_json()')
    for archivo_json in archivos_json:
        if 'fravega' in archivo_json.lower():
            log.info(f'TransformFravega {archivo_json}')
            filedir = BASE_PATH + r'\\data\\' + archivo_json
            log.info(filedir)

            df = pd.read_json(filedir, orient='records')

            df['ean/modelo'] = df['ean/modelo'].fillna('ND').str.strip()
            df['cod_interno'] = df['cod_interno'].str.extract('([0-9]+)').astype(int)
            df['producto'] = df['producto'].fillna('ND').str.strip()
            df['marca'] = df['marca'].fillna('ND').str.strip()
            df['precio_online'] = df['precio_online'].str.replace(r'[^0-9]+', '', regex=True).astype(int)
            df['precio_cuotas'] = df['precio_cuotas'].fillna('ND')
            df['garantia'] = df['garantia'].fillna('0').astype(int)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            df.to_csv('./data/FravegaDataset.csv', index=False)

        elif 'musimundo' in archivo_json.lower():
            log.info(f'TransformMusimundo {archivo_json}')
            filedir = BASE_PATH + r'\\data\\' + archivo_json
            log.info(filedir)

            df = pd.read_json(filedir, orient='records')

            df['ean/modelo'] = df['ean/modelo'].fillna('ND')
            df['cod_interno'] = df['cod_interno'].str.extract('([0-9]+)').astype(int)
            df['producto'] = df['producto'].fillna('ND').str.strip()
            df['marca'] = df['marca'].fillna('ND').str.strip()
            precio_online = df['precio_online'].tolist()
            precio_online_f = []
            for p in precio_online:
                try:
                    if ',' in p:
                        precio_spliteado = p.split(',')
                        precio_online_f.append(precio_spliteado[0])
                    else:
                        precio_online_f.append(p)
                except (Exception,):
                    precio_online_f.append(p)
                    pass
            df['precio_online'] = precio_online_f
            df['precio_online'] = df['precio_online'].str.replace(r'[^0-9]+', '', regex=True).fillna('ND')

            # df['precio_cuotas'] = df['precio_cuotas']#.str.replace(r'[^0-9]+', '', regex=True).astype(int)
            df['precio_cuotas'] = df['precio_cuotas'].str.replace(r'\n', ' ', regex=True)
            df['garantia'] = df['garantia'].fillna('0').str.replace(r'[^0-9]+', '', regex=True).astype(int)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            df.to_csv('./data/MusimundoDataset.csv', index=False)


def get_files() -> list:
    """ Función que lista los archivos dentro del directorio data, para poder filtrar y usar los que me interesan (en
    este caso los json).

    Returns:
        lista_json (list): lista con los nombres de los archivos de extensión json.
    """
    log.info('Ejecución get_files()')
    lista_json = []
    lista_ficheros = os.listdir(rf'./data/')
    log.info(f'Archivos en ~/web-scraping/data: {lista_ficheros}')
    for fichero in lista_ficheros:
        if fichero.endswith('.json'):
            lista_json.append(fichero)
        else:
            pass
    log.info(f'Archivos json: {lista_json}')
    return lista_json


def check_if_exists() -> bool:
    """ Función que corrobora si existen los archivos json producto de ejecutar los Spiders, ya que Scrapy por defecto
    no sobreescribe los mismos, sino que hace una especie de append que, en este caso, no me sirve.
    Returns:
        bool: si es True los archivos ya fueron eliminados y se puede ejecutar el Spider, si es False ocurrió un error.
    """
    log.info('Ejecución de check_if_exists()')
    try:
        lista_ficheros = os.listdir(rf'./data/')
        log.info(f'{lista_ficheros}')
        for fichero in lista_ficheros:
            if fichero.endswith('.json'):
                os.remove(f'{BASE_PATH}/data/{fichero}')
                log.info(f'Fichero {BASE_PATH}/data/{fichero} eliminado')
            else:
                pass
        return True
    except Exception as e:
        log.error(f'OCURRIÓ UN ERROR INTENTANDO ELIMINAR LOS ARCHIVOS .JSON: {e}')
        return False


def run_spiders():
    """ Función que ejecuta los Spiders definidos en cadenaelectromesticos.py e importados al principio del script.
    Tomé los ejemplos de la documentación oficial de Scrapy:
    - https://docs.scrapy.org/en/latest/topics/practices.html
    - https://docs.scrapy.org/en/latest/topics/api.html#scrapy.crawler.CrawlerRunner
    - https://docs.scrapy.org/en/latest/topics/practices.html#run-from-script
    """

    log.info('Ejecución de run_spiders()')

    flag = check_if_exists()
    if flag is True:
        log.info('~/data -> clean, continúa ejecución')
        try:
            settings = get_project_settings()
            log.info('Importando configuraciones')
            runner = CrawlerRunner(settings)
            log.info(f'RUNNING SPIDERS')
            log.info('Process started')
            runner.crawl(fravega)
            runner.crawl(musimundo)
            d = runner.join()
            d.addBoth(lambda _: reactor.stop())
            reactor.run()
            log.info('Process finished')
        except Exception as e:
            log.error(f'OCURRIÓ UN ERROR: {e}')
    else:
        log.info('~/data -> not clean, termina ejecución')


def get_spiders():
    """ Función que lista los Spiders definidos en cadenaelectrodomésticos.py. Podría usarla en un futuro si tengo
    muchos spiders para ejecutar. Habría que redefinir la función run_spiders().

    Returns:
        spiders (list): lista que contiene el nombre de cada Spider definido.
    """
    spiders = []
    for name, obj in inspect.getmembers(ce):
        try:
            if inspect.isclass(obj) and 'Spider' in obj.__name__:
                print(obj.__name__)
                spiders.append(obj)
        except (Exception,):
            pass
    return spiders


if __name__ == "__main__":
    """ 
    1. Si se quieren ejecutar ambos Spiders, hay que llamar a la función run_spiders().
    2. Para hacer la transformación de los datos obtenidos, llamar a la función procesa_json().
    """

    procesa_json()
