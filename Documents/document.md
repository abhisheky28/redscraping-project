# 🕸️ RedScraping Documentation
## The Ultimate Open-Source SEO Spider & Automation Framework.

RedScraping is a powerful, stealthy, and AI-integrated CLI tool and Python library designed for SEO professionals, data engineers, and web scrapers. It combines the speed of asynchronous requests with the stealth of Selenium to bypass anti-bot protections (like Cloudflare), all while seamlessly integrating with Google Workspace (Sheets & Drive).

---

# ✨ Key Features

- 🚀 **Async + Stealth Engine:** Uses `curl_cffi` for blazing-fast async requests, automatically falling back to a stealthy Selenium Chrome profile if Cloudflare or bot-protection is detected.

- 📊 **Google Workspace Native:** Read inputs directly from Google Sheets, write outputs to Sheets, and backup massive SQLite crawl databases to Google Drive.

- 🕷️ **Deep SEO Crawling:** Map entire domains, find broken links, extract assets (JS/CSS/Images), hunt for emails, and cross-reference sitemaps to find orphan pages.

- 🤖 **AI Code Generation:** Built-in integration with Google's Gemini 2.5 Flash to automatically write custom Selenium scraping scripts based on your prompts.

---

# 📦 1. Installation

RedScraping requires **Python 3.8+**.

``` 
# Install via pip (assuming you have built the package)
pip install redscraping

```

Note: RedScraping uses Google Chrome for its stealth engine. Ensure you have Chrome installed on your machine.

🚀 2. Quick Start & Setup

Before scraping, you need to initialize your project workspace and set up your stealth Chrome profile.

Step 1: Initialize the Project

Navigate to your desired folder and run the init command. This creates the necessary folder structure (input/, output/, .cache/) and boilerplate code.

redscrape init --type sheets
# OR
redscrape init --type excel
Step 2: Setup Stealth Chrome Profile

RedScraping uses a persistent Chrome profile to store cookies and bypass captchas. Run this command, log into any necessary accounts (like Google), and close the browser.

redscrape setup-chrome
🎯 3. URL Feature Scraping

Extract specific data points from a list of URLs.

Input Formats

RedScraping commands accept three types of inputs:

Text File: urls.txt (placed in the input/ folder)

Excel File: data.xlsx (must have a column named URL)

Google Sheets: gsheet:SheetName/WorksheetName (Requires Google Auth)

Commands

All commands support --format (excel, csv, json, txt) and --restart (to clear cache).

Extract Headings (H1-H6)
redscrape headings urls.txt --format csv
Extract Meta Titles & Descriptions
redscrape titles gsheet:MySEOProject/URLs
redscrape description data.xlsx
Extract All Meta Tags
redscrape meta urls.txt
Extract Links (Internal/External Classification)
redscrape href urls.txt
Extract Specific CSS Elements
redscrape elements ".product-price" urls.txt
Extract Visible Text (Word Count & Content)
redscrape text urls.txt
Check Status Codes (Cloudflare Bypass)

Uses Network logs to bypass 403/503 blocks.

redscrape status urls.txt
🕷️ 4. Site Crawling (The Spider)

RedScraping includes a highly concurrent (100 workers) async crawler. It uses SQLite to cache progress locally and can sync to Google Drive for massive crawls.

Map All Internal URLs
redscrape urls example.com
Find Broken Links (404s)
redscrape broken example.com
Extract All Emails
redscrape emails example.com
Audit Assets (Images, JS, CSS, Video)
redscrape assets example.com
Find Orphan Pages

Downloads the sitemap.xml and cross-references it against a live crawl to find pages that exist but aren't linked anywhere.

redscrape orphans example.com

💡 Tip: Use --limit 500 to restrict the crawl to a specific number of pages.

🤖 5. AI Automation (Gemini Integration)

RedScraping can write custom Selenium scripts for you using Google's Gemini 2.5 Flash model.

Setup API Key

Get a free key from Google AI Studio and save it to RedScraping:

redscrape ai-key set YOUR_GEMINI_API_KEY
Generate a Custom Scraper

Tell the AI what you want to scrape. It will use your local config.py and stealth Chrome profile automatically.

redscrape ai "Go to amazon.com, search for laptops, and scrape the titles and prices of the first page into a CSV." --name amazon_scraper.py
Generate AI Context (For ChatGPT/Claude)

If you prefer using ChatGPT or Claude to write your code, generate a context file. Give this file to your LLM so it understands how the RedScraping library works.

redscrape context

(This generates CONTEXT_FOR_AI.py)

⚙️ 6. Advanced Architecture & Integrations
The Hybrid Engine (curl_cffi + Selenium)

RedScraping's crawler is designed to never be blocked.

It first attempts to fetch pages using curl_cffi (impersonating Chrome 110). This allows for massive concurrency (100+ pages/sec).

If it detects a 403, 503, or Cloudflare challenge, it dynamically routes that specific URL to a background headless Selenium instance to solve the challenge, extract the HTML, and return it to the async loop.

Google Workspace Integration

When you run:

redscrape init --type sheets

RedScraping will prompt you to log into your Google Account. It generates a token.json file locally.

Sheets

Allows you to use:

gsheet:DocName/TabName

as an input for any scraping command.

Drive

When running large crawls (redscrape urls), the CLI will ask if you want to sync to Google Drive. This uploads the SQLite .db file to a folder called RedScraping_Cache, allowing you to pause a crawl on one computer and resume it on another.

Cache Management

RedScraping caches all URL scraping and crawling to prevent data loss if your internet drops.

To clean your cache:

redscrape clean headings  # Cleans heading cache
redscrape clean all       # Cleans all URL scraping cache
🤝 Contributing

RedScraping is open-source! We welcome pull requests for:

New URL feature extractors (e.g., Schema markup extractor)

New crawler modules

Bug fixes and documentation improvements

💡 How to host this documentation

If you want to turn this into a beautiful website (like standard open-source tools), I highly recommend using MkDocs with the Material theme.

pip install mkdocs-material
mkdocs new my-project