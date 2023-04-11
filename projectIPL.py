from flask import Flask
from flask import request
from flask import Response
import requests
import random
import json
from urllib.request import urlopen, Request
import os 
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")
ATERNOS_USERNAME = os.getenv("ATERNOS_USERNAME")
ATERNOS_PASSWORD = os.getenv("ATERNOS_PASSWORD")
CRIC_API=os.getenv("CRIC_API")

app = Flask(__name__)

def tel_aternos_start(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    requests.post(url,json={'chat_id':chat_id,'text':'Request Recieved - Starting server GBBPP625.aternos.me - This could take several minutes'})
    from python_aternos import Client
    aternos = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD)
    servs = aternos.list_servers()
    myserv=servs[0]
    myserv.start()
    payload = {
            'chat_id': chat_id,
            'text': 'Server has started!'
            }
   
    r = requests.post(url,json=payload)
    return r

def tel_aternos_stop(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    requests.post(url,json={'chat_id':chat_id,'text':'Request Recieved - Stopping server GBBPP625.aternos.me - This could take several minutes'})
    from python_aternos import Client
    aternos = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD)
    servs = aternos.list_servers()
    myserv=servs[0]
    myserv.stop()
    payload = {
        'chat_id': chat_id,
        'text': 'Server has stopped!'
        }
   
    r = requests.post(url,json=payload)
    return r

def parse_poll(message):
    poll_id = message['poll_answer']['poll_id']
    user = message['poll_answer']['user']['username']
    option = message['poll_answer']['option_ids']

    print("poll_id-->", poll_id)
    print("user-->", user)
    print("option-->", option)

    return poll_id, user, option
 
def parse_message(message):
    print("message-->",message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id,txt
 
def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': text
                }
   
    r = requests.post(url,json=payload)
    return r

def tel_send_video(chat_id):
    video=""
    url = f'https://api.telegram.org/bot{TOKEN}/sendVideo'
    payload = {
        'chat_id' : chat_id,
        'video' : video
    }

    r = requests.post(url, json=payload)
    return r


def tel_send_image(chat_id):
    tails="https://qph.cf2.quoracdn.net/main-qimg-148ae81e6fe0500e130fb547026a9b26-lq"
    heads="https://qph.cf2.quoracdn.net/main-qimg-e0e0099a4e81c40def6da0742c9201b5-lq"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {
        'chat_id':chat_id,
        'photo': random.choice([heads,tails])
    }
    r = requests.post(url, json=payload)
    return r

def tel_nsfw_waifu(chat_id, text):
    text = list(text.split(" "))

    response = Request(
        url=f'https://api.waifu.pics/{text[0][1:]}/{text[1]}', 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    data_json = json.loads(urlopen(response).read())
    if data_json['url'][-4:] == '.gif':
        tel_url = f"https://api.telegram.org/bot{TOKEN}/sendAnimation"
        payload = {
            'chat_id':chat_id,
            'animation': data_json['url']
        }
        r = requests.post(tel_url, json=payload)
        return r
    else:
        tel_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            'chat_id':chat_id,
            'photo': data_json['url']
            }
        r = requests.post(tel_url, json=payload)
        return r

def tel_send_poll(chat_id,text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendPoll'
    text = list(text.split(" "))
    print(len(text))
    if len(text) > 1:
        payload = {
            'chat_id' : chat_id,
            'question': 'Who wil win today?',
            "options": json.dumps([text[1], text[2]]),
            "is_anonymous" : False,
            "type":"regular",

        }
        r = requests.post(url, json=payload)
        return r
    else:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
        return requests.post(url, json={'chat_id':chat_id, 'text':'Also add poll options :)'})

def tel_update_score(chat_id, text, msg):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    text = list(text.split(" "))
    if len(text) > 1:
        with open('score.json', "r") as file:
            data = json.load(file)
        data.update({text[1]:int(text[2])})
        with open('score.json', "w") as file:
            json.dump(data, file)
        file.close()

        payload={
            'chat_id': chat_id,
            'text': f'Updated {text[1]}\'s score to {text[2]} issued by @{msg["message"]["from"]["username"]}'
        }

        r = requests.post(url, json=payload)
        return r
    else:
        return requests.post(url,json={'chat_id':chat_id,'text':'Enter username with score please :)'})

def tel_show_score(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    with open('score.json', "r") as file:
        data = json.load(file)
    text='Current Score\n\n'
    for i in data:
        text = text + str(i) + " : " + str(data[i]) + '\n'
    file.close()

    payload={
        'chat_id':chat_id,
        'text': text
    }
    r = requests.post(url, json=payload)
    return r

def tel_match_score(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    iplurl = "https://api.cricapi.com/v1/cricScore?apikey={CRIC_API}"

    response = urlopen(iplurl)
    data_json = json.loads(response.read())

    for i in data_json['data']:
        if i['ms'] == 'live' or i['ms'] == 'result' and i['matchType'] == 't20':
            currentMatch = i
            break
            
    text = currentMatch['t1'] + '\t' +  currentMatch['t1s']  + '\nVS \n' + currentMatch['t2'] + '\t' + currentMatch['t2s']+ '\n\n' + currentMatch['status']
    print(text)
    payload = {
                'chat_id': chat_id,
                'text': text
                }

    r= requests.post(url, json=payload)
    return r
 
def tel_help(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': 'Commands:\n\n /toss - Flips a coin \n /poll <option1> <option2> - Creates a poll\n /match - Shows status of current match\n /score <username> <value> - updates the score\n /show - shows current score\n /help - This page'
                }
   
    r = requests.post(url,json=payload)
    return r

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        try:
            chat_id,txt = parse_message(msg)

            if txt == "/toss":
                tel_send_image(chat_id)
            elif txt[:5] == "/poll":
                tel_send_poll(chat_id, txt)
            elif txt[:6] == "/score":
                tel_update_score(chat_id, txt, msg)
            elif txt == "/show":
                tel_show_score(chat_id)
            elif txt == '/match':
                tel_match_score(chat_id)
            elif txt == '/help':
                tel_help(chat_id)
            elif txt[:5] =='/nsfw' or txt[:4] == '/sfw':
                tel_nsfw_waifu(chat_id, txt)
            elif txt == '/aternos start':
                tel_aternos_start(chat_id)
            elif txt == '/aternos stop':
                tel_aternos_stop(chat_id)
            else:
                pass
                
        except:
            print("No file from index-->")
            # poll_id,user,option=parse_poll(msg)
    
        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"
 
if __name__ == '__main__':
   app.run(debug=True)