from pyngrok import ngrok, conf
from urllib.request import urlopen
import os 
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TEL_TOKEN")
NGROK_TOKEN = os.getenv("NGROK_TOKEN")
ngrok.set_auth_token(NGROK_TOKEN)
http_tunnel = ngrok.connect(5000)
conf.get_default().region = "in"
conf.get_default().ngrok_version = "v3"

os.system("curl  http://localhost:4040/api/tunnels > tunnels.json")

tunnels = ngrok.get_tunnels()
tunnel = tunnels[0].__dict__['data']['public_url']

urlopen(f'https://api.telegram.org/bot{TOKEN}/setWebhook?url={tunnel}')


ssh_tunnel = ngrok.connect(22, "tcp")
ngrok_process = ngrok.get_ngrok_process()

try:
    # Block until CTRL-C or some other terminating event
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print(" Shutting down server.")

    ngrok.kill()