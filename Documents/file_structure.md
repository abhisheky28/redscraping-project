# 📁 File Structure

Understanding the file structure of RedScraping is crucial whether you are a user setting up your first scraping project or a developer looking to contribute to the open-source core.

### This document is divided into two parts:
1. User Workspace Structure: The folders and files generated on your machine when you use the tool.
2. Source Code Architecture: The internal structure of the RedScraping Python package.

## 1. User Workspace Structure
When you run redscrape init --type sheets (or excel), RedScraping generates a boilerplate project in your current directory. This keeps your inputs, outputs, and configurations neatly organized.

```
your-project-folder/
│
├── input/                  # 📥 Put your input files here (urls.txt, data.xlsx)
├── output/                 # 📤 Scraped data and crawl reports are saved here
├── .cache/                 # ⚙️ Hidden folder storing JSON caches and SQLite DBs
│
├── Chrome-Profile/         # 🕵️ The persistent stealth Chrome profile (auto-generated)
├── token.json              # 🔑 Google OAuth token (generated after login)
├── .env                    # 🔐 Stores your Gemini API key (if configured)
│
├── config.py               # 🛠️ Global settings (User-Agents, Search URLs, Paths)
├── scraper.py              # 🐍 Your main custom scraping script (Boilerplate)
├── CONTEXT_FOR_AI.py       # 🤖 Give this to ChatGPT/Claude to help write your scraper
└── data.xlsx               # 📊 Template Excel file (if initialized with --type excel)

```

### Key Workspace Files:
scraper.py: This is where you write your custom Selenium logic. It comes pre-configured with Google Sheets/Excel connections and stealth browser initialization.
Chrome-Profile/: Do not delete this unless you want to reset your browser fingerprints and logins. It allows the scraper to bypass captchas by acting like a real user.
.cache/: RedScraping caches everything. If your internet drops during a 10,000 URL crawl, it resumes exactly where it left off using the SQLite databases stored here.


## 2. Source Code Architecture (For Contributors)
If you are cloning the RedScraping repository to contribute, here is how the core engine is organized. The project follows a modular design, separating CLI commands, utility functions, and scraping engines.

```
redscraping_core/
│
├── cli.py                  # 🚀 Main entry point. Registers all Click command groups.
├── __init__.py
│
├── utils/                  # 🛠️ Core utilities and setup scripts
│   ├── setup_cmds.py       # CLI commands for init, info, and context
│   ├── project_generator.py# Logic for creating the User Workspace
│   ├── templates.py        # String templates for boilerplate code
│   ├── chrome_setup.py     # Logic for building the Master Chrome Profile
│   ├── gcp_setup.py        # Google Cloud OAuth flow
│   ├── auth_config.py      # GCP Client ID and Secrets
│   └── preflight.py        # Ensures folders exist before commands run
│
├── scraping/               # 🕷️ The heart of the framework
│   │
│   ├── url_features/       # 📄 Module for scraping specific data from lists of URLs
│   │   ├── scrape_cmds.py  # CLI commands (headings, titles, href, etc.)
│   │   ├── engine.py       # UrlEngine: Requests + Selenium fallback logic
│   │   ├── headings.py     # H1-H6 extractor
│   │   ├── href.py         # Link extractor (Internal/External logic)
│   │   ├── status_code.py  # Network log Cloudflare bypass logic
│   │   └── ... (other feature extractors)
│   │
│   ├── crawler/            # 🕸️ Module for deep domain crawling (The Spider)
│   │   ├── crawl_cmds.py   # CLI commands (urls, broken, orphans, etc.)
│   │   ├── crawler_engine.py # AsyncCrawlerEngine: curl_cffi + Asyncio + Selenium
│   │   ├── db_manager.py   # SQLite manager for massive crawls
│   │   ├── drive_manager.py# Google Drive sync for SQLite databases
│   │   ├── domain_utils.py # URL resolution and cleaning
│   │   ├── orphans.py      # Sitemap vs Crawl cross-referencing
│   │   └── ... (other crawler modules)
│   │
│   └── ai/                 # 🤖 Module for Gemini AI integration
│       ├── ai_cmds.py      # CLI commands (ai, ai-key)
│       ├── ai_generator.py # Gemini 2.5 Flash prompt and generation logic
│       └── key_manager.py  # .env key storage logic
│
├── setup.py                # 📦 Pip package configuration and dependencies
└── requirements.txt        # 📚 List of required Python packages

```

### Architecture Highlights:
1. Separation of Engines: Notice that url_features uses a synchronous UrlEngine (Requests + Selenium), while crawler uses a highly concurrent AsyncCrawlerEngine (curl_cffi + Asyncio + Selenium Semaphore).

2. Click CLI: Every folder has a *_cmds.py file. This is where the Click CLI commands are defined before being imported into the main cli.py.
