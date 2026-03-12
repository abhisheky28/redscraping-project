# redscraping_core/scraping/crawler/domain_utils.py

import requests
from urllib.parse import urlparse
from rich.console import Console

console = Console()

def get_true_domain_info(user_input):
    """
    Takes any user input (nike.com, http://www.nike.com)
    Returns the True Start URL and the Clean Base Domain.
    """
    console.print(f"[dim]🔍 Resolving true URL for {user_input}...[/dim]")
    
    if not user_input.startswith(('http://', 'https://')):
        url = f"http://{user_input}"
    else:
        url = user_input
        
    try:
        # Ping the server and follow all redirects
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, allow_redirects=True)
        final_url = response.url
        
        # Extract the clean base domain (e.g., 'nike.com' from 'https://www.nike.com/shop/')
        parsed = urlparse(final_url)
        base_domain = parsed.netloc.replace("www.", "")
        
        console.print(f"[dim green]✅ Resolved to: {final_url} (Domain: {base_domain})[/dim green]")
        return final_url, base_domain
        
    except Exception:
        # Fallback if the site is completely down or blocking requests
        fallback_url = f"https://{user_input.replace('http://', '').replace('https://', '')}"
        fallback_domain = urlparse(fallback_url).netloc.replace("www.", "")
        console.print(f"[dim yellow]⚠️ Ping failed. Falling back to: {fallback_url}[/dim yellow]")
        return fallback_url, fallback_domain