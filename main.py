import argparse
import news_page_object as news
# Para sacar cosas por consola más bonitas, no con print
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from common import config

def _news_scraper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    logging.info('Beginning scraper for {}'.format(host))
    homepage = news.HomePage(news_site_uid, host)
    for link in homepage.article_links:
        print (link)
        
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