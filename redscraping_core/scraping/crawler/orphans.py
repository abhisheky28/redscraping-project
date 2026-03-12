# redscraping_core/scraping/crawler/orphans.py

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Confirm
from urllib.parse import urlparse
import gc
import time

from .db_manager import DBManager
from .crawler_engine import AsyncCrawlerEngine
from .drive_manager import DriveManager
from .domain_utils import get_true_domain_info

console = Console()

def get_sitemap_urls(base_url):
    urls = set()
    clean_base = base_url.rstrip('/')
    sitemap_url = f"{clean_base}/sitemap.xml"
    try:
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for loc in soup.find_all('loc'):
                if loc.text: urls.add(loc.text.strip())
    except Exception:
        pass
    return list(urls)

def run_orphans_crawler(domain, limit, output_format, restart):
    base_dir = os.getcwd()
    output_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, ".cache")
    
    start_url, domain_name = get_true_domain_info(domain)
    db_path = os.path.join(cache_dir, f"{domain_name}_orphans.db")

    if restart and os.path.exists(db_path):
        os.remove(db_path)
        console.print(f"[yellow]🔄 Restarting crawl for {domain_name}. Old local database cleared.[/yellow]")

    use_cloud = False
    drive = None
    if Confirm.ask("\n[bold cyan]☁️ Do you want to sync this crawl with your Google Drive to speed up future runs?[/bold cyan]"):
        use_cloud = True
        drive = DriveManager()
        if not restart and not os.path.exists(db_path):
            drive.download_db(f"{domain_name}_orphans", db_path)
    else:
        console.print("[dim]Skipping Google Drive sync. Using local cache only.[/dim]\n")

    db = DBManager(db_path)
    
    # 1. Fetch and save the sitemap URLs to the special table
    console.print("[cyan]🗺️ Downloading Sitemap for cross-referencing...[/cyan]")
    sitemap_urls = get_sitemap_urls(start_url)
    if sitemap_urls:
        console.print(f"[green]✅ Saved {len(sitemap_urls)} URLs from sitemap.[/green]")
        db.save_sitemap_urls(sitemap_urls)
        # We DO NOT add them to the queue. We want the crawler to find them naturally!
    else:
        console.print("[red]❌ No sitemap found! Orphan analysis is impossible without a sitemap.[/red]")
        return
        
    db.add_to_queue([start_url])
    
    queue_size = db.get_queue_count()
    visited_size = len(db.get_all_visited())
    
    console.print(f"\n[green]🚀 Starting Orphan Hunter for {domain_name}[/green]")
    console.print(f"[dim]Current Queue: {queue_size} | Already Visited: {visited_size}[/dim]")

    if queue_size > 0:
        console.print(f"[cyan]⚙️  Launching Async Swarm (Concurrency: 100)...[/cyan]")
        engine = AsyncCrawlerEngine(db=db, start_url=start_url, base_domain=domain_name, limit=limit)
        engine.start()

    # 2. The Magic: Compare the tables!
    console.print("\n[cyan]🔍 Cross-referencing Sitemap vs Crawled Data...[/cyan]")
    
    orphans = db.get_orphan_urls()
    non_sitemap = db.get_non_sitemap_urls()
    
    # Format the output
    results = []
    for url in orphans:
        results.append({"URL": url, "Issue": "Orphan (In Sitemap, but not linked on site)"})
    for url in non_sitemap:
        results.append({"URL": url, "Issue": "Missing from Sitemap (Linked on site, but not in sitemap)"})
        
    if not results:
        console.print("[bold green]🎉 Perfect Architecture! The sitemap matches the website exactly.[/bold green]")
    else:
        df = pd.DataFrame(results)
        out_path = os.path.join(output_dir, f"{domain_name}_orphan_analysis.{'xlsx' if output_format == 'excel' else output_format}")
        if output_format == 'excel': df.to_excel(out_path, index=False)
        elif output_format == 'csv': df.to_csv(out_path, index=False)
        console.print(f"[bold red]⚠️ Found {len(results)} architecture issues! Saved to {out_path}[/bold red]")

    if use_cloud and drive:
        drive.upload_db(f"{domain_name}_orphans", db_path)

    if db.get_queue_count() == 0:
        if os.path.exists(db_path):
            del db
            if 'engine' in locals(): del engine
            if 'drive' in locals(): del drive
            gc.collect()
            time.sleep(0.5) 
            try:
                os.remove(db_path)
                console.print("[dim]🧹 Local cache cleared.[/dim]")
            except Exception:
                pass