import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from rich.console import Console

# Import your setup function
from ...utils.chrome_setup import setup_master_profile

console = Console()

class UrlEngine:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        self.driver = None
        self.profile_path = os.path.join(os.getcwd(), "Chrome-Profile")
        
        # ==============================================================
        # NEW: Auto-Setup Chrome Profile if it was deleted or missing
        # ==============================================================
        if not os.path.exists(self.profile_path):
            console.print("\n[yellow]⚠️ Chrome Profile not found! Setting it up before we start scraping...[/yellow]")
            setup_master_profile()
        # ==============================================================

    def get_driver(self):
        if not self.driver:
            options = Options()
            options.add_argument(f"--user-data-dir={self.profile_path}")
            options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(options=options)
        return self.driver

    def fetch(self, url, parser_func):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return parser_func(soup, is_selenium=False)
        except Exception:
            pass

        driver = self.get_driver()
        driver.get(url)
        return parser_func(driver, is_selenium=True)

    def close(self):
        if self.driver:
            self.driver.quit()