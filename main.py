from python_aternos import Client
aternos = Client.from_credentials('rajudgamer','rajat1234Aternos$')
servs = aternos.list_servers()
myserv=servs[0]
myserv.start()