from flask import Flask, request, Response
import requests, json, os, traceback
from urllib.request import urlopen
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")


from anime import tel_nsfw_waifu, tel_anime, tel_add_anime
from mc import tel_aternos_execute, tel_aternos_start, tel_aternos_status, tel_aternos_stop
from ipl import tel_match_score, tel_send_poll, tel_show_score, tel_toss, tel_update_score
from misc import tel_fact, tel_send_message

app = Flask(__name__)
urls={
    "sendMessage": f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    "sendPhoto" : f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
    "sendAnimation" : f"https://api.telegram.org/bot{TOKEN}/sendAnimation",
    "sendPoll" : f"https://api.telegram.org/bot{TOKEN}/sendPoll",
    "sendDocument" : f'https://api.telegram.org/bot{TOKEN}/sendDocument',
    "editMessageReplyMarkup" : f'https://api.telegram.org/bot{TOKEN}/editMessageReplyMarkup',
    "answerCallbackQuery" : f'https://api.telegram.org/bot{TOKEN}/answerCallbackQuery',
    "deleteMessage" : f'https://api.telegram.org/bot{TOKEN}/deleteMessage'
}

def parse_poll(message, *args):
    poll_id = message['poll_answer']['poll_id']
    user = message['poll_answer']['user']['username']
    option = message['poll_answer']['option_ids']

    print("poll_id-->", poll_id)
    print("user-->", user)
    print("option-->", option)

    return poll_id, user, option
 
def tel_parse_get_message(message):
    print("message-->", message)

    for media_type in ['photo', 'video', 'audio', 'document']:
        try:
            if media_type == 'photo':
                media_id = message['message'][media_type][-1]['file_id']
            else:
                media_id = message['message'][media_type]['file_id']
            chat_id = message['message']['chat']['id']
            print(f"g_chat_id-->{chat_id}, g_{media_type}_id-->{media_id}")

            return media_id
        except:
            pass

    print("No valid media file found")

def parse_message(message):
    try:
        chat_id = None
        txt = None
        message_id = None
        date = message.get('message', {}).get('date')
        if date:
            import datetime, time
            dftime = time.mktime(datetime.datetime.now().timetuple())
            if int(dftime-10) > date:
                return chat_id, txt, message_id
            chat_id = message['message']['chat']['id']
            txt = message['message']['text']
            message_id = message['message']['message_id']
            print("chat_id-->", chat_id)
            print("txt-->", txt)
        else:
            chat_id = message.get('callback_query', {}).get('message', {}).get('chat', {}).get('id')
            txt = message.get('callback_query', {}).get('data')
            message_id = message.get('callback_query', {}).get('message', {}).get('message_id')
            print("chat_id-->", chat_id)
            print("txt-->", txt)

            # Delete the original message
            if message_id:
                payload = {
                    'chat_id': chat_id,
                    'message_id': message_id
                }
                requests.post(urls['deleteMessage'], json=payload)

        return chat_id, txt
    except:
        print("Error in parsing message")
        return chat_id, txt
 
def tel_help(chat_id, *args):
    payload = {
        'chat_id': chat_id,
        'text': '''Commands:\n
/toss - Flips a coin
/poll <option1> <option2> - Creates a poll with two options
/match - Shows the status of the current match
/score <username> <value> - Updates the score for a user
/show - Shows the current score
/aternos start - Starts the Minecraft server
/aternos stop - Stops the Minecraft server
/aternos status - Tells the status of the Minecraft server
/fact - Tells a random fact
/help - Shows this help page'''
    }
    requests.post(urls['sendMessage'], json=payload)

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

def tel_send_inlineurl(chat_id, *args):
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

def tel_send_menu(chat_id, txt, msg, *args):
    payload = {
        'chat_id': chat_id,
        'text': "What can I help you with?",
        'reply_markup': {
            'inline_keyboard': [
                [
                    {
                        'text': '🪙 Toss a coin',
                        'callback_data': '/toss'
                    },
                    {
                        'text': '📈 Show score',
                        'callback_data': '/show'
                    }
                ],
                [
                    {
                        'text': '🏏 Status of the match',
                        'callback_data': '/match'
                    },
                    {
                        'text': '🕹️ Start Minecraft Server',
                        'callback_data': '/mcstart'
                    }
                ],
                [
                    {
                        'text': '❌ Cancel',
                        'callback_data': '/cancel'
                    }
                ]
            ]
        }
    }
    r = requests.post(urls['sendMessage'], json=payload)
    return r



# Define a list of valid commands to avoid repeated slicing of txt string
valid_commands = ['/mcexecute', '/toss', '/poll', '/score', '/show', '/match', '/help', '/nsfw', '/sfw', '/mcstart', '/mcstop', '/mcstatus', '/fact', '/anime', '/addanime', '/inlineurl', '/menu']

# Define the route and HTTP methods to be used
@app.route('/', methods=['GET', 'POST'])
def index():
    
    # Handle the POST request
    if request.method == 'POST':
        msg = request.get_json()
        try:
            chat_id, txt = parse_message(msg)

            #removes the @sagebestbot tag if the user inputted it
            def remove_bot_username(command):
                split_command = command.split()
                if len(split_command) > 0 and split_command[0].endswith("@sagebestbot"):
                    split_command[0] = split_command[0][:-(len("@sagebestbot"))]
                return ' '.join(split_command)
            
            txt = remove_bot_username(txt)

            # Use a dictionary to map the commands to their corresponding functions
            commands = {
                '/toss': tel_toss,
                '/poll': tel_send_poll,
                '/score': tel_update_score,
                '/show': tel_show_score,
                '/match': tel_match_score,
                '/help': tel_help,
                '/nsfw': tel_nsfw_waifu,
                '/sfw': tel_nsfw_waifu,
                '/mcstart': tel_aternos_start,
                '/mcstop': tel_aternos_stop,
                '/mcstatus': tel_aternos_status,
                '/fact': tel_fact,
                '/anime': tel_anime,
                '/addanime': tel_add_anime,
                '/inlineurl': tel_send_inlineurl,
                '/menu': tel_send_menu,
                '/mcexecute' : tel_aternos_execute
            }

            # Check if the txt string contains a valid command
            if txt.split()[0] in valid_commands:
                # Call the corresponding function based on the command
                commands[txt.split()[0]](chat_id, txt, msg)
            else:
                # Handle invalid commands
                pass
                
        except:
            traceback.print_exc()

        try:
            file_id = tel_parse_get_message(msg)
            tel_upload_file(file_id)
        except:
            print("No file from index--->")
    
        return Response('ok', status=200)
    
    # Handle the GET request
    else:
        return "<h1>Welcome!</h1>"

 
if __name__ == '__main__':
   app.run(threaded=True, debug=True)