import bot
from utils import glance

bot_state = ''


def set_bot_state(state):
    global bot_state
    bot_state = state


def run(message, matches, convo_id, chat_data, user_data):
    msg_type, convo_id, user_id = glance(message)
    if matches[0] == 'status' and len(matches) == 2:
        if not bot.is_sudo(user_id):
            return bot.send_message(convo_id, 'You\'re not authorized')
        bot.set_status(matches[1])
        return bot.send_message(convo_id, 'Status updated')

    if matches[0] == 'changepic':
        if not bot.is_sudo(user_id):
            return bot.send_message(convo_id, 'You\'re not authorized')
        set_bot_state('waiting_picture')
        return bot.send_message(convo_id, 'Please send a photo...')

    if msg_type == 'image':
        global bot_state
        if bot_state == 'waiting_picture':
            if not bot.is_sudo(user_id):
                return
            path = message.file_path
            bot.set_profile_pricture(path)
            bot_state = ''
            return bot.send_message(convo_id, 'Photo has been changed :)')


plugin = {
    "name": "Botself",
    "desc": "Bot itself",
    "usage": ["/status <text status>"],
    "run": run,
    "sudo": False,
    "patterns": [
        "^[!/#](status) (.+)$",
        "^[!/#](changepic)$",
    ],
    "action": ["image"],
}
