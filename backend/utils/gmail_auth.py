import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from ..config import settings

CLIENT_SECRET_FILE = settings.google_client_secret_file
SCOPES = settings.google_scopes_list
redirect_uri = "http://localhost:8000/"  # ← MUST MATCH Google Console

def get_gmail_service():
    creds = None
    print("SCOPES BEING USED:", SCOPES)
    print("Redirect URI being used:", redirect_uri)
    
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES
        )
        # Using redirect_uri_trailing_slash=True uses http://localhost:8000/
        creds = flow.run_local_server(
            port=8000,
            redirect_uri_trailing_slash=True  # matches http://localhost:8000/
        )
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)
    return service
