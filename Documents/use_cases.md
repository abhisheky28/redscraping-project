# 💡 Real-World Use Cases

RedScraping is designed to solve complex data extraction and SEO auditing problems that traditional tools struggle with. By combining blazing-fast async requests with stealthy Selenium fallbacks and Google Workspace integration, it opens up entirely new workflows.

## Here are five common use cases where RedScraping shines.

### 1. The "Unblockable" SEO Audit (Bypassing Cloudflare)
The Problem: You need to audit the HTTP status codes and meta tags of 10,000 URLs for a client. However, the client's website is protected by aggressive Cloudflare Bot Management or Datadome, which blocks standard crawlers (like Screaming Frog or Python requests) with 403 Forbidden or 503 Service Unavailable errors.

The RedScraping Solution:
1. RedScraping's hybrid engine handles this automatically.
2. You put the 10,000 URLs in a Google Sheet.
3. You run redscrape status gsheet:ClientAudit/URLs.
4. RedScraping starts checking URLs concurrently using curl_cffi (impersonating Chrome 110).
5. When it hits a 403/503 block, it dynamically routes that specific URL to a background, headless Selenium instance using your persistent Chrome-Profile.
6. Selenium solves the JS challenge, reads the Network logs to get the true status code, and returns the result.

Result: A complete, 100% accurate audit without getting IP banned.


### 2. Massive E-Commerce Crawls (With Cloud Sync)
The Problem: You are crawling a massive e-commerce site (e.g., 500,000 pages) to map its architecture and find broken links. Your laptop needs to restart for an update, or your internet connection drops halfway through the 12-hour crawl. You lose all your progress.

The RedScraping Solution:
1. RedScraping uses SQLite databases to cache every single page visited.
2. You run redscrape urls massive-store.com.
3. The CLI asks: "Do you want to sync this crawl with your Google Drive?" You select Yes.
4. RedScraping crawls at 100 pages per second.
5. Your computer crashes at page 250,000.
6. You open your laptop the next day, run the exact same command, and RedScraping downloads the SQLite database from your Google 7. Drive, resuming instantly from page 250,001.

Result: Zero data loss on massive, multi-day crawls.


### 3. Finding "Orphan" Pages for Content Pruning
The Problem: A website has been running for 10 years. The marketing team wants to know which pages exist in the sitemap.xml but are never actually linked to from anywhere on the live website (Orphan pages). These pages waste crawl budget and confuse users.

The RedScraping Solution:
1. RedScraping has a dedicated architecture analysis command.
2. You run redscrape orphans old-blog.com.
3. RedScraping automatically downloads and parses the sitemap.xml.
4. It then launches a full spider crawl starting from the homepage, mapping every internal link it can find.
5. Finally, it cross-references the two datasets using SQL.
6. It outputs an Excel file detailing exactly which URLs are in the sitemap but missing from the site, and vice versa.

Result: Actionable data for immediate SEO architecture improvements.


### 4. Automated Lead Generation (Email Hunting)
The Problem: You have a list of 50 target company domains. You need to find contact email addresses for all of them to build a cold outreach campaign, but manually clicking through "Contact Us" and "About" pages takes hours.

The RedScraping Solution:
1. RedScraping's crawler can hunt for specific data types across entire domains.
2. You write a simple bash script to loop through your 50 domains.
3. For each domain, it runs redscrape emails company.com --limit 50.
4. RedScraping spiders the first 50 pages of each website, using Regex to extract every unique email address it finds in the HTML.
5. It automatically filters out image files (e.g., logo@2x.png) and saves the clean emails to a CSV.

Result: A highly targeted lead list generated in minutes while you drink coffee.


5. AI-Powered Custom Scraping (No Code Required)
The Problem: You need to scrape the pricing data from a specific competitor's website every morning. The site requires you to log in first, and the pricing data is hidden inside a complex React dropdown menu. Standard CLI commands won't work; you need a custom Selenium script, but you don't know how to write Python.

The RedScraping Solution:
1. RedScraping integrates with Google's Gemini 2.5 Flash to write the code for you.
2. You run redscrape setup-chrome, open the competitor's site, and log in manually. Your session cookies are now saved in the Chrome-Profile.
3. You run redscrape init --type excel to set up your workspace.
4. You run: redscrape ai "Go to competitor.com/pricing, click the 'Enterprise' dropdown, and scrape the monthly price into my data.xlsx file." --name daily_price.py
4. Gemini generates a perfect, custom Selenium script that utilizes your pre-authenticated Chrome profile.
5. You run python daily_price.py every morning.

Result: Complex, authenticated web scraping achieved with zero coding knowledge.