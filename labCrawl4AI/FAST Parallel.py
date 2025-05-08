import os
import psutil
import asyncio
import requests
from xml.etree import ElementTree
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

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

async def crawl_parallel(urls: List[str], max_concurrent: int = 3, output_dir: str = "output"):
    print("\n=== Extraction parallèle avec réutilisation de navigateur + Suivi mémoire ===")

    # Création du dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    # Suivi de l'utilisation maximale de mémoire
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # en octets
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Mémoire actuelle: {current_mem // (1024 * 1024)} MB, Max: {peak_memory // (1024 * 1024)} MB")

    # Configuration minimale du navigateur
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Création de l'instance du crawler
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # Traitement des URLs par lots de 'max_concurrent'
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # ID de session unique par sous-tâche concurrente
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Vérification de l'utilisation de mémoire avant le lancement des tâches
            log_memory(prefix=f"Avant lot {i//max_concurrent + 1}: ")

            # Récupération des résultats
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Vérification de l'utilisation de mémoire après l'exécution des tâches
            log_memory(prefix=f"Après lot {i//max_concurrent + 1}: ")

            # Évaluation des résultats
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Erreur d'extraction {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1
                    # Sauvegarde du contenu extrait (optionnel)
                    file_name = url.split('/')[-1] if url.split('/')[-1] else "index"
                    file_path = os.path.join(output_dir, f"{file_name}.md")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(result.markdown.raw_markdown)
                    print(f"Contenu sauvegardé dans {file_path}")
                else:
                    fail_count += 1

        print(f"\nRésumé:")
        print(f"  - Extraction réussie: {success_count}")
        print(f"  - Échecs: {fail_count}")

    finally:
        print("\nFermeture du crawler...")
        await crawler.close()
        # Log final de mémoire
        log_memory(prefix="Final: ")
        print(f"\nUtilisation maximale de mémoire (MB): {peak_memory // (1024 * 1024)}")

async def main():
    # Installer psutil si ce n'est pas déjà fait
    try:
        import psutil
    except ImportError:
        print("Installation de psutil...")
        import subprocess
        subprocess.check_call(["pip", "install", "psutil"])
        import psutil
    
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Trouvé {len(urls)} URLs à extraire")
        await crawl_parallel(urls, max_concurrent=5, output_dir="output_docs")
    else:
        print("Aucune URL trouvée à extraire")

if __name__ == "__main__":
    asyncio.run(main())