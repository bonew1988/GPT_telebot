import telebot
import openai
import os


class NeuroBot:
    def __init__(self, telegram_bot_token, openai_api_key):
        self.telegram_bot_token = telegram_bot_token
        self.openai_api_key = openai_api_key
        self.bot = telebot.TeleBot(self.telegram_bot_token)
        openai.api_key = self.openai_api_key
        self.dialog_context = {}
        self.LOGS_DIR = "logs"
        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)
        self.bot_running = False
        self.bot_thread = None

    def start_bot(self):
        if not self.bot_running:
            self.bot_thread = threading.Thread(target=self.bot.polling)
            self.bot_thread.start()
            self.bot_running = True
            self.bot.send_message(message.chat.id, "Бот успешно запущен.")
        else:
            self.bot.send_message(message.chat.id, "Бот уже запущен.")

    def stop_bot(self):
        if self.bot_running:
            self.bot.stop_polling()
            self.bot_thread.join()
            self.bot_running = False
            self.bot.send_message(message.chat.id, "Бот успешно остановлен.")
        else:
            self.bot.send_message(message.chat.id, "Бот не был запущен.")

    def view_log(self, user_id):
        user_log_file = os.path.join(self.LOGS_DIR, f"{user_id}_log.txt")
        if os.path.exists(user_log_file):
            with open(user_log_file, "r", encoding="utf-8") as file:
                return file.read()
        else:
            return "Лог для данного пользователя не найден."

    def start_message(self, message):
        user_id = message.from_user.id
        self.dialog_context[user_id] = """ Я хочу что ты зна(а) я первый в России нейро-психолог-бот. 
        Моя миссия - помочь вам лучше понимать себя и свой мир, исследуя тайны 
        человеческой психологии и нейронаук. Я готов разгадывать ваши головоломки, 
        предлагать вдохновение и давать советы для улучшения вашей жизни. 
        Доверьтесь моим талантам, и вместе мы сможем сделать вашу жизнь ярче и осознаннее. 
        Добро пожаловать в мир исследования собственного ума!"""
        self.bot.send_message(
            message.chat.id, f"Привет! Я твой личный психолог. {self.dialog_context[user_id]} Просто напиши мне что-нибудь.")

    def reply_to_message(self, message):
        user_message = message.text
        user_id = message.from_user.id
        system_message = self.dialog_context.get(user_id, "")

        context = system_message
        context += " " + user_message
        self.dialog_context[user_id] = context

        response = self.generate_chat_response(context)

        if response.strip():
            self.bot.send_message(message.chat.id, response)
            self.log_message(user_id, user_message, response)

    def generate_chat_response(self, user_message):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_message,
            max_tokens=500,
            temperature=0.5,
            n=1
        )

        response_text = response.choices[0].text.strip()

        if response_text.startswith('?'):
            response_text = response_text[1:]

        if response_text:
            response_text = response_text[0].upper() + response_text[1:]
            response_text = ' ' + response_text

        return response_text

    def log_message(self, user_id, user_message, bot_response):
        user_log_file = os.path.join(self.LOGS_DIR, f"{user_id}_log.txt")
        with open(user_log_file, "a", encoding="utf-8") as file:
            file.write(f"User: {user_message}\n")
            file.write(f"Bot: {bot_response}\n")
            file.write("\n")

    def handle_commands(self, message):
        if message.text == '/start_bot':
            self.start_bot()
        elif message.text == '/stop_bot':
            self.stop_bot()
        elif message.text == '/view_log':
            user_id = message.from_user.id
            log_text = self.view_log(user_id)
            self.bot.send_message(message.chat.id, log_text)


if __name__ == '__main__':
    neuro_bot = NeuroBot('YOUR_TELEGRAM_BOT_TOKEN',
                         'YOUR_OPENAI_API_KEY')
    neuro_bot.bot.message_handler(commands=['start'])(neuro_bot.start_message)
    neuro_bot.bot.message_handler(func=lambda message: True)(
        neuro_bot.reply_to_message)
    neuro_bot.bot.message_handler(
        commands=['start_bot', 'stop_bot', 'view_log'])(neuro_bot.handle_commands)

    print("Bot is running...")
    neuro_bot.bot.polling()
