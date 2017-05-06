import json
import uuid
from collections import namedtuple
import re
from .ui_types import PlayerContact, UIButton


ForReply = namedtuple('ForReply', [
    'inline_query_id', # query, entered inline
    'message_id', # it is message that holds pressed button in case of 'callback'
    'reply_to_message_id', # user's message
    'chat_id' # chat, in which user talks to us
])


def parse_message(message, bot_name='beachranks_bot'):
    input = None
    command = None
    
    if 'edited_message' in message or 'message' in message:
        kind = 'message'
        body = message['message']
        command = body['text'] if 'text' in body else ''
        if 'contact' in body:
            input = PlayerContact(name=body['contact']['first_name'], phone=body['contact']['phone_number'])
        reply = ForReply(
            chat_id=body['chat']['id'],
            message_id=None,
            reply_to_message_id=body['message_id'],
            inline_query_id=None
        )
    if 'inline_query' in message:
        kind = 'inline'
        body = message['inline_query']
        command = body['query']
        reply = ForReply(
            chat_id=None,
            message_id=None,
            reply_to_message_id=None,
            inline_query_id=body['id']
        )
    if 'callback_query' in message:
        kind = 'callback'
        body = message['callback_query']
        command = None
        reply = ForReply(
            chat_id=body['message']['chat']['id'],
            message_id=body['message']['message_id'],
            reply_to_message_id=None,
            inline_query_id=None
        )

    if kind is None:
        print('ERROR: unknown message format', message)
        return

    if command is not None:
        print('parsing command:', command)
        m = re.search(f'^(@{bot_name} |)(\/\w*\s*|)(@{bot_name}\s*|)(.*)', command)
        
        if input is None and m is not None:
            input = m.group(4)
            
        if m is not None:
            command = m.group(2)
            if command is not None:
                command = re.search('\/(\w*)', command)
                if command is not None:
                    command = command.group(1)
    print('command:', command, 'input:', input)
        
    # if something wrong, it throws exception

    return {
        'kind': kind,
        'body': body,
        'command': command,
        'input': input,
        'reply': reply
    }


class TelegramUserInteraction():
    buttons = {}
    messages = {}
    perform_request = None # function (request) performing request to telegram API
    on_user_input = None # function (command, input, as_reply) called on user incoming messages
    on_user_inline_input = None # function (command, input, as_reply) called on user inline input
    
    def __init__(self, perform_request):
        self.perform_request = perform_request
    
    def gen_req_id(self):
        return str(uuid.uuid1())

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
        
        r['body']['chat_id'] = as_reply.chat_id
        if as_reply.reply_to_message_id is not None:
            r['body']['reply_to_message_id'] = as_reply.reply_to_message_id

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
                    req_id = self.gen_req_id()
                    self.buttons[req_id] = b
                    btns.append({
                            'text': b.text,
                            'callback_data': req_id 
                        })

            r['body'].update({
                'reply_markup': json.dumps({
                    'inline_keyboard': all_btns
                })
            })
            
        self.perform_request(r)
        
    def show_contacts(self, contacts, as_reply):
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
        
        self.perform_request(r)
        
    def on_user_message(self, message):
        parsed = parse_message(message)
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
                print('no button callback for', req_id)