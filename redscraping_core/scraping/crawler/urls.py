# redscraping_core/scraping/crawler/urls.py

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Confirm
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

def run_urls_crawler(domain, limit, output_format, restart):
    base_dir = os.getcwd()
    output_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, ".cache")
    
    # --- USE THE NEW DOMAIN RESOLVER ---
    start_url, domain_name = get_true_domain_info(domain)
    
    # --- UNIQUE DB NAME FOR THIS FEATURE ---
    db_path = os.path.join(cache_dir, f"{domain_name}_urls.db")

    if restart and os.path.exists(db_path):
        os.remove(db_path)
        console.print(f"[yellow]🔄 Restarting crawl for {domain_name}. Old local database cleared.[/yellow]")

    use_cloud = False
    drive = None
    if Confirm.ask("\n[bold cyan]☁️ Do you want to sync this crawl with your Google Drive to speed up future runs?[/bold cyan]"):
        use_cloud = True
        drive = DriveManager()
        if not restart and not os.path.exists(db_path):
            drive.download_db(f"{domain_name}_urls", db_path)
    else:
        console.print("[dim]Skipping Google Drive sync. Using local cache only.[/dim]\n")

    db = DBManager(db_path)
    
    if db.get_queue_count() == 0 and len(db.get_all_visited()) == 0:
        console.print("[cyan]🗺️ Hunting for Sitemaps...[/cyan]")
        sitemap_urls = get_sitemap_urls(start_url)
        if sitemap_urls:
            console.print(f"[green]✅ Found {len(sitemap_urls)} URLs in sitemap![/green]")
            db.add_to_queue(sitemap_urls)
        else:
            console.print("[dim]No sitemap found. Proceeding with standard discovery.[/dim]")
            
    db.add_to_queue([start_url])
    
    queue_size = db.get_queue_count()
    visited_size = len(db.get_all_visited())
    
    console.print(f"\n[green]🚀 Starting crawl for {domain_name}[/green]")
    console.print(f"[dim]Current Queue: {queue_size} | Already Visited: {visited_size}[/dim]")

    if queue_size == 0:
        console.print("[bold green]✅ Crawl is already complete![/bold green]")
    else:
        console.print(f"[cyan]⚙️  Launching Async Swarm (Concurrency: 100)...[/cyan]")
        # --- PASS BASE_DOMAIN TO THE ENGINE ---
        engine = AsyncCrawlerEngine(db=db, start_url=start_url, base_domain=domain_name, limit=limit)
        engine.start()

    console.print("\n[cyan]💾 Exporting results...[/cyan]")
    results = db.get_all_visited()
    
    if not results:
        console.print("[yellow]⚠️ No URLs found to export.[/yellow]")
        return

    df = pd.DataFrame(results, columns=['URL', 'Status Code', 'Method'])
    out_path = os.path.join(output_dir, f"{domain_name}_all_urls.{'xlsx' if output_format == 'excel' else output_format}")
    
    if output_format == 'excel': df.to_excel(out_path, index=False)
    elif output_format == 'csv': df.to_csv(out_path, index=False)
        
    console.print(f"[bold green]🎉 Done! Saved {len(results)} URLs to {out_path}[/bold green]")

    if use_cloud and drive:
        drive.upload_db(f"{domain_name}_urls", db_path)

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
            except Exception as e:
                console.print(f"[dim yellow]⚠️ Could not delete local cache: {e}[/dim yellow]")