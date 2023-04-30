import requests
from urllib.request import urlopen
import json, os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")
urls={
    "sendMessage": f"https://api.telegram.org/bot{TOKEN}/sendMessage",
}


def tel_fact(chat_id, *args):
    text = json.loads(urlopen('https://uselessfacts.jsph.pl/api/v2/facts/random').read())['text']
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'{text}'})
    
def tel_send_message(chat_id, text, *args):
    requests.post(urls['sendMessage'], json={'chat_id': chat_id,'text': text})