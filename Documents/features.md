# 🛠️ How to Add Features

Welcome to the contributor's guide for RedScraping!

Because RedScraping is divided into two distinct engines, adding a feature depends on what you want to build:
URL Feature (scraping/url_features/): Extracts specific data from a provided list of URLs (e.g., scraping Schema markup, reading specific tags).

Crawler Module (scraping/crawler/): Spiders an entire domain to map data (e.g., finding all social media links across a website).
Here is the step-by-step process for adding both types of features.


## Scenario A: Adding a URL Feature

Example: Let's add a command to scrape schema (JSON-LD) from a list of URLs.

### Step 1: Create the Extractor File
Create a new file in redscraping_core/scraping/url_features/schema.py.
The easiest way to start is to copy an existing file (like titles.py or description.py) and modify it.

### Step 2: Write the Parsing Logic
Inside your new schema.py file, define your extraction function. The UrlEngine will pass either a BeautifulSoup object (is_selenium=False) or a Selenium WebDriver object (is_selenium=True).

```
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def extract_schema(source, is_selenium=False):
    """Extracts JSON-LD schema markup from the page."""
    schemas = []
    
    if is_selenium:
        elements = source.find_elements(By.CSS_SELECTOR, "script[type='application/ld+json']")
        schemas = [el.get_attribute("innerHTML").strip() for el in elements]
    else:
        elements = source.find_all("script", type="application/ld+json")
        schemas = [el.string.strip() for el in elements if el.string]
        
    return {"Schema": schemas if schemas else "No Schema Found"}

```

### Step 3: Update the Runner Function

1. In the same file, update the run_schema_scraper function. Since you copied this from titles.py, you only need to change a few lines:

2. Change the cache file name: cache_file = os.path.join(cache_dir, f"schema_{input_file...}.json")

3. Pass your new parser to the engine: data = engine.fetch(url, extract_schema)

4. Update the output file name: out_path = os.path.join(output_dir, f"{base_name}_schema.xlsx")

### Step 4: Register the CLI Command
Open redscraping_core/scraping/scrape_cmds.py and add your new Click command:

```
from .schema import run_schema_scraper

@click.command()
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv', 'json', 'txt']), default='excel')
@click.option('--restart', is_flag=True, help="Ignore cache and start from scratch")
def schema(input_file, output_format, restart):
    """Scrapes JSON-LD Schema markup from URLs."""
    run_schema_scraper(input_file, output_format, restart)

```

### Step 5: Add to Main CLI
Finally, open redscraping_core/cli.py, import your command, and add it to the main group:

```
from .scraping.scrape_cmds import schema

main_cli.add_command(schema)
```

<br>
## Scenario B: Adding a Crawler Module

Example: Let's add a crawler that finds all external social media links across an entire domain.

### Step 1: Update the Database Manager
Because the crawler is highly concurrent, it uses SQLite to prevent data loss. Open redscraping_core/scraping/crawler/db_manager.py.
Add a new table in init_db():

```
cursor.execute('''CREATE TABLE IF NOT EXISTS socials (social_url TEXT UNIQUE, source_url TEXT)''')
Add save and retrieve methods:
```
```
def save_socials(self, social_data):
    if not social_data: return
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT OR IGNORE INTO socials (social_url, source_url) VALUES (?, ?)', social_data)
        conn.commit()

def get_all_socials(self):
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT social_url, source_url FROM socials')
        return cursor.fetchall()
```

### Step 2: Create the Crawler File
Create redscraping_core/scraping/crawler/socials.py. Copy the boilerplate from emails.py or assets.py.
### Step 3: Write the Extraction Logic
Write a function that takes raw HTML and the current URL, and returns a list of tuples to be saved in the database.
```
from bs4 import BeautifulSoup

def extract_socials_from_html(html, current_url):
    soup = BeautifulSoup(html, 'html.parser')
    social_domains = ['twitter.com', 'facebook.com', 'linkedin.com', 'instagram.com']
    found_socials = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if any(domain in href for domain in social_domains):
            found_socials.add(href)
            
    return [(social, current_url) for social in found_socials]
```

### Step 4: Update the Runner Function
In your socials.py file, update the run_socials_crawler function:

Change the DB name: db_path = os.path.join(cache_dir, f"{domain_name}_socials.db")
Pass your extractor to the engine:
engine = AsyncCrawlerEngine(..., extractor_func=extract_socials_from_html)
Crucial Step: Temporarily override the engine's save method so it uses your new DB function:

```
original_save = db.save_emails
db.save_emails = db.save_socials # Route data to your new table
engine.start()
db.save_emails = original_save
Export the data using db.get_all_socials().
```

### Step 5: Register the Command
Open redscraping_core/scraping/crawl_cmds.py and add your command:

```
from .socials import run_socials_crawler

@click.command()
@click.argument('domain')
@click.option('--limit', type=int, default=0)
@click.option('--format', 'output_format', type=click.Choice(['excel', 'csv']), default='excel')
@click.option('--restart', is_flag=True)
def socials(domain, limit, output_format, restart):
    """Crawls a domain and extracts all social media links."""
    run_socials_crawler(domain, limit, output_format, restart)

```

### Step 6: Add to Main CLI
Open redscraping_core/cli.py, import your command, and add it:

```
from .scraping.crawl_cmds import socials

main_cli.add_command(socials)

```

## 💡 Best Practices for Contributors

1. Never bypass the Cache: Always ensure your feature checks .cache/ before running, and saves to it during execution. This is a core philosophy of RedScraping.

2. Use Rich for UI: Use from rich.console import Console for all print statements to maintain the beautiful, colorful CLI experience.

3. Respect the Engines: Do not write custom requests.get() loops. Always pass your logic through UrlEngine or AsyncCrawlerEngine so users benefit from the built-in Cloudflare bypass and stealth profiles.