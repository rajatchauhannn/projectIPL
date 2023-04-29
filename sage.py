from flask import Flask, request, Response
import requests, random, json, os, traceback
from urllib.request import urlopen, Request
from dotenv import load_dotenv
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
    "sendPoll" : f"https://api.telegram.org/bot{TOKEN}/sendPoll",
    "sendDocument" : f'https://api.telegram.org/bot{TOKEN}/sendDocument'
}

def tel_send_message(chat_id, text):
    requests.post(urls['sendMessage'], json={'chat_id': chat_id,'text': text})

def tel_add_anime(chat_id, text):
    text = list(text.split('\n'))
    question=text[1]
    options=[text[2],text[3],text[4],text[5],]
    correct_answer=text[6]

    print("\n")
    
    entry={'question': question, 'options': options, 'correct_answer': correct_answer}

    with open('anime.json', "r") as file:
        data = json.load(file)

    data.append(entry)

    with open('anime.json', "w") as file:
        json.dump(data, file)
    
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'Added question : {question} \nOptions : {text[2]}, {text[3]}, {text[4]}, {text[5]}\nCorrect Answer : {text[6]}'})

def tel_anime(chat_id):
    import random
    url = urlopen(f'https://opentdb.com/api.php?amount=1&category=31').read()
    question = json.loads(url)['results'][0]['question']
    correct_answer = json.loads(url)['results'][0]['correct_answer']
    all_answers = json.loads(url)['results'][0]['incorrect_answers']
    all_answers.append(correct_answer)
    print(all_answers)
    random.shuffle(all_answers)
    correct_option_id=all_answers.index(correct_answer)
    print(correct_option_id)
    payload = {
            'chat_id' : chat_id,
            'question': question,
            "options": json.dumps(all_answers),
            "is_anonymous" : False,
            "type":"quiz",
            "correct_option_id": correct_option_id

        } 
    requests.post(urls['sendPoll'], json=payload)

def tel_fact(chat_id):
    text = json.loads(urlopen('https://uselessfacts.jsph.pl/api/v2/facts/random').read())['text']
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'{text}'})

def tel_aternos_status(chat_id):    
    players = ''
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'Checking status for GBBPP625.aternos.me \n This could take several minutes...'})
    from python_aternos import Client   
    serv = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD).list_servers()[0]
    serv.fetch()

    if serv.players_count > 0:
        for i in serv.players_list:
            players += i + '\n'
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'GBBPP625.aternos.me is currently {serv.status} \n Players Connected: {serv.players_count} \n {players}'}) 

def tel_aternos_start(chat_id):
    """Starts Minecraft Server

    Args:
        chat_id (string): Telegram Chat ID

    Returns:
        _type_: _description_
    """
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':'Request Recieved - Starting server GBBPP625.aternos.me - This could take several minutes'})
    from python_aternos import Client
    myserv = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD).list_servers()[0]
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
 
def tel_parse_get_message(message):
    print("message-->", message)

    try:  # if the file is an image
        g_chat_id = message['message']['chat']['id']
        g_file_id = message['message']['photo'][0]['file_id']
        print("g_chat_id-->", g_chat_id)
        print("g_image_id-->", g_file_id)

        return g_file_id
    except:
        try:  # if the file is a video
            g_chat_id = message['message']['chat']['id']
            g_file_id = message['message']['video']['file_id']
            print("g_chat_id-->", g_chat_id)
            print("g_video_id-->", g_file_id)

            return g_file_id
        except:
            try:  # if the file is an audio
                g_chat_id = message['message']['chat']['id']
                g_file_id = message['message']['audio']['file_id']
                print("g_chat_id-->", g_chat_id)
                print("g_audio_id-->", g_file_id)

                return g_file_id
            except:
                try:  # if the file is a document
                    g_chat_id = message['message']['chat']['id']
                    g_file_id = message['message']['document']['file_id']
                    print("g_chat_id-->", g_chat_id)
                    print("g_file_id-->", g_file_id)

                    return g_file_id
                except:
                    pass

