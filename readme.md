# Scraper multisite cadenas de electrodomésticos
### Idea
La idea de este proyecto era "jugar" un poco a extraer datos de la web, ya que nunca lo había hecho, y además que sean 
de mi interés, por lo que elegí hacerlo con la web de Musimundo. Una vez que más o menos funcionó me copó y busqué la 
forma de agregar otras páginas similares como Fravega, que me permitan en un futuro juntar todos los datos que me 
interesen de las páginas y poder comprar lo que me interesa al mejor precio.

### Estructura del proyecto
```
├───cadena_electrodomesticos
│   └───spiders
└───data
```
En el directorio principal se encuentran las configuraciones de Scrapy como también el script `main.py` que es el que 
ejecuta ambos spiders y la función que formatea los datos.

En el directorio `spiders` están definidos tanto el de Fravega como el de Musimundo.

En el directorio `data` se encuentran los datos extraídos de la web en formato `.json`, los datasets resultantes en 
formato `.csv` y también los logs del script.

### Pre-requisitos
Para descargar este script e instalar todo lo necesario para ejecutarlo:
```
https://github.com/akalautaro/scraping-cadenas.git

pip install -r requirements.txt
```

## MUSIMUNDO
### Datos a scrapear
### Página Inicio
- Url producto
- Botón próxima página

### Página del producto
- EAN
- Producto
- Marca
- Urls
- Cod. interno
- Precio online
- Precio cuotas
- Garantía

### Ejecución con `scrapy crawl`:
```
~/cadena_electrodomesticos> scrapy crawl fravega-spider
~/cadena_electrodomesticos> scrapy crawl musimundo-spider
```

#### Tiempo de ejecución con `scrapy crawl`:
La primera versión del scraper la realicé con BeautifulSoup4 y aunque cumplía la misma función (con muchos ciclos for 
y validaciones de por medio), demoraba 6 minutos aproximadamente para traer ~100 resultados.

Este tiempo mejoró bastante usando ```concurrent.futures```, pasando a ~1.3 min. para la misma cantidad de resultados 
(4.65x veces más rápido).

Aprovechando el #PlatziDay hice el [Curso de Scrapy](https://platzi.com/cursos/scrapy/) y los resultados para la misma 
web usando este framework fueron los siguientes:
```
2022-03-21 15:09:44 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 90638,
 'elapsed_time_seconds': 26.148441,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2022, 3, 21, 18, 9, 44, 908222),
 'item_scraped_count': 151,
 ...
 'start_time': datetime.datetime(2022, 3, 21, 18, 9, 18, 759781)}
2022-03-21 15:09:44 [scrapy.core.engine] INFO: Spider closed (finished)
```
Demoró aproximadamente **26 segundos** para ~150 resultados (originalmente eran 100), casi **14x** más veloz que la 
solución original con BS4 y requests, y **3x** veces más veloz que utilizando BS4 y multithreading.

Al ejecutar los spiders, la data se almacena en formato `.json` dentro de la carpeta `~/cadena_electrodomesticos/data/`, 
y al procesar el mismo se guarda la data ya transformada en formato `csv`.

## Ejecución de varios spiders con `CrawlerRunner`

Para ejecutar el spider de Musimundo y Fravega definí las funciones de todo el ETL en el archivo `main.py`, que se 
encarga de ejecutar los spiders y además de transformar los datos que extraigo de las webs para volcarlos en un archivo 
`.csv`.

#### Ejecución:
`./web-scraping/cadena_electrodomesticos/main.py`

Los archivos resultantes del web scraping son almacenados en `~/cadena_electrodomesticos/data/` en formato `.json`, 
luego de manipular los datos con Pandas se guardan como `.csv` en el mismo directorio.

### Resumen de stats de la ejecución con `CrawlerRunner`:
**Musimundo**
```
2022-03-26 11:46:29 [scrapy.extensions.feedexport] INFO: Stored json feed (633 items) in: ../cadena_electrodomesticos/data/ProductosMusimundo.json
2022-03-26 11:46:29 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 418526,
 'downloader/request_count': 744,
 'downloader/request_method_count/GET': 744,
 'downloader/response_bytes': 23554371,
 'downloader/response_count': 744,
 'elapsed_time_seconds': 58.539706,
 'feedexport/success_count/FileFeedStorage': 1,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2022, 3, 26, 14, 46, 29, 204166),
 'item_scraped_count': 633,
 'start_time': datetime.datetime(2022, 3, 26, 14, 45, 30, 664460)}
2022-03-26 11:46:29 [scrapy.core.engine] INFO: Spider closed (finished)
```
*Resumen Musimundo*: 58 segundos para 633 resultados.

**Fravega**
```
2022-03-26 11:52:46 [scrapy.extensions.feedexport] INFO: Stored json feed (1374 items) in: ../cadena_electrodomesticos/data/ProductosFravega.json
2022-03-26 11:52:46 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 529061,
 'downloader/request_count': 1481,
 'downloader/request_method_count/GET': 1481,
 'downloader/response_bytes': 128579839,
 'downloader/response_count': 1481,
 'downloader/response_status_count/200': 1481,
 'elapsed_time_seconds': 435.861936,
 'feedexport/success_count/FileFeedStorage': 1,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2022, 3, 26, 14, 52, 46, 517371),
 'item_scraped_count': 1374,
 'start_time': datetime.datetime(2022, 3, 26, 14, 45, 30, 655435)}
2022-03-26 11:52:46 [scrapy.core.engine] INFO: Spider closed (finished)
```
*Resumen Fravega*: ~436 segundos para 1374 resultados.

### TODO:
- Extraer precio en cuotas de Fravega
- Ver la estructura de los archivos csv para agregar cant. de cuotas, costo de las mismas y precio final en cuotas
- Ejecutar spiders individuales o todos juntos (tal cual está ahora)
- Agregar otras web (pueden ser Megatone, Mercado Libre, Bodrone, Walmart, etc)
