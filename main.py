import telebot
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
bot = telebot.TeleBot(config['Release']['TOKEN'])

tournament_commands_list = ['create_tournament', 'register', 'get_registered_users']
rating_commands_list = ['update_attack', 'get_rating_list']
settings_commands_list = ['show_settings', 'update_settings']


@bot.message_handler(commands=['start', 'help'])
def start_mes(message):
    bot.send_message(message.chat.id, f'Hi, {message.from_user.first_name}')


if __name__ == '__main__':
    bot.polling()
