import requests
import random
from cloudbot import hook


FuckOffList = [	'donut',
				'bus',
				'chainsaw',
				'king',
				'madison',
				'gfy',
				'back',
				'keep',
				'name'
				]

headers = {'Accept' : 'text/plain'}
RNDnumber = random.randrange(0, len(FuckOffList)-1)



@hook.command('fos','fuckoff','foaas')
def foaas(text, nick, message)
	Fuckee = text.strip()
	Fucker = nick

	r = requests.get('http://www.foaas.com/' + str(FuckOffList[RNDnumber]) + '/' + Fuckee + Fucker, headers=headers)
	out = r.text
	message(out)
