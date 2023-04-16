from flask import Flask
from flask import request
from flask import Response
import requests
import random
import json
from urllib.request import urlopen, Request
import os 
from dotenv import load_dotenv
import traceback
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")
ATERNOS_USERNAME = os.getenv("ATERNOS_USERNAME")
ATERNOS_PASSWORD = os.getenv("ATERNOS_PASSWORD")
CRIC_API1=os.getenv("CRIC_API1")
CRIC_API2=os.getenv("CRIC_API2")

app = Flask(__name__)
urls={
    "sendMessage": f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    "sendPhoto" : f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
    "sendAnimation" : f"https://api.telegram.org/bot{TOKEN}/sendAnimation",
    "sendPoll" : f"https://api.telegram.org/bot{TOKEN}/sendPoll"
}
def tel_aternos_status(chat_id):
    players = ''
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'Checking status for GBBPP625.aternos.me \n This could take several minutes...'})
    from python_aternos import Client   
    aternos = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD)
    serv = aternos.list_servers()[0]
    serv.fetch()

    if serv.players_count > 0:
        for i in serv.players_list:
            players += i + '\n'
    return requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'GBBPP625.aternos.me is currently {serv.status} \n Players Connected: {serv.players_count} \n {players}'}) 

def tel_aternos_start(chat_id):
    """Starts Minecraft Server

    Args:
        chat_id (string): Telegram Chat ID

    Returns:
        _type_: _description_
    """
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':'Request Recieved - Starting server GBBPP625.aternos.me - This could take several minutes'})
    from python_aternos import Client
    aternos = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD)
    servs = aternos.list_servers()
    myserv=servs[0]
    myserv.start()
    requests.post(urls['sendMessage'],json={'chat_id': chat_id,'text': 'Server has started!'})

def tel_aternos_stop(chat_id):
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':'Request Recieved - Stopping server GBBPP625.aternos.me - This could take several minutes'})
    from python_aternos import Client
    aternos = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD)
    servs = aternos.list_servers()
    myserv=servs[0]
    myserv.stop()
   
    requests.post(urls['sendMessage'],json={'chat_id': chat_id,'text': 'Server has stopped!'})

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
    date = message['message']['date']
    import datetime, time
    date_time = datetime.datetime.now()
    dftime = time.mktime(date_time.timetuple())
    if int(dftime-10) > date:
        return chat_id, ""
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id,txt

def tel_toss(chat_id):
    tails="https://qph.cf2.quoracdn.net/main-qimg-148ae81e6fe0500e130fb547026a9b26-lq"
    heads="https://qph.cf2.quoracdn.net/main-qimg-e0e0099a4e81c40def6da0742c9201b5-lq"
    
    requests.post(urls['sendPhoto'], json={'chat_id':chat_id,'photo': random.choice([heads,tails])})

def tel_nsfw_waifu(chat_id, text):
    text = list(text.split(" "))

    response = Request(
        url=f'https://api.waifu.pics/{text[0][1:]}/{text[1]}', 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    data_json = json.loads(urlopen(response).read())
    if data_json['url'][-4:] == '.gif':
        requests.post(urls['sendAnimation'], json={'chat_id':chat_id,'animation': data_json['url']})
    else:
        requests.post(urls['sendPhoto'], json={'chat_id':chat_id,'photo': data_json['url']})

def tel_send_poll(chat_id,text):
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
        requests.post(urls['sendPoll'], json=payload)
    else:
        requests.post(urls['sendMessage'], json={'chat_id':chat_id, 'text':'Also add poll options :)'})

def tel_update_score(chat_id, text, msg):
    text = list(text.split(" "))
    if len(text) > 1:
        with open('score.json', "r") as file:
            data = json.load(file)
        data.update({text[1]:int(text[2])})
        with open('score.json', "w") as file:
            json.dump(data, file)
        file.close()
        requests.post(urls['sendMessage'], json={'chat_id': chat_id,'text': f'Updated {text[1]}\'s score to {text[2]} issued by @{msg["message"]["from"]["username"]}'})
    else:
        requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':'Enter username with score please :)'})

def tel_show_score(chat_id):

    with open('score.json', "r") as file:
        data = json.load(file)
    text='Current Score\n\n'
    for i in data:
        text = text + str(i) + " : " + str(data[i]) + '\n'
    file.close()
    requests.post(urls['sendMessage'], json={'chat_id':chat_id,'text': text })

def tel_match_score(chat_id):
    response = urlopen(f"{CRIC_API1}")
    data_json = json.loads(response.read())

    for i in data_json['data']:
        try:
            if i['matchType'] == 't20':
                break
        except:
            pass
    response = urlopen(f"{CRIC_API2}")
    data_json = json.loads(response.read())
    for j in data_json['data']: 
        if j['id'] == i['id']:
            break

    text = j['t1'] + '\t' +  j['t1s']  + '\nVS \n' + j['t2'] + '\t' + j['t2s']+ '\n\n' + j['status']
    print(text)
    requests.post(urls['sendMessage'], json={'chat_id': chat_id,'text': text})
 
def tel_help(chat_id):
    payload = {
                'chat_id': chat_id,
                'text': '''Commands:\n\n 
                /toss - Flips a coin \n
                /poll <option1> <option2> - Creates a poll\n
                /match - Shows status of current match\n
                /score <username> <value> - updates the score\n
                /show - shows current score\n 
                /help - This page'''
                }
   
    requests.post(urls['sendMessage'],json=payload)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        try:
            chat_id,txt = parse_message(msg)

            if txt == "/toss":
                tel_toss(chat_id)
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
            elif txt == '/aternos status':
                tel_aternos_status(chat_id)
            else:
                pass
                
        except:
            traceback.print_exc()
    
        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"
 
if __name__ == '__main__':
   app.run(debug=True)