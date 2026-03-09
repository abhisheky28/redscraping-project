import os
import click
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from .auth_config import CLIENT_CONFIG

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def setup_gcp_auth():
    creds = None
    current_dir = os.getcwd()
    token_path = os.path.join(current_dir, 'token.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            click.secho("🔄 Refreshing expired Google token...", fg="yellow")
            creds.refresh(Request())
        else:
            click.secho("🌐 Opening browser to authenticate with Google...", fg="cyan")
            flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
        click.secho(f"✅ Success! Google Sheets connected.", fg="green", bold=True)
    else:
        click.secho("✅ Google Sheets is already connected!", fg="green")