import bot


def run(message, matches, convo_id, chat_data, user_data):
    if matches[0] == 'example':
        text = 'Hello {}, nice to meet you.'.format(user_data.display_name)
        bot.send_message(convo_id, text)


plugin = {
    "name": "Example",
    "desc": "For example",
    "usage": ["/example"],
    "run": run,
    "sudo": True,
    "patterns": [
        "^[!/#](example)$",
    ],
    "action": [],
}
