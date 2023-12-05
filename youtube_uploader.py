import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from apiclient.errors import HttpError
import httplib2
import argparse

CLIENT_SECRETS_FILE = "client_secrets.json"  # Path to your client_secrets.json
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service():
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    CREDENTIALS_FILE = "youtube_credentials.pickle"

    credentials = None
    # Load existing credentials from a file
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            credentials = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(CREDENTIALS_FILE, 'wb') as token:
            pickle.dump(credentials, token)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)

def initialize_upload(youtube, video_path, title, description, category, keywords, privacy_status):
    tags = None
    if keywords:
        tags = keywords.split(",")

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category
        },
        'status': {
            'privacyStatus': privacy_status,
            'madeForKids': False,  # This video is not made for kids
            'selfDeclaredMadeForKids': False  # Self-declaration of the content not being made for kids
        }
    }

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if 'id' in response:
                print(f"Video id '{response['id']}' was successfully uploaded.")
            else:
                print("The upload failed with an unexpected response.")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        except httplib2.HttpLib2Error as e:
            error = f"A retriable error occurred: {e}"

        if error is not None:
            print(error)
            retry += 1
            if retry > 10:
                exit("No longer attempting to retry.")
            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(f"Sleeping {sleep_seconds} seconds and then retrying...")
            time.sleep(sleep_seconds)

def upload_video_to_youtube(video_path, title, description, category="22", keywords="", privacy_status="public"):
    if not os.path.exists(video_path):
        raise Exception("Please specify a valid file.")

    youtube = get_authenticated_service()
    try:
        initialize_upload(youtube, video_path, title, description, category, keywords, privacy_status)
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        raise
