import requests, logging, json
from config import settings
from database import get_item
logger = logging.Logger("BOT_1")

class BotError(Exception):
    ...

class Bot:
    def __init__(self, token):
        self.token = token
        self.base_url = f'https://api.telegram.org/bot{self.token}'
        self.file_base_url = f'https://api.telegram.org/file/bot{self.token}'

    def _request(self, http_method, tg_method, **kwargs):
        resp = requests.request(http_method, f"{self.base_url}/{tg_method}", **kwargs)
        try:
            resp_json = resp.json()
        except Exception:
            resp_json = {}

        cleaned_request_args = {
            k: ({fn: '...' for fn in v.keys()} if k == 'files' and v else v)
            for k, v in kwargs.items()
        }
        logger.info(
            f'TG {http_method} Request: {tg_method} Token: {self.token}\n'
            f'Request data: {cleaned_request_args} Response: {resp_json}',
        )

        try:
            resp.raise_for_status()
        except requests.HTTPError as ex:
            raise BotError(
                f'Request error: {ex}, response: {resp_json or ex.response.content}',
                response=resp,
            )
        if not resp_json['ok']:
            raise BotError(f'Request to TG API failed: {resp}', response=resp)
        return resp_json['result']

    def get(self, tg_method, params=None):
        return self._request('GET', tg_method, params=params)

    def post(self, tg_method, data=None, files=None):
        return self._request('POST', tg_method, data=data, files=files)

    def get_bot_info(self):
        return self.get("getMe")

    def get_chat_member_info(self, chat_id, user_id):
        return self.get("getChatMember", {'chat_id': chat_id, 'user_id': user_id})

    def set_webhook(self, url):
        params = {"url": url}
        return self.get('setWebhook', params=params)

    def send_tg_message(
        self,
        chat_id,
        text,
        parse_mode=None,
        reply_markup=None,
        message_thread_id=None,
        reply_to_message_id=None,
        disable_web_page_preview=False,
    ):
        data = {
            "text": text,
            "chat_id": chat_id,
            "parse_mode": parse_mode,
            "reply_markup": reply_markup,
            "message_thread_id": message_thread_id,
            "reply_to_message_id": reply_to_message_id,
            "disable_web_page_preview": disable_web_page_preview,
        }
        resp = self.post('sendMessage', data=data)
        return resp['message_id']

    def answer_callback_query(
        self,
        callback_query_id,
        text,
        show_alert=False,
        url=None,
    ):
        data = {
            "text": text,
            "callback_query_id": callback_query_id,
            "show_alert": show_alert,
            "url": url,
        }
        resp = self.post('answerCallbackQuery', data=data)
        return resp

    def update_tg_message(self, chat_id, message_id, text, parse_mode=None, reply_markup=None):
        data = {
            "text": text,
            "chat_id": chat_id,
            "message_id": message_id,
            "parse_mode": parse_mode,
            "reply_markup": reply_markup,
        }
        return self.post('editMessageText', data=data)

    def edit_message_caption(
        self,
        chat_id,
        message_id,
        caption,
        caption_entities=None,
        parse_mode=None,
    ):
        data = {
            "caption": caption,
            "chat_id": chat_id,
            "message_id": message_id,
            "caption_entities": caption_entities,
            "parse_mode": parse_mode,
        }
        try:
            self.post('editMessageCaption', data=data)
        except BotError as ex:
            if (
                ex.response.status_code == 400 and
                'new message content and reply markup are exactly the same' in
                ex.response.json().get('description', '')
            ):
                pass
            else:
                raise

    def edit_photo_message(
        self,
        chat_id,
        message_id,
        file_id,
        caption,
        parse_mode,
    ):
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'media': json.dumps({
                'type': 'photo',
                'media': file_id,
                'caption': caption,
                'parse_mode': parse_mode,
            }),
        }
        return self.post('editMessageMedia', data)

    def delete_messages(self, chat_id, message_ids):
        data = {"chat_id": chat_id, "message_ids": json.dumps(message_ids)}
        return self.post('deleteMessages', data)

    def delete_message(self, chat_id, message_id):
        data = {"chat_id": chat_id, "message_id": message_id}
        return self.post('deleteMessage', data)

    def pin_message(self, chat_id, message_id, disable_notification=False):
        data = {"chat_id": chat_id, "message_id": message_id}
        return self.post('pinChatMessage', data)

    def promote_chat_member(self, chat_id, user_id, data):
        data = {"chat_id": chat_id, "user_id": user_id, **data}
        return self.post('promoteChatMember', data)

    def restrict_chat_member(self, chat_id, user_id, data):
        data = {"chat_id": chat_id, "user_id": user_id, **data}
        return self.post('restrictChatMember', data)

    def ban_chat_member(self, chat_id, user_id):
        data = {
            "user_id": user_id,
            "chat_id": chat_id,
        }
        return self.post('BanChatMember', data=data)

    def unban_chat_member(self, chat_id, user_id):
        data = {
            "user_id": user_id,
            "chat_id": chat_id,
        }
        return self.post('unbanChatMember', data=data)

    def create_thread(self, chat_id, name, icon=None, icon_color=None):
        data = {
            "name": name,
            "chat_id": chat_id,
            "icon_color": icon_color,
            "icon_custom_emoji_id": icon,
        }
        return self.post('createForumTopic', data=data)

    def edit_thread(self, chat_id, message_thread_id, name, icon=None):
        data = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
            "name": name,
            "icon_custom_emoji_id": icon,
        }
        return self.post('editForumTopic', data=data)

    def delete_thread(self, chat_id, message_thread_id):
        data = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return self.post('deleteForumTopic', data=data)

    def forward_tg_message(
        self,
        from_chat_id,
        message_id,
        to_chat_id,
        message_thread_id,
    ):
        data = {
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "chat_id": to_chat_id,
            "message_thread_id": message_thread_id,
        }
        resp = self.post('forwardMessage', data=data)
        return resp['message_id']

    def copy_tg_messages(
        self,
        from_chat_id,
        message_ids,
        to_chat_id,
        message_thread_id=None,
    ):
        data = {
            "from_chat_id": from_chat_id,
            "message_ids": json.dumps(message_ids),
            "chat_id": to_chat_id,
            "message_thread_id": message_thread_id,
        }
        logger.info(data)
        resp = self.post('copyMessages', data=data)
        return resp['message_id']

    def copy_tg_message(
        self,
        from_chat_id,
        message_id,
        to_chat_id,
        message_thread_id=None,
    ):
        data = {
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "chat_id": to_chat_id,
            "message_thread_id": message_thread_id,
        }
        logger.info(data)
        resp = self.post('copyMessage', data=data)
        return resp['message_id']

    def send_photo(
        self,
        chat_id,
        photo,
        caption=None,
        parse_mode=None,
        reply_markup=None,
        message_thread_id=None,
        caption_entities=None,
        reply_to_message_id=None,
    ):
        data = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
            "parse_mode": parse_mode,
            "reply_markup": reply_markup,
            "message_thread_id": message_thread_id,
            "caption_entities": caption_entities,
            "reply_to_message_id": reply_to_message_id,
        }
        resp = self.post('sendPhoto', data=data)
        return resp['message_id'], resp['photo'][-1]['file_id']

    def send_document(
        self,
        chat_id,
        file,
        message_thread_id=None,
        reply_to_message_id=None,
    ):
        data = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
            "reply_to_message_id": reply_to_message_id,
        }
        resp = self.post('sendDocument', data=data, files=file)
        return resp['message_id']

    def approve_chat_join_request(self, chat_id, user_id):
        resp = self.post(
            'approveChatJoinRequest',
            data={"chat_id": chat_id, "user_id": user_id},
        )
        return resp

    def send_voice(
        self,
        chat_id,
        url=None,
        message_thread_id=None,
        reply_to_message_id=None,
        stream=None,
    ):
        if url:
            content_resp = requests.get(url)
            resp = self.post(
                'sendVoice',
                data={
                    'chat_id': chat_id,
                    'message_thread_id': message_thread_id,
                    'reply_to_message_id': reply_to_message_id,
                },
                files={'voice': content_resp.content},
            )
        else:
            resp = self.post(
                'sendVoice',
                data={
                    'chat_id': chat_id,
                    'message_thread_id': message_thread_id,
                    'reply_to_message_id': reply_to_message_id,
                },
                files={'voice': stream},
            )

        return resp['message_id']

    def send_chat_action(self, action, chat_id, message_thread_id=None):
        return self.post(
            'sendChatAction',
            data={
                'action': action,
                'chat_id': chat_id,
                'message_thread_id': message_thread_id,
            },
        )

    def create_invite_link(self, chat_id, creates_join_request=False):
        return self.post(
            'createChatInviteLink',
            data={'chat_id': chat_id, 'creates_join_request': creates_join_request},
        )

    def get_user_profile_photos(self, user_id):
        return self.post('getUserProfilePhotos', data={'user_id': user_id})

    def get_chat(self, chat_id):
        return self.post('getChat', data={'chat_id': chat_id})

    def get_file_url(self, file_id):
        tg_file_path = self.get('getFile', {'file_id': file_id})['file_path']
        return f'{self.file_base_url}/{tg_file_path}'

    def set_chat_photo(self, chat_id, file_path):
        return self.post(
            'setChatPhoto',
            data={'chat_id': chat_id},
            files={'photo': ('photo.jpg', open(file_path, 'rb'))},
        )

    def set_chat_title(self, chat_id, title):
        return self.post(
            'setChatTitle',
            data={'chat_id': chat_id, 'title': title},
        )

