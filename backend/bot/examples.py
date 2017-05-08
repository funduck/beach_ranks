import urllib.request

params = urllib.parse.urlencode({
    'chat_id':151337209, 
    'parse_mode': 
    'markdown', 
    'reply_to_message_id': 3,
    'text': '29 Apr 13:17 epic win!\n29 Apr 13:36 loose'})

url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/sendMessage?%s' % params

print(urllib.request.urlopen(url).read())

{
'update_id': 269774286, 
	'callback_query': {
		'id': '649988363972810428', 
		'from': {
			'id': 151337209, 
			'first_name': 'Oleg', 
			'last_name': 'Milekhin', 
			'username': 'Oleg_Milekhin'}, 
		'message': {
			'message_id': 151, 
			'from': {
				'id': 299909888, 
				'first_name': 'beachranks', 
				'username': 'beachranks_bot'}, 
			'chat': {
				'id': 151337209, 
				'first_name': 'Oleg', 
				'last_name': 'Milekhin', 
				'username': 'Oleg_Milekhin', 
				'type': 'private'}, 
			'date': 1493584312, 
			'reply_to_message': {
				'message_id': 150, 
				'from': {
					'id': 151337209, 
					'first_name': 'Oleg', 
					'last_name': 'Milekhin', 
					'username': 'Oleg_Milekhin'}, 
				'chat': {
					'id': 151337209, 
					'first_name': 'Oleg', 
					'last_name': 'Milekhin', 
					'username': 'Oleg_Milekhin', 
					'type': 'private'}, 
				'date': 1493584309, 
				'text': '/list', 
				'entities': [
					{'type': 'bot_command', 'offset': 0, 'length': 5}
				]
			}, 
			'text': 'list'
		}, 
		'chat_instance': '-945995049493712829', 
		'data': 'next_btn'
	}
}