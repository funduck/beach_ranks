import json
import re
from collections import namedtuple
from .common_types import Contact, Button


MessageIds = namedtuple('MessageIds', [
    'user_id', # telegram user id
    'inline_query_id', # can be None
    'message_id', # can be None
    'chat_id' # can be None
])

TelegramInMessage = namedtuple('TelegramInMessage', [
    'kind', # message, inline_query, callback_query
    'command', # bot's command
    'input', # text or contact
    'ids', # MessageIds
])

TelegramOutMessage = namedtuple('TelegramOutMessage', [
    'method',
    'body'
])


class TelegramInteraction():
    buttons = {}
    messages = {}
    perform_request = None # function (request) performing request to telegram API
    on_user_input = None # function (command, input, as_reply) called on user incoming messages
    on_user_inline_input = None # function (command, input, as_reply) called on user inline input

    @staticmethod
    def parse_message(message, bot_name='beachranks_bot'):
        kind = None
        input = None
        command = None
        ids = None
        
        if 'edited_message' in message or 'message' in message:
            kind = 'message'
            body = message['message']
            command = body['text'] if 'text' in body else None
            if 'contact' in body:
                input = Contact(name=body['contact']['first_name'], phone=body['contact']['phone_number'])
            ids = MessageIds(
                user_id=body['from']['id'],
                inline_query_id=None,
                message_id=body['message_id'],
                chat_id=body['chat']['id']
            )
        if 'inline_query' in message:
            kind = 'inline_query'
            body = message['inline_query']
            command = body['query']
            ids = MessageIds(
                user_id=body['from']['id'],
                inline_query_id=body['id'],
                message_id=None,
                chat_id=None
            )
        if 'callback_query' in message:
            kind = 'callback_query'
            body = message['callback_query']
            command = body['data']
            ids = MessageIds(
                user_id=body['from']['id'],
                inline_query_id=None,
                message_id=None,
                chat_id=body['message']['chat']['id']
            )

        if kind is None:
            print('ERROR: unknown message format', message)
            return

        if command is not None:
            #print('parsing command:', command)
            m = re.search(f'^(@{bot_name} |)(\/\w*|)(@{bot_name}|)(\s*)(.*)', command)
            
            if input is None and m is not None:
                input = m.group(5)
                
            if input is not None and len(input) == 0 and len(m.group(4)) == 0:
                input = None
                
            if m is not None:
                command = m.group(2)
                if command is not None:
                    command = re.search('\/(\w*)', command)
                    if command is not None:
                        command = command.group(1)
                
        #print('command:', command, 'input:', input)
            
        # if something wrong, it throws exception

        return TelegramInMessage(
            kind=kind,
            command=command,
            input=input,
            ids=ids
        )

    def show_message(self, as_reply, message=None, buttons=None):
        if as_reply.chat_id is None:
            print('ERROR: Can show message only when know chat_id')
            return
        r = {
            'method': 'sendMessage',
            'body': {
                'parse_mode': 'markdown',
                'text': message
            }
        }
        
        r['body']['chat_id'] = as_reply.chat_id if as_reply.chat_id is not None else as_reply.user_id
        if as_reply.message_id is not None:
            r['body']['reply_to_message_id'] = as_reply.message_id

        if buttons is not None:
            # now support 1 row only, when change to multirow, change it in scenarios too
            all_btns = [[]]
            btns = all_btns[0]
            for b in buttons:
                if b.switch_inline is not None:
                    btns.append({
                        'text': b.text,
                        'switch_inline_query_current_chat': b.switch_inline 
                    })
                else:
                    btns.append({
                        'text': b.text,
                        'callback_data': b.callback
                    })

            r['body'].update({
                'reply_markup': json.dumps({
                    'inline_keyboard': all_btns
                })
            })
            
        return TelegramOutMessage(
            method=r['method'],
            body=r['body']
        )

    def show_contacts(self, as_reply, contacts):
        if as_reply.inline_query_id is None:
            print('ERROR: Can show contacts only on inline query')
            return
        c = []
        for i in range(0, len(contacts)):
            c.append({
                'type': 'contact',
                'id': str(i),
                'phone_number': str(contacts[i].phone),
                'first_name': contacts[i].name
            })
        r = {
            'method': 'answerInlineQuery',
            'body': {
                'inline_query_id': as_reply.inline_query_id,
                'results': json.dumps(c)
            }
        }
        
        return TelegramOutMessage(
            method=r['method'],
            body=r['body']
        ) 

'''    def on_user_message(self, message):
        parsed = TelegramInteraction.parse_message(message)
        if parsed['kind'] == 'message':
            if self.on_user_input is not None:
                self.on_user_input(command=parsed['command'], input=parsed['input'], as_reply=parsed['reply'])
            else:
                print('ERROR: on_user_input is not defined')
        
        if parsed['kind'] == 'inline':
            if self.on_user_inline_input is not None:
                self.on_user_inline_input(command=parsed['command'], input=parsed['input'], as_reply=parsed['reply'])
            else:
                print('ERROR: on_user_inline_input is not defined')
                
        if parsed['kind'] == 'callback':
            req_id = parsed['body']['data']
            
            if req_id in self.buttons:
                self.buttons[req_id].callback(self.buttons[req_id].arg)
                del self.buttons[req_id]
            else:
                print('no button callback for', req_id)'''