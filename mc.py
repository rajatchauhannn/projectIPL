import requests
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")
ATERNOS_USERNAME = os.getenv("ATERNOS_USERNAME")
ATERNOS_PASSWORD = os.getenv("ATERNOS_PASSWORD")
urls={
    "sendMessage": f"https://api.telegram.org/bot{TOKEN}/sendMessage"
}

def tel_aternos_status(chat_id, *args):    
    players = ''
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'Checking status for GBBPP625.aternos.me \n This could take several minutes...'})
    from python_aternos import Client   
    serv = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD).list_servers()[0]
    serv.fetch()

    if serv.players_count > 0:
        for i in serv.players_list:
            players += i + '\n'
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':f'GBBPP625.aternos.me is currently {serv.status} \n Players Connected: {serv.players_count} \n {players}'}) 

def tel_aternos_start(chat_id, *args):
    requests.post(urls['sendMessage'],json={'chat_id':chat_id,'text':'Request Received - Starting server GBBPP625.aternos.me - This could take several minutes'})
    from python_aternos import Client
    try:
        myserv = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD).list_servers()[0]
        myserv.start()
        requests.post(urls['sendMessage'],json={'chat_id': chat_id,'text': 'Server has started!'})
    except Exception as e:
        requests.post(urls['sendMessage'],json={'chat_id': chat_id,'text': f"Error starting server: {e}"})

def tel_aternos_stop(chat_id, *args):
    requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': 'Request Received - Stopping server GBBPP625.aternos.me - This could take several minutes'})
    from python_aternos import Client
    import time
    aternos = Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD)
    server = aternos.list_servers()[0]
    server.stop()
    
    while server.status != "offline":
        requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': f'Server is currently {server.status}, waiting it to finish before stopping...'})
        server.fetch()
        time.sleep(60)
    
    requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': 'Server has stopped!'})

def tel_aternos_execute(chat_id, *args):
    command = ' '.join(args)
    requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': f'Executing command "{command}" on GBBPP625.aternos.me...'})
    try:
        from python_aternos import Client   
        with Client.from_credentials(ATERNOS_USERNAME, ATERNOS_PASSWORD) as client:
            servers = client.list_servers()
            server = next((server for server in servers if server.name == 'GBBPP625'), None)
            if server is not None:
                server.execute_command(command)
                requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': 'Command executed successfully.'})
            else:
                requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': 'Server not found.'})
    except Exception as e:
        requests.post(urls['sendMessage'], json={'chat_id': chat_id, 'text': f'An error occurred: {e}'})