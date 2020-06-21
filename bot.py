#!/usr/bin/env python

from __future__ import print_function
import os
import config
import pickle
import telegram
import logging
from telegram.ext import Updater
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler ,MessageHandler
from telegram.ext import MessageHandler, Filters
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)


def getCreds():
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  creds = None
  SCOPES = 'https://www.googleapis.com/auth/drive'

  if os.path.exists('token.pickle'):
      with open('token.pickle', 'rb') as token:
          creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              'credentials.json', SCOPES)
          creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open('token.pickle', 'wb') as token:
          pickle.dump(creds, token)

  return creds

def start(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id, text="Upload files here.")


def file_handler(update, context):
  """handles the uploaded files"""

  file = context.bot.getFile(update.message.document.file_id)
  file.download(update.message.document.file_name)

  doc = update.message.document

  service = build('drive', 'v3', credentials=getCreds(),cache_discovery=False)
  filename = doc.file_name

  metadata = {'name': filename}
  media = MediaFileUpload(filename, chunksize=1024 * 1024, mimetype=doc.mime_type,  resumable=True)
  request = service.files().create(body=metadata,
                                media_body=media)

  response = None
  while response is None:
    status, response = request.next_chunk()
    if status:
       print( "Uploaded %d%%." % int(status.progress() * 100))

  context.bot.send_message(chat_id=update.effective_chat.id, text="✅ File uploaded!")


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

def error(bot, update, error):
  logger.warning('Update "%s" caused error "%s"', update, error)

def main():
  updater = Updater(token=config.TOKEN,use_context=True)
  dispatcher = updater.dispatcher
  updater.dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(MessageHandler(Filters.document,file_handler))
  updater.start_polling()

if __name__ == '__main__':
    main()