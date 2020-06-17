#!/usr/bin/env python

from __future__ import print_function
import os
import config
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
DRIVE = discovery.build('drive', 'v2', http=creds.authorize(Http()),cache_discovery=False)



def start(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id, text="Upload files here.")


def file_handler(update, context):
  file = context.bot.getFile(update.message.document.file_id)
  file.download(update.message.document.file_name)

  FILES = ((update.message.document.file_name, False),(update.message.document.file_name, True),)

  for filename, convert in FILES:
      metadata = {'name': filename}
      media = MediaFileUpload(filename, chunksize=1024 * 1024, mimetype='application/x-rar-compressed',  resumable=True)
      request = DRIVE.files().create(body=metadata,
                                    media_body=media)
      response = None
      while response is None:
        status, response = request.next_chunk()
        if status:
           print( "Uploaded %d%%." % int(status.progress() * 100))
      print ("Upload Complete!")



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