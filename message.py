import utils
import bot


class Message(object):
    def __init__(self, message_entity):
        self.user_id = utils.get_sender_id(message_entity)
        self.display_name = utils.sender_name(message_entity)
        self.phone_number = utils.get_phone_number(message_entity)
        self.conversation = message_entity.getFrom()
        self.chat_id = utils.get_chat_id(message_entity)
        self.chat_type = 'group' if message_entity.isGroupMessage() else 'user'
        self.type = message_entity.getMediaType() if utils.is_media_message(message_entity) else 'text'
        self.message_entity = message_entity
        self.valid = False
        self.message = ""
        self.text = ""
        self.file_path = None
        self.command = None

        self.build()

    def build(self):
        if utils.is_text_message(self.message_entity):
            self.build_text_message()
        elif utils.is_media_message(self.message_entity):
            self.build_media_message()
        else:
            print("Unsupported message")

    """
    Builds text message
    """

    def build_text_message(self):
        self.message = utils.clean_message(self.message_entity)
        self.text = utils.clean_message(self.message_entity)
        self.valid = True

    """
    Tries to build the media message. If fails, builds the text message
    """

    def build_media_message(self):
        if hasattr(self.message_entity, 'getMediaUrl'):
            if utils.is_image_media(self.message_entity):
                self.file_path = utils.get_file(self.message_entity, bot.config['download_dir'])
                self.text = self.message_entity.getCaption()
                self.message = self.message_entity.getCaption()
            elif utils.is_location_media(self.message_entity):
                print(self.message_entity)
            self.valid = True
        else:
            self.build_text_message()
