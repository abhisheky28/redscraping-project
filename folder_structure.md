```mermaid
graph TD
%% Main Entry Point
    User((👤 User CLI)) --> CLI[🚀 cli.py Master Hub]

%% Routing from CLI
    CLI --> Utils[🛠️ utils/ <br> Setup & Config]
    CLI --> Scraping[🕷️ scraping/ <br> Core Engines]

%% Utils Subgraph
    subgraph UtilsModule["⚙️ Utils Module"]
        Utils --> SetupCmds[setup_cmds.py]
        SetupCmds --> Chrome[chrome_setup.py <br> Stealth Profile]
        SetupCmds --> ProjGen[project_generator.py <br> Workspace Init]
        ProjGen --> GCP[gcp_setup.py <br> Google Auth]
    end

%% Scraping Subgraph
    subgraph ScrapingModule["🕷️ Scraping Module"]
        Scraping --> URLCmds[scrape_cmds.py]
        Scraping --> CrawlCmds[crawl_cmds.py]
        Scraping --> AICmds[ai/ai_cmds.py]

%% URL Features
        URLCmds --> URLEngine{engine.py <br> BS4 + Selenium}
        URLEngine --> Extractors[Headings, Titles,<br> Meta, Href, Elements]

%% Crawler Engine
        CrawlCmds --> CrawlEngine{crawler_engine.py <br> Async Swarm}
        CrawlEngine <--> DB[(db_manager.py <br> SQLite Cache)]
        DB <--> Drive[drive_manager.py <br> Google Drive Sync]
        CrawlEngine --> Spiders[URLs, Broken Links,<br> Emails, Assets]

%% AI Module
        AICmds --> AIGen{ai_generator.py <br> Gemini 2.5 Flash}
        AIGen <--> KeyMgr[key_manager.py <br> .env Storage]
    end

%% Styling
    classDef core fill:#1a1a2e,stroke:#0f3460,stroke-width:3px,color:#fff,font-weight:bold;
    classDef engine fill:#e94560,stroke:#c62828,stroke-width:2px,color:#fff,font-weight:bold;
    classDef db fill:#1976d2,stroke:#0d47a1,stroke-width:2px,color:#fff,font-weight:bold;
    classDef subgraph fill:#f5f5f5,stroke:#333,stroke-width:2px;
    classDef module fill:#f0f0f0,stroke:#666,stroke-width:2px;
    
    class CLI core;
    class URLEngine,CrawlEngine,AIGen engine;
    class DB,Drive db;
