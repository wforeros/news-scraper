import requests
import bs4
from common import config

# Esta será la clase padre de nuestras páginas
class NewsPage:

    def __init__(self, news_site_uid, url):
        # El news_site_uid es el nombre de la página. EJ: elpais, eluniversal
        # traermos toda la configuración de esa página puntual
        self._config = config()['news_sites'][news_site_uid]
        # tomamos las queries que escribimos en nuestra config y las cargamos
        self._queries = self._config['queries']
        # Inicialmente no hay html
        self._html = None
        # Visitamos esa página con nuestro método _visit
        self._visit(url)

    # para visitar la página
    def _visit(self, url):
        # Hacemos la solicitud
        response = requests.get(url)

        # Lo que esto hace es que permite arrojar error si la solicitud no fue concluida correctamente
        response.raise_for_status()
        # Con ayuda de bs4 tomamos el texto ya parseado y lo guardamos en html
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')

    # Va a permitir acceder a info del documento que acabamos de parsear
    # puede ser un link, el titulo, una clase de css especial
    def _select(self, query_string):
        return self._html.select(query_string)

    
# Clase hija de NewsPage
# Contendrá nuestra página principal
class HomePage(NewsPage):

    def __init__(self, news_site_uid, url):
        # Llamamos el constructor de la clase padre
        super().__init__(news_site_uid, url)
        
    # El decorador lo que permite es que a esto se le trate como
    # atributo no como método
    @property
    def article_links(self):
        # creamos la lista donde guardamos todos links que hayan en esa página
        link_list = []
        # Para tomar los links cargamos las queries que tengamos, esto luego de haber 
        # revisado la página on inspect y anotar las clases css que nos sirven 
        # para la extracción
        for link in self._select(self._queries['homepage_article_links']):
            # si el link si tiene href
            if link and link.has_attr('href'):
                # es válido y lo guardamos
                link_list.append(link)
        # para que no se repitan links usaremos set
        return set(link['href'] for link in link_list)

# Esta clase también hereda de NewsPage pero será la encargada de visitar
# el sitio que tenga al artículo
class ArticlePage(NewsPage):
    # de nuevo usamos el cosntructor padre
    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)
        self.url = url

    # Esta propiedad permitirá que tomemos el título del artículo
    @property
    def title(self):
        # Ejecutamos el query que tiene las clases de css que nos permiten
        # acceder al título
        result = self._select(self._queries['article_title'])
        # Lo tomamos, es posible que esta parte cambie dependiendo de la
        # estructura, por ejemplo para ElTiempo toca cambiarla (a futuro)
        return result[0].text if len(result) else ''

    # Propiedad para tomar el cuerpo del artículo y se hace básicamente lo mismo
    # de arriba
    @property
    def body(self):
        result = self._select(self._queries['article_body'])
        return result[0].text if len(result) else ''
    


