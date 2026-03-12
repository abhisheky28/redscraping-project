# redscraping_core/scraping/url_features/status_code.py

import os
import json
import pandas as pd
import gspread
import requests
from google.oauth2.credentials import Credentials
from rich.console import Console
from rich.progress import track
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ...utils.gcp_setup import setup_gcp_auth
from ...utils.chrome_setup import setup_master_profile

console = Console()

# ==================================================================
# THE SELENIUM NETWORK LOG TRICK
# ==================================================================
def get_selenium_status(url):
    """Uses Selenium to bypass Cloudflare and reads Network logs for the status code."""
    profile_path = os.path.join(os.getcwd(), "Chrome-Profile")
    if not os.path.exists(profile_path):
        setup_master_profile()

    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--headless=new")
    
    # --- THE MAGIC LINE ---
    # This tells Chrome to record the F12 Network Tab logs in the background
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        final_url = driver.current_url
        status_code = "Unknown"
        
        # Dig through the network logs to find the main document's status code
        logs = driver.get_log('performance')
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if log['method'] == 'Network.responseReceived':
                response = log['params']['response']
                # If the log matches the URL we ended up on, grab its status!
                if response['url'] == final_url or response['url'] == url:
                    status_code = response['status']
                    break
                    
        return status_code, final_url
    except Exception as e:
        return "Error", url
    finally:
        driver.quit()

# ==================================================================
# THE MAIN CHECKER
# ==================================================================
def check_status(url):
    """Tries requests first. If blocked by Cloudflare (403/503), uses Selenium."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        is_redirect = len(response.history) > 0
        original_status = response.history[0].status_code if is_redirect else response.status_code
        final_status = response.status_code
        
        # --- CLOUDFLARE BYPASS LOGIC ---
        if final_status in [403, 503]:
            console.print(f"[dim yellow]🛡️ Blocked by Cloudflare ({final_status}). Bypassing with Selenium: {url}[/dim yellow]")
            sel_status, sel_final_url = get_selenium_status(url)
            
            return {
                "Status Code": sel_status,
                "Final Status": sel_status,
                "Final URL": sel_final_url,
                "Redirected": "Yes" if sel_final_url != url else "No",
                "Method": "Selenium (Bypass)"
            }
        # -------------------------------

        console.print(f"[dim green]⚡ Fast Check: {url}[/dim green]")
        return {
            "Status Code": original_status,
            "Final Status": final_status,
            "Final URL": response.url,
            "Redirected": "Yes" if is_redirect else "No",
            "Method": "Requests"
        }
        
    except requests.exceptions.Timeout:
        return {"Status Code": "Timeout", "Final Status": "Timeout", "Final URL": url, "Redirected": "No", "Method": "Requests"}
    except Exception as e:
        return {"Status Code": "Error", "Final Status": "Error", "Final URL": url, "Redirected": "No", "Method": "Requests"}

def run_status_scraper(input_file, output_format, restart):
    base_dir = os.getcwd()
    urls = []

    # (INPUT DISPATCHER LOGIC REMAINS THE SAME)
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

    if not urls:
        console.print("[yellow]⚠️ No URLs found in the input source.[/yellow]")
        return

    output_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, ".cache")
    cache_file = os.path.join(cache_dir, f"status_{input_file.replace('/', '_').replace(':', '_')}.json")
    
    results, completed_urls = [], set()

    if restart and os.path.exists(cache_file): os.remove(cache_file)
    elif os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
            results, completed_urls = cache.get("results", []), set(cache.get("completed_urls", []))
        console.print(f"[green]♻️ Resuming from cache. {len(completed_urls)} URLs done.[/green]")

    urls_to_scrape = [u for u in urls if u not in completed_urls]
    if not urls_to_scrape:
        console.print("[bold green]✅ All URLs are already checked![/bold green]")
        return

    for url in track(urls_to_scrape, description="[cyan]Checking Status Codes..."):
        data = check_status(url)
        row = {"Original URL": url, **data}
        results.append(row)
        completed_urls.add(url)
        
        with open(cache_file, 'w') as f:
            json.dump({"completed_urls": list(completed_urls), "results": results}, f)

    # OUTPUT SAVING LOGIC
    base_name = os.path.splitext(input_file)[0].replace("gsheet:", "").replace("/", "_")
    out_path = os.path.join(output_dir, f"{base_name}_status.{'xlsx' if output_format == 'excel' else output_format}")
    
    df = pd.DataFrame(results)
    
    if output_format in ['excel', 'csv']:
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
                f.write(f"{res.get('Original URL')} -> [{res.get('Status Code')}] ({res.get('Method')})\n")
    
    console.print(f"[bold green]🎉 Done! Saved to {out_path}[/bold green]")
    if os.path.exists(cache_file): os.remove(cache_file)