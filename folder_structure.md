graph TD
%% Main Entry Point
    User((👤 User CLI)) --> CLI[🚀 cli.py Master Hub]

%% Routing from CLI
    CLI --> Utils[🛠️ utils/ <br> Setup & Config]
    CLI --> Scraping[🕷️ scraping/ <br> Core Engines]

%% Utils Subgraph
    subgraph Utils Module
        Utils --> SetupCmds[setup_cmds.py]
        SetupCmds --> Chrome[chrome_setup.py <br> Stealth Profile]
        SetupCmds --> ProjGen[project_generator.py <br> Workspace Init]
        ProjGen --> GCP[gcp_setup.py <br> Google Auth]
    end

%% Scraping Subgraph
    subgraph Scraping Module
        Scraping --> URLCmds[scrape_cmds.py]
        Scraping --> CrawlCmds[crawl_cmds.py]
        Scraping --> AICmds[ai/ai_cmds.py]

%% URL Features (List-Based)
        URLCmds --> URLEngine{engine.py <br> BS4 + Selenium}
        URLEngine --> Extractors[Headings, Titles, Meta, <br> Href, Elements, Text, Status]

%% Crawler (Site-Wide)
        CrawlCmds --> CrawlEngine{crawler_engine.py <br> Async + Selenium Swarm}
        CrawlEngine <--> DB[(db_manager.py <br> SQLite Cache)]
        DB <--> Drive[drive_manager.py <br> Google Drive Sync]
        CrawlEngine --> Spiders[URLs, Broken, Emails, <br> Assets, Orphans]

%% AI Module
        AICmds --> AIGen{ai_generator.py <br> Gemini 2.5 Flash}
        AIGen <--> KeyMgr[key_manager.py <br> .env Storage]
    end

%% Styling
    classDef core fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef engine fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef db fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    
    class CLI core;
    class URLEngine,CrawlEngine,AIGen engine;
    class DB,Drive db;
