from telebot import TeleBot, types
from time import sleep
import db

TOKEN = '7137134345:AAGGznKxyxxxrcu3FrVAxzMBd4puauyu0qk'
bot = TeleBot(TOKEN)
game = False
night = False

# kill
# Добавить проверку, что человек не мафия
# if message.from_user.username in db.get_mafia_usernames():
# Проверить что сейчас ночь

def game_loop(message):
    global night
    bot.send_message(message.chat.id, 'Добро пожаловать в игру, вам дается 2 минуты чтобы познкомится')
    sleep(120)
    while True:
        if night:
            bot.send_message(message.chat.id, 'Город засыпает, мафия просыпается')
            bot.send_message(message.chat.id, get_killed())
        else:
            bot.send_message(message.chat.id, 'Наступил день, город просыпается')
            bot.send_message(message.chat.id, get_killed())
        winner = db.check_winner()
        if winner is not None:
            bot.send_message(message.chat.id, f'Победили {winner}')
            break
        night = not night
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, f'Остались в игре: {alive}')
        db.clear()
        sleep(120)


def get_killed():
    if night:
        killed = db.mafia_kill()
        return f'Мафия убила {killed}'
    killed = db.citizen_kill()
    return 'Горожане выгнали {killed}'


@bot.message_handler(commands=['kill'])
def kill(message):
    username = message.text.split()[1:]
    usernames = db.get_all_alive()
    mafia = db.get_mafia_usernames()
    if night:
        if not message.from_user.username in mafia:
            bot.send_message(message.chat.id, 'Вы не мафия!')
            return
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого пользователя нет в игре')
            return
        voted = db.vote('mafia_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтен')
            return
        bot.send_message(message.chat.id, 'Вы не можете голосовать')
        return
    bot.send_message(message.chat.id, 'Сейчас день! Нельзя голосовать')


@bot.message_handler(commands=['kick'])
def kick(message):
    username = message.text.split()[1]
    usenames = db.get_all_alive()
    if not night:
        if username not in usenames:
            bot.send_message(message.chat.id, 'Такого пользователя нет в игре')
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтен')
            return
        bot.send_message(message.chat.id, 'Вы не можете голосовать')
        return
    bot.send_message(message.chat.id, 'Сейчас ночь, нельзя голосовать')


@bot.message_handler(commands=['play'])
def start(message):
    bot.send_message(
        message.chat.id, 'Если хотите играть напишие "готов играть" боту в лс')


@bot.message_handler(func=lambda message: message.text.lower() == 'готов играть' and message.chat.type == 'private')
def add_player(message):
    db.insert_player(message.from_user.id, message.from_user.username)
    bot.send_message(message.chat.id, f'{message.from_user.username} играет')
    bot.send_message(message.chat.id, 'Вы добавлены в игру')


@bot.message_handler(commands=['game'])
def start_game(message):
    global game
    players = db.players_amount()
    if players >= 5:
        db.set_roles(players)
        game = True
        players_roles = db.get_player_roles()
        mafias = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player_id, f'Ваша роль: {role}')
            if role == 'mafia':
                bot.send_message(player_id, f'Мафия: {mafias}')
        bot.send_message(message.chat.id, 'Игра началась')
        db.clear(dead=True)
        game_loop(message)
        return
    bot.send_message(message.chat.id, 'Недостаточно игроков')


if __name__ == '__main__':
    bot.polling(none_stop=True)
