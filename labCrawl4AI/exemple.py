import os
import asyncio
import re
from typing import List, Set
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

class WebsiteCrawler:
    def __init__(self, base_url: str, output_dir: str = "crawled_data"):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls: Set[str] = set()
        self.urls_to_visit: List[str] = [base_url]
        self.output_dir = output_dir
        
        # Création du dossier de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Configuration du crawler
        self.browser_config = BrowserConfig(
            headless=True,
            extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
        )
        self.crawler = None
    
    def get_robots_txt_rules(self):
        """Récupère les règles de robots.txt"""
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            response = requests.get(robots_url)
            if response.status_code == 200:
                print(f"Règles robots.txt trouvées: {robots_url}")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            else:
                print(f"Pas de robots.txt trouvé à {robots_url}")
        except Exception as e:
            print(f"Erreur lors de la récupération de robots.txt: {e}")
    
    def extract_links(self, url: str, html_content: str) -> List[str]:
        """Extrait les liens d'une page HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Convertit les URLs relatives en URLs absolues
            full_url = urljoin(url, href)
            
            # Vérifie si l'URL est dans le même domaine
            if urlparse(full_url).netloc == self.domain:
                links.append(full_url)
        
        return links
    
    async def crawl_site(self, max_pages: int = 10, max_concurrent: int = 3):
        """Parcourt le site en extrayant le contenu et en suivant les liens"""
        try:
            # Démarre le crawler
            self.crawler = AsyncWebCrawler(config=self.browser_config)
            await self.crawler.start()
            
            page_count = 0
            
            while self.urls_to_visit and page_count < max_pages:
                # Prend un lot d'URLs à traiter
                batch_size = min(max_concurrent, max_pages - page_count, len(self.urls_to_visit))
                batch_urls = [self.urls_to_visit.pop(0) for _ in range(batch_size)]
                tasks = []
                
                for url in batch_urls:
                    # Marque l'URL comme visitée
                    self.visited_urls.add(url)
                    # Crée une tâche pour extraire la page
                    session_id = f"session_{page_count}"
                    task = self.process_page(url, session_id)
                    tasks.append(task)
                
                # Exécute les tâches en parallèle
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Analyse les résultats et collecte de nouveaux liens
                for url, result in zip(batch_urls, batch_results):
                    if isinstance(result, Exception):
                        print(f"Erreur lors du traitement de {url}: {result}")
                    elif result:
                        print(f"Traité avec succès: {url}")
                        page_count += 1
                
                print(f"Pages traitées: {page_count}/{max_pages}")
            
            print(f"\nTerminé! {page_count} pages ont été extraites et sauvegardées dans {self.output_dir}")
        
        finally:
            # Ferme le crawler à la fin
            if self.crawler:
                await self.crawler.close()
    
    async def process_page(self, url: str, session_id: str) -> bool:
        """Traite une page web individuelle"""
        try:
            # Extraction de la page
            result = await self.crawler.arun(
                url=url,
                session_id=session_id
            )
            
            if not result.success:
                print(f"Échec de l'extraction: {url} - {result.error_message}")
                return False
            
            # Sauvegarde du contenu Markdown
            file_name = self.url_to_filename(url)
            file_path = os.path.join(self.output_dir, file_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.markdown.raw_markdown)
            
            # Extraction des nouveaux liens
            new_links = self.extract_links(url, result.raw_html)
            
            # Ajoute les nouveaux liens non visités à la liste à visiter
            for link in new_links:
                if link not in self.visited_urls and link not in self.urls_to_visit:
                    self.urls_to_visit.append(link)
            
            return True
        
        except Exception as e:
            print(f"Erreur lors du traitement de {url}: {e}")
            return False
    
    def url_to_filename(self, url: str) -> str:
        """Convertit une URL en nom de fichier valide"""
        # Supprime le protocole et le domaine
        path = urlparse(url).path
        
        # Traite les cas spéciaux
        if path == "" or path == "/":
            return "index.md"
        
        # Remplace les caractères non valides pour les noms de fichiers
        filename = re.sub(r'[\\/*?:"<>|]', "_", path)
        
        # Supprime les slashes de début et de fin
        filename = filename.strip("/")
        
        # Remplace les slashes restants par des underscores
        filename = filename.replace("/", "_")
        
        # Ajoute l'extension .md si nécessaire
        if not filename.endswith(".md"):
            filename += ".md"
        
        return filename

async def main():
    # URL du site à extraire
    site_url = "https://ai.pydantic.dev/"  # Remplacez par le site de votre choix
    
    # Installez les dépendances si nécessaire
    try:
        import bs4
    except ImportError:
        print("Installation de BeautifulSoup...")
        import subprocess
        subprocess.check_call(["pip", "install", "beautifulsoup4"])
    
    # Création du crawler
    crawler = WebsiteCrawler(site_url, output_dir="site_content")
    
    # Vérification des règles robots.txt
    crawler.get_robots_txt_rules()
    
    # Lancement de l'extraction
    print(f"Démarrage de l'extraction du site: {site_url}")
    await crawler.crawl_site(max_pages=20, max_concurrent=5)

if __name__ == "__main__":
    asyncio.run(main())