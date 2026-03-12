# redscraping_core/scraping/crawler/drive_manager.py

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from rich.console import Console
import io

console = Console()

class DriveManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.folder_name = "RedScraping_Cache"
        self.authenticate()

    def authenticate(self):
        """Authenticates using the existing token.json."""
        token_path = os.path.join(os.getcwd(), 'token.json')
        if os.path.exists(token_path):
            scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            self.creds = Credentials.from_authorized_user_file(token_path, scopes)
            self.service = build('drive', 'v3', credentials=self.creds)
        else:
            console.print("[red]⚠️ Google Auth token not found. Run 'redscrape init' first.[/red]")

    def _get_folder_id(self):
        """Finds or creates the RedScraping_Cache folder in Google Drive."""
        if not self.service: return None
        
        query = f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if not items:
            file_metadata = {'name': self.folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            return folder.get('id')
        return items[0].get('id')

    def _get_file_id(self, filename, folder_id):
        """Finds a specific file inside the cache folder."""
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        return items[0].get('id') if items else None

    def download_db(self, domain_name, local_path):
        """Downloads the SQLite database from Google Drive if it exists."""
        if not self.service: return False
        
        folder_id = self._get_folder_id()
        filename = f"{domain_name}_crawl.db"
        file_id = self._get_file_id(filename, folder_id)
        
        if file_id:
            console.print(f"[cyan]☁️ Found previous cache for {domain_name} on Google Drive. Downloading...[/cyan]")
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(local_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            console.print("[green]✅ Cache downloaded successfully![/green]")
            return True
        else:
            console.print(f"[dim]No previous cloud cache found for {domain_name}. Starting fresh.[/dim]")
            return False

    def upload_db(self, domain_name, local_path):
        """Uploads or updates the SQLite database on Google Drive."""
        if not self.service or not os.path.exists(local_path): return
        
        console.print("[cyan]☁️ Backing up cache to Google Drive...[/cyan]")
        folder_id = self._get_folder_id()
        filename = f"{domain_name}_crawl.db"
        file_id = self._get_file_id(filename, folder_id)
        
        media = MediaFileUpload(local_path, mimetype='application/x-sqlite3', resumable=True)
        
        if file_id:
            # Update existing file
            self.service.files().update(fileId=file_id, media_body=media).execute()
        else:
            # Create new file
            file_metadata = {'name': filename, 'parents': [folder_id]}
            self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
        if hasattr(media, '_fd') and media._fd:
            media._fd.close()
            
        console.print("[green]✅ Cloud backup complete![/green]")