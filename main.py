# Esto para parsear los argumentos de nuestro programa
# estos se encuentran en el config.yaml, serían elpais y eleluiversal
import argparse
# Para saber de cuándo es
import datetime
# Para guardar nuestros datos
import csv
# Aquí están nuestras clases
import news_page_object as news
# Módulo para expresiones regulares
import re
# Para sacar cosas por consola más bonitas, no con print
import logging
# Import de errores que se nos pueden presentar
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
# Configuración básica
logging.basicConfig(level=logging.INFO)
# Le decimos que de aquí (del main) será usado
logger = logging.getLogger(__name__)

# Comienza con la r porque le indica a python que esto es un string 'raw', 
# el ^ indica que ese es el inicio de la palabra
# el ? dice que la s es opcional
# .+ porque queremos que tenga una o más letras
# Un patrón que haría match aquí sería: https://example.com/hello
is_well_formed_link = re.compile(r'^https?://.+/.+')

# Queremos saber si es un path que se basa en la raíz, y sabemos que estos comienzan
# con una diagonal, por eso ponemos ^/
# y con $ decimos que termina nuestra expresión
# una que haría match es /hello
is_root_path = re.compile(r'^/.+$')
# Importamos la función que nos cargará lo que tenemos en la config
from common import config

# Esta función inicia nuestro scraper
# el news_site_uid es el argumento, por ejemplo 'eluniversal'
def _news_scraper(news_site_uid):
    # accedemos a la url principal que se encuentra en nuestra config
    host = config()['news_sites'][news_site_uid]['url']
    # Mensaje de inicio
    logging.info('Beginning scraper for {}'.format(host))
    # Instanciamos un objeto de tipo HomePage
    homepage = news.HomePage(news_site_uid, host)
    # En esta lista irán nuestros artículos
    articles = []
    # recorremos todos los links que encontramos en la pag principal
    for link in homepage.article_links:
        # llamamos a fetch article para que nos traiga el artículo (o retorne None si no hay)
        article = _fetch_article(news_site_uid, host, link)
        # Si encontró el artículo
        if article:
            # Decimos que sí wooooooon
            logger.info('Article fetched!!')
            # Lo añadimos a nuestra lista
            articles.append(article)
    _save_articles(news_site_uid, articles)

def _save_articles(news_site_uid, articles):
    # Tomar la hora de ese momento
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    out_file_name = '{news_site_uid}_{datetime}_articles.csv'.format(
        news_site_uid=news_site_uid,
        datetime=now
    )
    # Generaremos los headers de nuestro csv
    # una función lambda es una función inline
    # con esa función lo que hacemos es que buscamos todos los metodos del primer artículo
    # esto porque todos los artículos tendrán los mismos métodos, la idea es 
    # El filtro es para tomar los que no sean privados (no empiezan con '_')
    # y pues sabemos que el resultado será body y title
    # el filtro nos da un iterador, por eso lo convertimos con list
    # estos nos ayuda por si agregamos propiedades, directamente nos permitirá tomarlas
    # no tenemos que cambiar nada
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    with open(out_file_name, mode='w+') as f:
        writer = csv.writer(f)
        # Escribimos nuestros headers (la primera fila)
        writer.writerow(csv_headers)
        for article in articles:
            # Así tomamos las propiedades que tenemos como headers, 
            # entonces guardamos el 100% sin importar que las hayamos creado después
            row = [str(getattr(article, prop))for prop in csv_headers]
            writer.writerow(row)
           

# Esta función nos permite traer el artículo especificado 
def _fetch_article(news_site_uid, host, link):
    # Mensaje de que está buscando el artículo
    logger.info('Start fetching article at: {}'.format(link))
    article = None
    # Nos puede retornar error (ver el comentario del except)
    try:
        # instanciamos un objeto de ArticlePage, pero antes construimos el link
        # con la función _buid_link
        article = news.ArticlePage(news_site_uid, _buid_link(host, link))
    
    # HTTPError, cuando la pag no existe, MaxRetryError elimina la posibilidad de que se vaya
    # mucho tiempo intentando acceder
    except (HTTPError, MaxRetryError):
        # Saca el aviso pero no saca el error de la vida
        logger.warning('Error while fetching the article with link {}'.format(link), exc_info=False)
        pass
    
    # Si el articulo no tiene cuerpo... No nos sirve
    if article and not article.body:
        logger.warning('Invalid article, there is not body', exc_info=False)
        return None
    # Retornamos el artículo
    return article


# Esto nos permitirá construir una url
def _buid_link(host, link):
    # Usaremos el modulo de expresiones regulares (re)
    # Si hace match aquí quiere decir que el link está ok
    if is_well_formed_link.match(link):
        return link
    # Si hace match aquí quiere decir que es sólo /algo y toca formar la url completa
    elif is_root_path.match(link):
        return '{}{}'.format(host, link)
    # Sino el enlace no sirve porque no inicia con http o /
    else:
        return '{host}/{uri}'.format(host=host, uri=link)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_site_choices = list(config()['news_sites'].keys())
    # Los choices vendrán de nuestra config
    parser.add_argument('news_site', help='The news site you want to scrape', 
                        type=str,
                        choices=news_site_choices
                        )

    # Ahora parseamos nuestros argumentos 
    args = parser.parse_args()
    _news_scraper(args.news_site)