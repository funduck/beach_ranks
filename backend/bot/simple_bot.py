import urllib.request
import json
import time


def send_request(params, method='sendMessage'):
	p = urllib.parse.urlencode(params)
	url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/%s?%s' % (method, p)
	return json.loads(urllib.request.urlopen(url).read())

def stupid_respond(message, not_inline=True):
	if not_inline:
		if 'text' in message:
			# to personal messages
			if message['chat']['type'] != 'group': 
				send_request({
					'chat_id': message['from']['id'], 
				    'parse_mode': 'markdown', 
				    'reply_to_message_id': message['message_id'],
				    'text': 'echo'
				})
			# to chat
			else:
				send_request({
					'chat_id': message['chat']['id'], 
				    'parse_mode': 'markdown', 
				    'reply_to_message_id': message['message_id'],
				    'text': 'echo'
				})
	else:
		# reply to personal messages only on commands 'test'
		if message['query'] == '/test':
			send_request({
				'chat_id': message['from']['id'], 
			    'parse_mode': 'markdown',
			    'text': 'echo'
			})

def get_updates(last_id=0):
	updates = send_request(params={'offset': last_id+1}, method='getUpdates')
	updates = updates['result']
	new_last_id = last_id
	for update in updates:
		print('responding to', update)

		if update['update_id'] > new_last_id:
			new_last_id = update['update_id']

		if last_id == 0:
			continue

		if 'edited_message' in update:
			stupid_respond(update['edited_message'])
		if 'message' in update:
			stupid_respond(update['message'])
		if 'inline_query' in update:
			stupid_respond(message=update['inline_query'], not_inline=False)
	return new_last_id


last_update = 0
while True:
	last_update = get_updates(last_update)
	time.sleep(5)