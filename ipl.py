import requests
from urllib.request import urlopen
import json, os, random
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")
CRIC_API1=os.getenv("CRIC_API1")
CRIC_API2=os.getenv("CRIC_API2")
urls={
    "sendMessage": f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    "sendPhoto" : f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
}

def tel_toss(chat_id, *args):
    tails="https://qph.cf2.quoracdn.net/main-qimg-148ae81e6fe0500e130fb547026a9b26-lq"
    heads="https://qph.cf2.quoracdn.net/main-qimg-e0e0099a4e81c40def6da0742c9201b5-lq"
    
    requests.post(urls['sendPhoto'], json={'chat_id':chat_id,'photo': random.choice([heads,tails])})

def tel_send_poll(chat_id,text, *args):
    text = list(text.split(" "))
    if len(text) > 2:
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

def tel_update_score(chat_id, text, msg, *args):
    try:
        username, score = text.split()[1:3] 
        score = int(score)
    except ValueError:
        requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': 'Invalid input format. Please use /update_score <username> <score>.'})
        return

    with open('score.json') as file:
        data = json.load(file)
    data[username] = score
    with open('score.json', 'w') as file:
        json.dump(data, file)

    requests.post(urls['sendMessage'], json={
        'chat_id': chat_id,
        'text': f'Updated {username}\'s score to {score} issued by @{msg["message"]["from"]["username"]}'
    })

    tel_show_score(chat_id)

def tel_show_score(chat_id, *args):
    with open('score.json') as file:
        data = json.load(file)
    
    text = 'Current Score\n\n'
    for key, value in data.items():
        text += f'{key} : {value}\n'
    
    requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': text})

def tel_match_score(chat_id, *args):
    try:
        response1 = urlopen(CRIC_API1)
        data_json1 = json.loads(response1.read())

        match_id = None
        for data in data_json1['data']:
            if data['series_id'] == 'c75f8952-74d4-416f-b7b4-7da4b4e3ae6e':
                match_id = data['id']
                break

        if match_id is not None:
            response2 = urlopen(CRIC_API2)
            data_json2 = json.loads(response2.read())

            for match_data in data_json2['data']:
                if match_data['id'] == match_id:
                    t1, t1s, t2, t2s, status = match_data['t1'], match_data['t1s'], match_data['t2'], match_data['t2s'], match_data['status']
                    text = f"{t1}\t{t1s}\nVS\n{t2}\t{t2s}\n\n{status}"
                    requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': text})
                    break

    except Exception as e:
        print(f"Error occurred in tel_match_score(): {e}")