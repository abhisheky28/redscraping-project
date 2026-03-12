# redscraping_core/scraping/crawler/assets.py

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Confirm
from urllib.parse import urlparse, urljoin
import gc
import time

from .db_manager import DBManager
from .crawler_engine import AsyncCrawlerEngine
from .drive_manager import DriveManager
from .domain_utils import get_true_domain_info

console = Console()

def extract_assets_from_html(html, current_url):
    """Extracts Images, Scripts, Stylesheets, and Videos."""
    soup = BeautifulSoup(html, 'html.parser')
    assets = []
    
    # Images
    for img in soup.find_all('img', src=True):
        assets.append((urljoin(current_url, img['src']), 'Image', current_url))
    # Scripts
    for script in soup.find_all('script', src=True):
        assets.append((urljoin(current_url, script['src']), 'JavaScript', current_url))
    # Stylesheets
    for link in soup.find_all('link', rel='stylesheet', href=True):
        assets.append((urljoin(current_url, link['href']), 'CSS', current_url))
    # Videos
    for video in soup.find_all(['video', 'source'], src=True):
        assets.append((urljoin(current_url, video['src']), 'Video', current_url))
        
    return assets

def run_assets_crawler(domain, limit, output_format, restart):
    base_dir = os.getcwd()
    output_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, ".cache")
    
    start_url, domain_name = get_true_domain_info(domain)
    db_path = os.path.join(cache_dir, f"{domain_name}_assets.db")

    if restart and os.path.exists(db_path):
        os.remove(db_path)
        console.print(f"[yellow]🔄 Restarting crawl for {domain_name}. Old local database cleared.[/yellow]")

    use_cloud = False
    drive = None
    if Confirm.ask("\n[bold cyan]☁️ Do you want to sync this crawl with your Google Drive to speed up future runs?[/bold cyan]"):
        use_cloud = True
        drive = DriveManager()
        if not restart and not os.path.exists(db_path):
            drive.download_db(f"{domain_name}_assets", db_path)
    else:
        console.print("[dim]Skipping Google Drive sync. Using local cache only.[/dim]\n")

    db = DBManager(db_path)
    db.add_to_queue([start_url])
    
    queue_size = db.get_queue_count()
    visited_size = len(db.get_all_visited())
    
    console.print(f"\n[green]🚀 Starting Asset Auditor for {domain_name}[/green]")
    console.print(f"[dim]Current Queue: {queue_size} | Already Visited: {visited_size}[/dim]")

    if queue_size > 0:
        console.print(f"[cyan]⚙️  Launching Async Swarm (Concurrency: 100)...[/cyan]")
        # Pass the asset extractor to the engine!
        engine = AsyncCrawlerEngine(db=db, start_url=start_url, base_domain=domain_name, limit=limit, extractor_func=extract_assets_from_html)
        
        # We need to slightly modify how the engine saves data for this specific run
        # Since the engine calls db.save_emails by default, we temporarily override it in Python
        original_save = db.save_emails
        db.save_emails = db.save_assets 
        engine.start()
        db.save_emails = original_save # Put it back

    console.print("\n[cyan]🔍 Compiling extracted assets...[/cyan]")
    all_assets = db.get_all_assets()
    
    if not all_assets:
        console.print("[yellow]⚠️ No assets found on this domain.[/yellow]")
    else:
        df = pd.DataFrame(all_assets, columns=['Asset URL', 'Asset Type', 'Found On URL'])
        out_path = os.path.join(output_dir, f"{domain_name}_assets.{'xlsx' if output_format == 'excel' else output_format}")
        if output_format == 'excel': df.to_excel(out_path, index=False)
        elif output_format == 'csv': df.to_csv(out_path, index=False)
        console.print(f"[bold green]🎉 Success! Found {len(all_assets)} assets. Saved to {out_path}[/bold green]")

    if use_cloud and drive:
        drive.upload_db(f"{domain_name}_assets", db_path)

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