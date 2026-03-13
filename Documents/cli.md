# 💻 CLI Commands Reference

RedScraping is a powerful command-line interface (CLI) tool. All commands start with the base keyword redscrape.

## The CLI is divided into four main categories:

1. Setup & Initialization
2. URL Scraping (List-based)
3. Domain Crawling (Spidering)
4. AI Automation

### 1. Setup & Initialization
These commands are used to configure your workspace, authenticate with Google, and prepare your stealth browser.

Command	Description	Example

1. redscrape init :- Generates the boilerplate project folder structure (input/, output/, config.py, scraper.py). 
```
Requires the --type flag.	

redscrape init --type sheets

redscrape init --type excel
```

2. redscrape setup-chrome :- Opens a fresh Chrome instance to create your persistent stealth profile. Log into Google/Cloudflare here.	
```
redscrape setup-chrome

redscrape setup-chrome --refresh
```

3. redscrape info :- Displays a quick-start guide and instructions on how to use the generated workspace.	
```
redscrape info
```


4. redscrape context :- Generates CONTEXT_FOR_AI.py. Feed this to ChatGPT/Claude so they understand the RedScraping library.	
```
redscrape context
```


### 2. URL Scraping (List-based)

These commands extract specific data points from a provided list of URLs.
Supported Input Formats

All scraping commands accept three types of inputs:
1. Text File: urls.txt (Must be placed in the input/ folder).
2. Excel File: data.xlsx (Must be in input/ and contain a column named URL).
3. Google Sheets: gsheet:SheetName/WorksheetName (Reads directly from your Google Drive).


#### Common Flags
1. --format [excel|csv|json|txt]: Choose the output format (Default: excel).
2. --restart: Ignores the local .cache and scrapes everything from scratch.

#### Scraping Commands
Command	Description	Example

1. headings	Scrapes all H1-H6 tags from the URLs.	redscrape headings urls.txt
2. titles	Scrapes the <title> tag.	redscrape titles gsheet:SEO/URLs
3. description	Scrapes the <meta name="description"> tag.	redscrape description data.xlsx
4. meta	Scrapes ALL meta tags (name, property, http-equiv).	redscrape meta urls.txt --format csv
5. href	Scrapes all links (<a> tags) and classifies them as Internal or External.	redscrape href urls.txt
6. elements	Scrapes text from a specific CSS selector. (Requires selector argument first).	redscrape elements ".price" urls.txt
7. text	Scrapes all visible, readable text and calculates the word count.	redscrape text gsheet:SEO/URLs
8. status	Checks HTTP status codes. Automatically uses Selenium to bypass Cloudflare 403/503 blocks.	redscrape status urls.txt
9. clean	Deletes the cache for a specific feature to free up space.	redscrape clean headings<br>redscrape clean all


### 3. Domain Crawling (Spidering)
Unlike URL scraping, Crawling commands take a domain name (e.g., example.com) and spider the entire website using a highly concurrent async engine (100 workers).

Note: All crawling commands will prompt you asking if you want to sync the SQLite cache to Google Drive.

#### Common Flags
1. --limit [INT]: Maximum number of pages to crawl. 0 means unlimited (Default: 0).
2. --format [excel|csv]: Choose the output format (Default: excel).
3. --restart: Deletes the local SQLite database and starts the crawl from page 1.

#### Crawling Commands
Command	Description	Example

1. urls	Maps the entire website, saving every internal URL and its status code.	redscrape urls nike.com
2. broken	Crawls the site specifically looking for 404s and broken links.	redscrape broken apple.com --limit 500
3. emails	Spiders the site and extracts every unique email address found in the HTML.	redscrape emails startup.io
4. assets	Catalogs all Images, CSS files, JavaScript files, and Videos across the domain.	redscrape assets example.com
5. orphans	Downloads the sitemap.xml and cross-references it against a live crawl to find Orphan pages.	redscrape orphans myblog.com

### 4. AI Automation
RedScraping integrates directly with Google's Gemini 2.5 Flash model to write custom Selenium automation scripts for you.

Command	Description	Example
1. ai-key set	Saves your Gemini API key to a local .env file.	      redscrape ai-key set AIzaSy...
2. ai-key show	Checks if you currently have an API key saved.	      redscrape ai-key show
3. ai-key reset	Deletes your saved API key.	                          redscrape ai-key reset
4. ai	Generates a custom Python scraper based on your prompt. Uses the --name flag to set the output filename.	                                                         redscrape ai "Go to amazon and scrape prices" --name amazon.py