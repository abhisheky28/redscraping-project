# redscraping_core/scraping/crawler/db_manager.py

import sqlite3
import os

class DBManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS urls_to_visit (url TEXT UNIQUE)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS urls_visited (url TEXT UNIQUE, status_code INTEGER, method TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS emails (email TEXT UNIQUE, source_url TEXT)''')
            
            # --- NEW TABLES FOR ASSETS AND ORPHANS ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    asset_url TEXT,
                    asset_type TEXT,
                    source_url TEXT,
                    UNIQUE(asset_url, source_url)
                )
            ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS sitemap_urls (url TEXT UNIQUE)''')
            conn.commit()

    def add_to_queue(self, urls):
        if not urls: return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for url in urls:
                cursor.execute('SELECT 1 FROM urls_visited WHERE url = ?', (url,))
                if cursor.fetchone(): continue
                cursor.execute('INSERT OR IGNORE INTO urls_to_visit (url) VALUES (?)', (url,))
            conn.commit()

    def get_next_batch(self, batch_size=100):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT url FROM urls_to_visit LIMIT ?', (batch_size,))
            return [row[0] for row in cursor.fetchall()]

    def mark_as_visited(self, url, status_code, method):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM urls_to_visit WHERE url = ?', (url,))
            cursor.execute('INSERT OR REPLACE INTO urls_visited (url, status_code, method) VALUES (?, ?, ?)', (url, status_code, method))
            conn.commit()

    def get_all_visited(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT url, status_code, method FROM urls_visited')
            return cursor.fetchall()
            
    def get_queue_count(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM urls_to_visit')
            return cursor.fetchone()[0]

    def save_emails(self, email_data):
        if not email_data: return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('INSERT OR IGNORE INTO emails (email, source_url) VALUES (?, ?)', email_data)
            conn.commit()

    def get_all_emails(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT email, source_url FROM emails')
            return cursor.fetchall()
        

    # --- NEW FUNCTIONS FOR ASSETS ---
    def save_assets(self, asset_data):
        if not asset_data: return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('INSERT OR IGNORE INTO assets (asset_url, asset_type, source_url) VALUES (?, ?, ?)', asset_data)
            conn.commit()

    def get_all_assets(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT asset_url, asset_type, source_url FROM assets')
            return cursor.fetchall()

    # --- NEW FUNCTIONS FOR ORPHANS ---
    def save_sitemap_urls(self, urls):
        if not urls: return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for url in urls:
                cursor.execute('INSERT OR IGNORE INTO sitemap_urls (url) VALUES (?)', (url,))
            conn.commit()

    def get_orphan_urls(self):
        """Returns URLs that are in the sitemap, but were NEVER found during the crawl."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url FROM sitemap_urls 
                WHERE url NOT IN (SELECT url FROM urls_visited)
            ''')
            return [row[0] for row in cursor.fetchall()]
            
    def get_non_sitemap_urls(self):
        """Returns URLs that were found during the crawl, but are MISSING from the sitemap."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url FROM urls_visited 
                WHERE url NOT IN (SELECT url FROM sitemap_urls)
            ''')
            return [row[0] for row in cursor.fetchall()]