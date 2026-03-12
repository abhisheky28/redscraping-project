# redscraping_core/scraping/crawler/emails.py

import os
import pandas as pd
import requests
import re
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

def extract_emails_from_html(html, current_url):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found_emails = re.findall(email_pattern, html)
    clean_emails = set()
    for email in found_emails:
        email = email.lower()
        if not email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
            clean_emails.add(email)
    return [(email, current_url) for email in clean_emails]

def run_emails_crawler(domain, limit, output_format, restart):
    base_dir = os.getcwd()
    output_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, ".cache")
    
    start_url, domain_name = get_true_domain_info(domain)
    db_path = os.path.join(cache_dir, f"{domain_name}_emails.db")

    if restart and os.path.exists(db_path):
        os.remove(db_path)
        console.print(f"[yellow]🔄 Restarting crawl for {domain_name}. Old local database cleared.[/yellow]")

    use_cloud = False
    drive = None
    if Confirm.ask("\n[bold cyan]☁️ Do you want to sync this crawl with your Google Drive to speed up future runs?[/bold cyan]"):
        use_cloud = True
        drive = DriveManager()
        if not restart and not os.path.exists(db_path):
            drive.download_db(f"{domain_name}_emails", db_path)
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
    
    console.print(f"\n[green]🚀 Starting Email Hunter for {domain_name}[/green]")
    console.print(f"[dim]Current Queue: {queue_size} | Already Visited: {visited_size}[/dim]")

    if queue_size == 0:
        console.print("[bold green]✅ Crawl is already complete![/bold green]")
    else:
        console.print(f"[cyan]⚙️  Launching Async Swarm (Concurrency: 100)...[/cyan]")
        engine = AsyncCrawlerEngine(db=db, start_url=start_url, base_domain=domain_name, limit=limit, extractor_func=extract_emails_from_html)
        engine.start()

    console.print("\n[cyan]🔍 Compiling extracted emails...[/cyan]")
    all_emails = db.get_all_emails()
    
    if not all_emails:
        console.print("[yellow]⚠️ No emails found on this domain.[/yellow]")
    else:
        df = pd.DataFrame(all_emails, columns=['Email Address', 'Found On URL'])
        out_path = os.path.join(output_dir, f"{domain_name}_emails.{'xlsx' if output_format == 'excel' else output_format}")
        if output_format == 'excel': df.to_excel(out_path, index=False)
        elif output_format == 'csv': df.to_csv(out_path, index=False)
        console.print(f"[bold green]🎉 Success! Found {len(all_emails)} unique emails. Saved to {out_path}[/bold green]")

    if use_cloud and drive:
        drive.upload_db(f"{domain_name}_emails", db_path)

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