import requests
from urllib.request import urlopen
import json, os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")
urls={
    "sendMessage": f"https://api.telegram.org/bot{TOKEN}/sendMessage"
}


def tel_fact(chat_id, *args):
    text = json.loads(urlopen('https://uselessfacts.jsph.pl/api/v2/facts/random').read())['text']
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'{text}'})
    
def tel_send_message(chat_id, text, *args):
    requests.post(urls['sendMessage'], json={'chat_id': chat_id,'text': text})


def tel_upload_file(file_id, *args):
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


def tel_send_document(chat_id, *args):
    payload = {
        'chat_id': chat_id,
        "document": "http://www.africau.edu/images/default/sample.pdf",
    }
    requests.post(urls['sendDocument'], json=payload)