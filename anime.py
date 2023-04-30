import requests
from urllib.request import urlopen, Request
import json, os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")
urls={
    "sendMessage": f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    "sendPhoto" : f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
    "sendAnimation" : f"https://api.telegram.org/bot{TOKEN}/sendAnimation",
}

def tel_add_anime(chat_id, *args):
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

def tel_anime(chat_id, *args):
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

def tel_nsfw_waifu(chat_id, text, *args):
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