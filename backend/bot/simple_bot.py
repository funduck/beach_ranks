import urllib.request
import json
import time


def send_request(params, method='sendMessage'):
	p = urllib.parse.urlencode(params)
	print('\n', method, '\n', params)
	url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/%s?%s' % (method, p)
	return json.loads(urllib.request.urlopen(url).read())

def stupid_respond(message):
	# regular messages
	if message['kind'] == 'message':
		r = {
			'parse_mode': 'markdown',
		    'text': 'echo'
		}
		if message['command'] == '/list':
			r.update({
				'text': 'list with paging',
				'reply_markup': json.dumps({
			    	'inline_keyboard': [
			    		[{
			    			'text': 'prev',
			    			'callback_data': 'prev_btn'
			    		}, {
			    			'text': 'next',
			    			'callback_data': 'next_btn'
			    		}]
			    	]
		    	})
	    	})
		r.update(message['reply'])
		send_request(params=r, method='sendMessage')

	if message['kind'] == 'inline':
		r = {
			'parse_mode': 'markdown',
		    'text': 'echo'
		}
		r.update(message['reply'])
		send_request(params=r, method='sendMessage')

	if message['kind'] == 'callback':
		r = {
			'parse_mode': 'markdown',
		    'text': 'next list' if message['body']['data'] == 'next_btn' else 'prev list',
		}
		r.update({
			'reply_markup': json.dumps({
		    	'inline_keyboard': [
		    		[{
		    			'text': 'prev',
		    			'callback_data': 'prev_btn'
		    		}, {
		    			'text': 'next',
		    			'callback_data': 'next_btn'
		    		}]
		    	]
	    	})
    	})
		r.update(message['reply'])
		send_request(params=r, method='editMessageText')

def parse_message(update):
	if 'edited_message' in update or 'message' in update:
		kind = 'message'
		body = update['message']
		command = body['text']
		reply = {
			'chat_id': body['chat']['id'] if body['chat']['type'] != 'group' else body['from']['id'],
			'reply_to_message_id': body['message_id']
		}
	if 'inline_query' in update:
		kind = 'inline'
		body = update['inline_query']
		command = body['query']
		reply = {
			'chat_id': body['from']['id']
		}
	if 'callback_query' in update:
		kind = 'callback'
		body = update['callback_query']
		command = body['message']['reply_to_message']['text']
		reply = {
			'chat_id': body['message']['chat']['id'],
			'message_id': body['message']['message_id']
		}

	# if something wrong, it throws exception

	return {
		'kind': kind,
		'body': body,
		'command': command,
		'reply': reply
	}

def get_updates(last_id=0):
	updates = send_request(params={'offset': last_id+1}, method='getUpdates')
	updates = updates['result']
	new_last_id = last_id
	for update in updates:
		print('\nresponding to:\n', update)

		if update['update_id'] > new_last_id:
			new_last_id = update['update_id']

		if last_id == 0:
			continue

		prep = parse_message(update)

		stupid_respond(message=prep)
	return new_last_id

last_update = 0
while True:
	last_update = get_updates(last_update)
	time.sleep(5)