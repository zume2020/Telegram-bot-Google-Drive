#!/usr/bin/env python

from __future__ import print_function
import os
import telegram
import logging
from telegram.ext import Updater
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler ,MessageHandler
from telegram.ext import MessageHandler, Filters
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)


SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()),cache_discovery=False)




def file_handler():
  file_name='abc.rar'
  FILES = ((file_name, False),)

  for filename, convert in FILES:
      metadata = {'name': filename}
      media = MediaFileUpload(file_name, chunksize=1024 * 1024, mimetype='application/x-rar-compressed',  resumable=True)
      request = DRIVE.files().create(body=metadata,
                                    media_body=media)
      response = None
      while response is None:
        status, response = request.next_chunk()
#        print(status)
        if status:
           print( "Uploaded %d%%." % int(status.progress() * 100))
      print ("Upload Complete!")


if __name__ == '__main__':
    file_handler()