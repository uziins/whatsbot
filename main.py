# -*- coding: utf-8 -*-
import sys

from os.path import dirname, realpath
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth import AuthError
from yowsup.layers.axolotl.props import PROP_IDENTITY_AUTOTRUST
from yowsup.layers.interface import ProtocolEntityCallback, YowInterfaceLayer
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.protocol_contacts.protocolentities import GetSyncIqProtocolEntity
from yowsup.stacks import YowStackBuilder

import bot
from message import Message

WD = dirname(realpath(__file__))

config = bot.config
encryption = True


class WhatsBotLayer(YowInterfaceLayer):
    PROP_CONTACTS = "whatsapp.contacts"

    def __init__(self):
        super(WhatsBotLayer, self).__init__()

    @ProtocolEntityCallback("success")
    def on_success(self, success_entity):
        bot.set_entity(self)
        contacts = self.getProp(self.__class__.PROP_CONTACTS, [])
        contact_entity = GetSyncIqProtocolEntity(contacts)
        self._sendIq(contact_entity, self.on_sync_result, self.on_sync_error)
        bot.initialized.send(self)

    def on_sync_result(self, result_sync_iq_entity, original_iq_entity):
        pass

    def on_sync_error(self, error_sync_iq_entity, original_iq_entity):
        pass

    @ProtocolEntityCallback("message")
    def on_message(self, message_entity):
        bot.receive_message(self, message_entity)

        message = Message(message_entity)
        if message.valid:
            bot.message_received.send(message)
        bot.disconnect(self)

    @ProtocolEntityCallback("receipt")
    def on_receipt(self, entity):
        self.toLower(entity.ack())


class WhatStack(object):
    def __init__(self):
        builder = YowStackBuilder()

        self.stack = builder \
            .pushDefaultLayers(encryption) \
            .push(WhatsBotLayer) \
            .build()

        self.stack.setCredentials((config['credentials']['phone'], config['credentials']['password']))
        self.stack.setProp(WhatsBotLayer.PROP_CONTACTS, list(config['contacts'].keys()))
        self.stack.setProp(PROP_IDENTITY_AUTOTRUST, True)

    def start(self):
        print("%s started" % config['bot_name'])

        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

        try:
            self.stack.loop(timeout=0.5, discrete=0.5)
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt:
            print("Bot Stopped by You")
            sys.exit(0)


if __name__ == "__main__":
    wb = WhatStack()
    wb.start()
