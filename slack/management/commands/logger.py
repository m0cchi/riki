from django.core.management.base import BaseCommand
import websocket
import threading
import time
from slacker import Slacker
import os
import sys
import json
from slack.models import Event, SlackUser, Message
from django.core.exceptions import ObjectDoesNotExist

def on_message(ws, message):
    payload = json.loads(message)
    type = payload['type']
    user = None
    if 'user' in payload:
        raw_id = payload['user']
        try:
            user = SlackUser.objects.get(raw_id = raw_id)
        except ObjectDoesNotExist:
            user = SlackUser.objects.create(raw_id = raw_id,
                                            display = raw_id)
    event = Event.objects.create(type = payload['type'],
                                 subtype = payload.get('subtype'),
                                 raw = message,
                                 user = user)

    if type == 'message' and 'reply_to' not in payload:
        Message.objects.create(event = event,
                               text = payload['text'])
    

def on_error(ws, error):
    print(error)

def on_close(ws):
   print('### closed ###')

def on_open(ws):
    def run():
       for i in range(3):
           time.sleep(1)
           ws.send('Hello %d' % i)
       time.sleep(1)
       ws.close()
       print('thread terminating...')
    threading.Thread(target = run, args = ())

class Command(BaseCommand):

    def handle(self, *args, **options):
        slack = Slacker(os.environ['TOKEN'])
        response = slack.rtm.start()
        body = response.body

        if not body['ok']:
            print(body['error'])
            sys.exit(1)

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(body['url'],
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close)
        ws.on_open = on_open
        ws.run_forever()
