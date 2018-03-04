import os
import re
from os.path import exists, join

import bot
from utils import glance


def add_plugin(plugin_name):
    if plugin_name in bot.config['plugins']:
        return "This plugin is already active"
    if not exists(join(bot.WD, "plugins", plugin_name + ".py")):
        return "There is no file with name " + plugin_name + " in plugins directory"
    bot.config['plugins'].append(plugin_name)
    bot.save_config()
    bot.load_plugins()
    text = plugin_name + " enabled"
    return text


def remove_plugin(plugin_name):
    if plugin_name == "admins":
        bot.load_plugins()
        return "You can't disable plugins admin!\nPlugins reloaded."
    if plugin_name not in bot.config['plugins']:
        return "This plugin is not active"
    bot.config['plugins'].remove(plugin_name)
    bot.save_config()
    bot.load_plugins()
    text = plugin_name + " disabled"
    return text


def show_plugins():
    plugin_files = [files for files in os.listdir(join(bot.WD, "plugins")) if re.search("^(.*)\.py$", files)]
    text = 'Plugins:'
    n = 1
    for plugin_file in plugin_files:
        plugin_file = plugin_file.replace(".py", "")
        if plugin_file == "__init__":
            continue
        status = '❌'
        if plugin_file in bot.config['plugins']:
            status = '✅'
        text = text + '\n{}. {} {}'.format(n, plugin_file, status)
        n += 1
    return text


def run(message, matches, convo_id, chat_data, user_data):
    # msg_type, convo_id, user_id = glance(message)
    if matches[0] == 'plugins':
        if len(matches) == 1:
            res = show_plugins()
            return bot.send_message(convo_id, res)
        if matches[1] == 'reload':
            bot.load_plugins()
            return bot.send_message(convo_id, 'Plugins has been reloaded')
        if matches[1] == 'enable':
            plugin_name = matches[2]
            bot.send_message(convo_id, add_plugin(plugin_name))
            return bot.send_message(convo_id, show_plugins())
        if matches[1] == 'disable':
            plugin_name = matches[2]
            bot.send_message(convo_id, remove_plugin(plugin_name))
            return bot.send_message(convo_id, show_plugins())


plugin = {
    "name": "Admin",
    "desc": "For admin",
    "usage": ["/plugins enable debug"],
    "run": run,
    "sudo": True,
    "patterns": [
        "^[!/#](plugins)$",
        "^[!/#](plugins) (enable) (.+?)$",
        "^[!/#](plugins) (disable) (.+?)$",
        "^[!/#](plugins) (reload)$",
    ],
    "action": [],
}
