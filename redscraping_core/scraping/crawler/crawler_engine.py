# redscraping_core/scraping/crawler/crawler_engine.py

import asyncio
import os
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ...utils.chrome_setup import setup_master_profile

console = Console()

class AsyncCrawlerEngine:
    def __init__(self, db, start_url, base_domain, limit=0, concurrency=100, extractor_func=None):
        self.db = db
        self.start_url = start_url
        self.base_domain = base_domain
        self.limit = limit
        self.concurrency = concurrency
        self.extractor_func = extractor_func
        
        # --- THE RAM PROTECTOR ---
        # This ensures a maximum of 3 Selenium browsers can open at the exact same time.
        self.selenium_semaphore = asyncio.Semaphore(3)

    def clean_and_filter_url(self, href, current_url):
        if not href or href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
            return None
            
        absolute_url = urljoin(current_url, href.strip())
        parsed = urlparse(absolute_url)
        
        target_domain = parsed.netloc.replace("www.", "")
        if target_domain != self.base_domain:
            return None
            
        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        return clean_url

    def fetch_with_selenium(self, url):
        """Synchronous function to run Selenium in a background thread."""
        profile_path = os.path.join(os.getcwd(), "Chrome-Profile")
        if not os.path.exists(profile_path):
            setup_master_profile()

        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            html = driver.page_source
            # Selenium doesn't give status codes easily, so if it loads, we assume 200
            return html, 200 
        except Exception:
            return "", 500
        finally:
            driver.quit()

    async def fetch_and_parse(self, session, url):
        """Tries curl_cffi first. Falls back to Selenium if blocked."""
        html = ""
        status = 500
        method_used = "curl_cffi"
        
        try:
            # 1. Try the fast Chrome impersonator
            response = await session.get(url, timeout=10, allow_redirects=True, impersonate="chrome110")
            status = response.status_code
            
            # 2. If blocked by Cloudflare/Bot Protection, use Selenium!
            if status in [403, 503, 400]:
                method_used = "Selenium (Bypass)"
                # Safely run Selenium in a background thread, limited to 3 at a time
                async with self.selenium_semaphore:
                    html, status = await asyncio.to_thread(self.fetch_with_selenium, url)
            else:
                html = response.text
                
        except Exception:
            status = 500
            method_used = "Error"

        # 3. Parse the HTML (regardless of which method got it)
        new_links = set()
        extracted_data = []
        
        if status == 200 and html:
            soup = BeautifulSoup(html, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                clean_link = self.clean_and_filter_url(a_tag['href'], url)
                if clean_link:
                    new_links.add(clean_link)
                    
            if self.extractor_func:
                extracted_data = self.extractor_func(html, url)
                
        return url, status, list(new_links), method_used, extracted_data

    async def run_batch(self, urls):
        async with AsyncSession() as session:
            tasks = [self.fetch_and_parse(session, url) for url in urls]
            return await asyncio.gather(*tasks)

    def start(self):
        asyncio.run(self._async_start())

    async def _async_start(self):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task_id = progress.add_task("[cyan]Crawling...", total=None)
            
            while True:
                visited_count = len(self.db.get_all_visited())
                if self.limit > 0 and visited_count >= self.limit:
                    console.print(f"\n[yellow]🛑 Reached the limit of {self.limit} pages.[/yellow]")
                    break
                    
                batch = self.db.get_next_batch(batch_size=self.concurrency)
                
                if not batch:
                    progress.update(task_id, description=f"[bold green]✅ Finished! (Visited: {visited_count} | Queue: 0)[/bold green]")
                    break 
                    
                progress.update(task_id, description=f"[cyan]Crawling... (Visited: {visited_count} | Queue: {self.db.get_queue_count()})")
                results = await self.run_batch(batch)
                
                all_new_links = []
                for url, status, new_links, method, extracted_data in results:
                    self.db.mark_as_visited(url, status, method)
                    all_new_links.extend(new_links)
                    if extracted_data:
                        self.db.save_emails(extracted_data)
                        
                self.db.add_to_queue(all_new_links)