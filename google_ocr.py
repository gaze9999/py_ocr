#!/usr/bin/python3
"""
Shows basic usage of the Drive v3 API.

Creates a Drive v3 API service and prints the names and ids of the last 10 files
the user has access to.
"""
from __future__ import print_function
import httplib2
import os
import io

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

# Setup the Drive v3 API
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Python OCR'

"""
get credentials, if not or invalid, get new one
return credential
"""
def get_credentials():
    cred_path = os.path.join("./", 'google-ocr-credential.json')
    store = Storage(credential_path)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
          creds = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
          creds = tools.run(flow, store)
        print('憑證儲存於：' + cred_path)
      return creds

def main():
  creds = get_credentials()
  http = creds.authorize(httplib2.Http())
  service = discovery.build('drive', 'v3', http=http)
  imgfile = '*.jpg' #input
  txtfile = '*.txt' #output

  #upload to google cloud
  mime = 'application/vnd.google-apps.document'
  res = service.files().create(
    body={
      'name': imgfile,
      'mimeType': mime
    },
    media_body=MediaFileUpload(imgfile, mimetype=mime, resumable=True)
  ).execute()

  # download resault
  downloader = MediaIoBaseDownload(
    io.FileIO(txtfile, 'wb'),
    service.files().export_media(fileId=res['id'], mimeType="text/plain")
  )
  done = False
  while done is False:
    status, done = downloader.next_chunk()
  service.files().delete(fileId=res['id']).execute() #remove upload file

if __name__ == '__main__':
  main()

""" google remain
# Call the Drive v3 API
results = service.files().list(
    pageSize=10, fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])
if not items:
    print('No files found.')
else:
    print('Files:')
    for item in items:
        print('{0} ({1})'.format(item['name'], item['id']))
"""
