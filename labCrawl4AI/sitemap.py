import asyncio
from typing import List
import requests
from xml.etree import ElementTree
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig # type: ignore
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator # type: ignore

def get_pydantic_ai_docs_urls():
    """
    Récupère toutes les URLs de la documentation Pydantic AI.
    Utilise le sitemap (https://ai.pydantic.dev/sitemap.xml) pour obtenir ces URLs.
    """
    sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        # Analyse le XML
        root = ElementTree.fromstring(response.content)

        # Extrait toutes les URLs du sitemap
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]

        return urls
    except Exception as e:
        print(f"Erreur lors de la récupération du sitemap: {e}")
        return []

async def crawl_sequential(urls: List[str]):
    print("\n=== Extraction séquentielle avec réutilisation de session ===")

    browser_config = BrowserConfig(
        headless=True,
        # Pour de meilleures performances dans Docker ou environnements à mémoire limitée:
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )

    # Crée le crawler (ouvre le navigateur)
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1"  # Réutilise la même session pour toutes les URLs
        for url in urls:
            result = await crawler.arun(
                url=url,
                config=crawl_config,
                session_id=session_id
            )
            if result.success:
                print(f"Extraction réussie: {url}")
                print(f"Longueur du Markdown: {len(result.markdown.raw_markdown)}")
                
                # Sauvegarde optionnelle du contenu dans un fichier
                # with open(f"output_{url.split('/')[-1]}.md", "w", encoding="utf-8") as f:
                #     f.write(result.markdown.raw_markdown)
            else:
                print(f"Échec: {url} - Erreur: {result.error_message}")
    finally:
        # Après avoir traité toutes les URLs, ferme le crawler (et le navigateur)
        await crawler.close()

async def main():
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Trouvé {len(urls)} URLs à extraire")
        await crawl_sequential(urls)
    else:
        print("Aucune URL trouvée à extraire")

if __name__ == "__main__":
    asyncio.run(main())