# redscraping_core/scraping/url_features/titles.py

import os
import json
import pandas as pd
import gspread
from google.oauth2.credentials import Credentials
from rich.console import Console
from rich.progress import track

from .engine import UrlEngine
from ...utils.gcp_setup import setup_gcp_auth

console = Console()

def extract_description(source, is_selenium=False):
    """Extracts the <meta name="description"> tag."""
    desc = "Missing Description"
    if is_selenium:
        try:
            el = source.find_element(By.CSS_SELECTOR, "meta[name='description']")
            desc = el.get_attribute("content")
        except:
            pass
    else:
        el = source.find("meta", attrs={"name": "description"})
        if el and el.get("content"):
            desc = el["content"]
            
    return {"Description": desc.strip()}

def run_description_scraper(input_file, output_format, restart):
    base_dir = os.getcwd()
    urls = []

    # ==================================================================
    # INPUT DISPATCHER LOGIC
    # ==================================================================
    try:
        if input_file.startswith("gsheet:"):
            console.print("[dim]Detected Google Sheets input...[/dim]")
            setup_gcp_auth()
            parts = input_file.replace("gsheet:", "").split('/')
            if len(parts) != 2:
                console.print("[red]❌ Invalid Google Sheet format. Use 'gsheet:SheetName/WorksheetName'[/red]")
                return
            sheet_name, worksheet_name = parts
            scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_authorized_user_file('token.json', scopes)
            gc = gspread.authorize(creds)
            sheet = gc.open(sheet_name).worksheet(worksheet_name)
            urls = sheet.col_values(1)[1:]
            console.print(f"[green]✅ Loaded {len(urls)} URLs from Google Sheet '{sheet_name}/{worksheet_name}'[/green]")

        elif input_file.endswith((".xlsx", ".xls")):
            input_path = os.path.join(base_dir, "input", input_file)
            if not os.path.exists(input_path):
                console.print(f"[red]❌ Excel file not found: {input_path}[/red]")
                return
            df = pd.read_excel(input_path)
            if 'URL' not in df.columns:
                console.print("[red]❌ Excel file must contain a column named 'URL'[/red]")
                return
            urls = df['URL'].dropna().tolist()
            console.print(f"[green]✅ Loaded {len(urls)} URLs from '{input_file}'[/green]")

        else:
            input_path = os.path.join(base_dir, "input", input_file)
            if not os.path.exists(input_path):
                console.print(f"[red]❌ TXT file not found: {input_path}[/red]")
                return
            with open(input_path, 'r') as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]
            console.print(f"[green]✅ Loaded {len(urls)} URLs from '{input_file}'[/green]")

    except Exception as e:
        console.print(f"[red]❌ Failed to read input: {e}[/red]")
        return
    # ==================================================================

    if not urls:
        console.print("[yellow]⚠️ No URLs found in the input source.[/yellow]")
        return

    output_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, ".cache")
    cache_file = os.path.join(cache_dir, f"description_{input_file.replace('/', '_').replace(':', '_')}.json")
    results, completed_urls = [], set()

    if restart and os.path.exists(cache_file): os.remove(cache_file)
    elif os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
            results, completed_urls = cache.get("results", []), set(cache.get("completed_urls", []))
        console.print(f"[green]♻️ Resuming from cache. {len(completed_urls)} URLs done.[/green]")

    urls_to_scrape = [u for u in urls if u not in completed_urls]
    if not urls_to_scrape:
        console.print("[bold green]✅ All URLs are already scraped![/bold green]")
        return

    engine = UrlEngine()
    try:
        for url in track(urls_to_scrape, description="[cyan]Scraping Descriptions..."):
            data = engine.fetch(url, extract_description)
            row = {"URL": url, **data}
            results.append(row)
            completed_urls.add(url)
            with open(cache_file, 'w') as f:
                json.dump({"completed_urls": list(completed_urls), "results": results}, f)
    finally:
        engine.close()

    # ==================================================================
    # OUTPUT SAVING LOGIC
    # ==================================================================
    base_name = os.path.splitext(input_file)[0].replace("gsheet:", "").replace("/", "_")
    out_path = os.path.join(output_dir, f"{base_name}_description.{'xlsx' if output_format == 'excel' else output_format}")
    
    df = pd.DataFrame(results)
    
    if output_format == 'excel':
        df.to_excel(out_path, index=False)
    elif output_format == 'csv':
        df.to_csv(out_path, index=False)
    elif output_format == 'json':
        with open(out_path, 'w') as f:
            json.dump(results, f, indent=4)
    elif output_format == 'txt':
        with open(out_path, 'w', encoding='utf-8') as f:
            for res in results:
                f.write(f"{res.get('Description', '')}\n")
    
    console.print(f"[bold green]🎉 Done! Saved to {out_path}[/bold green]")
    if os.path.exists(cache_file): os.remove(cache_file)