class Entrypoint:
    def __init__(self, body, token):
        self.body = body
        self.bot = Bot(token)
        self.admin_chat = settings.ADMIN_CHAT
        self.msg_hello = """Приветствуем вас в онлайн магазине [Название]!\nВ этом боте вы сможете оформить заказ и ознакомиться с ассортиментом."""
    
    def order_to_tg(self):
        message = ''
        phone = self.body.get("phone", None)
        address = self.body.get("address", None)
        comment = self.body.get("comment", None)
        user_id = self.body.get("user_id", None)
        products:dict = self.body.get("products", None)
        if user_id:
            if phone:
                message+=f'Телефон: {phone}.\n'
            else:
                message+=f'Телефон не указан.\n'
            if address:
                message+=f'Адрес: {address}.\n'
            else:
                message+=f'Адрес не указан.\n'
            if comment:
                message+=f'Комментарий: {comment}.\n'
            else:
                message+=f'Комментарий не указан.'
            if products:
                message+=f'Корзина:\n'
                total = 0
                for key in products.keys():
                    item = get_item(int(key)).to_json()
                    amount = int(products[key])
                    if amount >= 10:
                        total+=item['mt10']*amount
                    else:
                        total+=item['retail_price']*amount
                    message+=f'\t{item["name"]} - {amount} шт.\n'
                message+=f'Итого: {total}฿'

            with open("chat.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            
            topic_id = None
            for item in data:
                if item[0] == user_id:
                    topic_id = item[1]
            if not topic_id:
                topic_id = self.bot.create_thread(self.admin_chat, user_id)['message_thread_id']
                data.append([user_id, topic_id])
                with open("chat.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            self.bot.send_tg_message(
                chat_id=self.admin_chat,
                text=message,
                message_thread_id=topic_id
                )
            return

    def run(self):
        self.message = self.body.get('message', None)
        if not self.message:
            return

        self.message_id = self.message.get('message_id', None)
        self.message_from = self.message.get('from', {})
        if not self.message_from or self.message_from.get('is_bot', None):
            return

        self.chat = self.message.get('chat', None)
        self.chat_type = self.chat.get('type', None)
        self.chat_id = self.chat.get('id', None)

        self.text = ""
        self.document = ""
        if self.message.get('text'):
            self.text = self.message["text"]
        elif self.message.get('document'):
            self.document = self.message["document"]
        elif self.message.get('voice'):
            self.tg_file_id = self.message['voice']['file_id']
            self.text = self.transcribe_voice_audio(self.tg_file_id)
        else:
            return

        self.first_name = self.message_from.get('first_name')
        self.username = self.message_from.get('username')
        self.user_id = self.message_from.get('id')

        if self.chat_type == 'private' and self.text == '/start':
            keyboard = [[{"text": "В магазин", "web_app": {"url": "https://t.me/snus1_feni_bot/snus1feni0shop"}}]]
            markup = json.dumps({"inline_keyboard": keyboard})
            self.bot.send_tg_message(chat_id=self.chat_id, text=self.msg_hello, reply_markup=markup)

class Entrypoint2:
    def __init__(self, body, token):
        self.body = body
        self.bot = Bot(token)
        self.admin_chat = settings.ADMIN_CHAT
        self.msg_hello = """Приветствуем вас в онлайн магазине [Название]!\nВ этом боте вы сможете оформить заказ и ознакомиться с ассортиментом."""
    
    def run(self):
        self.message = self.body.get('message', None)
        if not self.message:
            return
        
        self.message_id = self.message.get('message_id', None)
        self.message_from = self.message.get('from', {})
        if not self.message_from:
            return

        self.chat = self.message.get('chat', None)
        self.chat_type = self.chat.get('type', None)
        self.chat_id = self.chat.get('id', "")

        self.new_chat_member = self.message.get('new_chat_member', {})
        self.new_chat_member_name = self.new_chat_member.get('first_name', {})
        if self.new_chat_member_name:
            self.bot.delete_message(self.chat_id, self.message_id)
            self.bot.send_tg_message(
                self.chat_id, 
                f"{self.new_chat_member_name}, добро пожаловать в группу!", 
            )

        self.first_name = self.message_from.get('first_name')
        self.username = self.message_from.get('username')
        self.user_id = self.message_from.get('id')

        if self.chat_type == "private":
            with open("chat.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            
            topic_id = None
            for item in data:
                if item[0] == self.chat_id:
                    topic_id = item[1]

            if not topic_id:
                topic_id = self.bot.create_thread(self.admin_chat, self.first_name)['message_thread_id']
                data.append([self.chat_id, topic_id])
                with open("chat.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            self.bot.forward_tg_message(self.chat_id, self.message_id, self.admin_chat, topic_id)
            return

        if self.message.get('text'):
            self.text = self.message["text"]
        else:
            return

        if self.chat_id != self.admin_chat:
            return

        if self.message.get('is_topic_message'):
            self.message_thread_id = self.message.get('message_thread_id', None)
            with open("chat.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            
            chat_id = None
            for item in data:
                if item[1] == self.message_thread_id:
                    chat_id = item[0]
            
            if not chat_id:
                return
            
            self.bot.send_tg_message(chat_id, self.text)
            return