def parse_message(message):
    try:
        print("message-->",message)
        date = message['message']['date']
        import datetime, time
        dftime = time.mktime(datetime.datetime.now().timetuple())
        if int(dftime-10) > date:
            return chat_id, ""
        chat_id = message['message']['chat']['id']
        txt = message['message']['text']
        print("chat_id-->", chat_id)
        print("txt-->", txt)

        return chat_id, txt
    except:
        print("NO text found-->>")

    try:
        cha_id = message['callback_query']['from']['id']
        i_txt = message['callback_query']['data']
        print("cha_id-->", cha_id)
        print("i_txt-->", i_txt)

        return cha_id, i_txt
    except:
        pass

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
        tel_show_score(chat_id)
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
            if i['series_id'] == 'c75f8952-74d4-416f-b7b4-7da4b4e3ae6e':
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
                'chat_id': chat_id,'text': '''Commands:\n\n/toss - Flips a coin \n/poll <option1> <option2> - Creates a poll\n/match - Shows status of current match\n/score <username> <value> - updates the score\n/show - shows current score\n/aternos start - starts minecraft server\n/aternos stop - stops minecraft server\n/aternos status - tells the status of the minecraft server\n/fact - tells a random fact\n/help - This page'''
                }
   
    requests.post(urls['sendMessage'],json=payload)

def tel_upload_file(file_id):
    # Getting the url for the file
    url = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}'
    a = requests.post(url)
    json_resp = json.loads(a.content)
    print("json_resp-->", json_resp)
    file_path = json_resp['result']['file_path']
    print("file_path-->", file_path)

    # saving the file to our computer
    url_1 = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
    b = requests.get(url_1)
    file_content = b.content
    with open(file_path, "wb") as f:
        f.write(file_content)


def tel_send_document(chat_id, text):
    payload = {
        'chat_id': chat_id,
        "document": "http://www.africau.edu/images/default/sample.pdf",
    }
    requests.post(urls['sendDocument'], json=payload)

def tel_send_inlinebutton(chat_id):
    payload = {
        'chat_id': chat_id,
        'text': "What is this?",
        'reply_markup': {
            "inline_keyboard": [[
                {
                    "text": "A",
                    "callback_data": "ic_A"
                },
                {
                    "text": "B",
                    "callback_data": "ic_B"
                }]
            ]
        }
    }
    requests.post(urls['sendMessage'], json=payload)

def tel_send_inlineurl(chat_id):
    payload = {
        'chat_id': chat_id,
        'text': "Which link would you like to visit?",
        'reply_markup': {
            "inline_keyboard": [
                [
                    {"text": "google", "url": "http://www.google.com/"},
                    {"text": "youtube", "url": "http://www.youtube.com/"}
                ]
            ]
        }
    }
    requests.post(urls['sendMessage'], json=payload)

def tel_send_button(chat_id):
    payload = {
        'chat_id': chat_id,
        'text': "What is this?",    # button should be in the propper format as described
        'reply_markup': {
            'keyboard': [[
                {
                    'text': 'supa'
                },
                {
                    'text': 'mario'
                }
            ]],
        'one_time_keyboard' : True
        }
    }
    r = requests.post(urls['sendMessage'], json=payload)
    return r

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        try:
            chat_id,txt = parse_message(msg)

            if txt[:5] == "/toss":
                tel_toss(chat_id)
            elif txt[:5] == "/poll":
                tel_send_poll(chat_id, txt)
            elif txt[:6] == "/score":
                tel_update_score(chat_id, txt, msg)
            elif txt[:5] == "/show":
                tel_show_score(chat_id)
            elif txt[:6] == '/match':
                tel_match_score(chat_id)
            elif txt[:5] == '/help':
                tel_help(chat_id)
            elif txt[:5] == '/nsfw' or txt[:4] == '/sfw':
                tel_nsfw_waifu(chat_id, txt)
            elif txt[:8] == '/mcstart':
                tel_aternos_start(chat_id)
            elif txt[:7] == '/mcstop':
                tel_aternos_stop(chat_id)
            elif txt[:9] == '/mcstatus':
                tel_aternos_status(chat_id)
            elif txt[:5] == '/fact':
                tel_fact(chat_id)
            elif txt[:6] == '/anime':
                tel_anime(chat_id)
            elif txt[:9] == '/addanime':
                tel_add_anime(chat_id, txt)
            elif txt == "/inline":
                tel_send_inlinebutton(chat_id)
            elif txt == "ic_A":
                tel_send_message(chat_id, "You have clicked A")
            elif txt == "ic_B":
                tel_send_message(chat_id, "You have clicked B")
            elif txt[:10] == "/inlineurl":
                tel_send_inlineurl(chat_id)
            elif txt == "/button":
                tel_send_button(chat_id)
            else:
                pass
                
        except:
            traceback.print_exc()

        try:
            file_id = tel_parse_get_message(msg)
            tel_upload_file(file_id)
        except:
            print("No file from index--->")
    
        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"
 
if __name__ == '__main__':
   app.run(threaded=True, debug=True)