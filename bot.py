# -*- coding: utf-8 -*-
import json
import time

import os
import random
import re
from blinker import signal
from os.path import join, realpath, dirname
from yowsup.common.optionalmodules import PILOptionalModule
from yowsup.common.tools import Jid
from yowsup.layers.protocol_chatstate.protocolentities import OutgoingChatstateProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities import GetStatusesIqProtocolEntity
from yowsup.layers.protocol_groups.protocolentities import SubjectGroupsIqProtocolEntity, InfoGroupsIqProtocolEntity, \
    LeaveGroupsIqProtocolEntity
from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.layers.protocol_media.protocolentities import RequestUploadIqProtocolEntity, \
    ImageDownloadableMediaMessageProtocolEntity, AudioDownloadableMediaMessageProtocolEntity, \
    VideoDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_presence.protocolentities import PresenceProtocolEntity, AvailablePresenceProtocolEntity, \
    UnavailablePresenceProtocolEntity
from yowsup.layers.protocol_profiles.protocolentities import SetPictureIqProtocolEntity, GetPictureIqProtocolEntity, \
    SetStatusIqProtocolEntity

import utils

WD = dirname(realpath(__file__))
config = {}
plugins = []
ack_queue = []
entity = None

initialized = signal('WhatsBot_initialized')
message_received = signal('message_received')


def get_config():
    global config
    file = open(join(WD, "data/config.json"), "r")
    config = json.loads(file.read())
    file.close()


def save_config():
    file = open(join(WD, "data/config.json"), "w")
    file.write(json.dumps(config))
    file.close()


def load_plugins():
    global plugins
    get_config()
    plugins = []
    for plugin_name in config['plugins']:
        plugin_dir = join(WD, "plugins", plugin_name + ".py")
        values = {}
        with open(plugin_dir, encoding="utf-8") as f:
            code = compile(f.read(), plugin_dir, 'exec')
            exec(code, values)
            f.close()
        plugin = values['plugin']
        plugins.append(plugin)
        print("Loading plugin: {}".format(plugin['name']))

    def sort_key(p):
        return p["name"]

    plugins.sort(key=sort_key)


def bot_init():
    get_config()
    if not os.path.exists(config['download_dir']):
        os.makedirs(os.path.join(config['download_dir'], 'images'))
        os.makedirs(os.path.join(config['download_dir'], 'profiles'))


bot_init()
db = utils.MySQL(config['database']['db_host'], config['database']['db_name'], config['database']['db_user'],
                 config['database']['db_password'])
db.init_database()


def set_entity(instance):
    global entity
    entity = instance


def receive_message(wbot, message_entity):
    wbot.toLower(message_entity.ack())
    # Add message to queue to ACK later
    ack_queue.append(message_entity)


def prepare_answer(wbot, chat_id, disconnect_after=True):
    # Set name Presence
    make_presence(wbot)

    # Set online
    online(wbot)
    time.sleep(random.uniform(0.1, 0.4))

    # Set read (double v blue)
    ack_messages(wbot, chat_id)

    # Set is writing
    start_typing(wbot, chat_id)
    time.sleep(random.uniform(0.5, 1.4))

    # Set it not writing
    stop_typing(wbot, chat_id)

    if disconnect_after:
        disconnect(wbot)


def make_presence(wbot):
    wbot.toLower(PresenceProtocolEntity(name=config['bot_name']))


def online(wbot):
    wbot.toLower(AvailablePresenceProtocolEntity())


def disconnect(wbot):
    wbot.toLower(UnavailablePresenceProtocolEntity())


def start_typing(wbot, conversation):
    wbot.toLower(OutgoingChatstateProtocolEntity(
        OutgoingChatstateProtocolEntity.STATE_TYPING,
        Jid.normalize(conversation)
    ))


def stop_typing(wbot, conversation):
    wbot.toLower(OutgoingChatstateProtocolEntity(
        OutgoingChatstateProtocolEntity.STATE_PAUSED,
        Jid.normalize(conversation)
    ))


def ack_messages(wbot, conversation):
    # Filter messages from this conversation
    queue = [message_entity for message_entity in ack_queue if same_conversation(message_entity, conversation)]

    # Get only last 20 messages (Will discard reading the others)
    queue = queue[-20:]

    # Ack every message in queue
    for message_entity in queue:
        wbot.toLower(message_entity.ack(True))

        # Remove it from queue
        if message_entity in ack_queue:
            ack_queue.remove(message_entity)

    # Clean queue
    remove_conversation_from_queue(conversation)


def same_conversation(message_entity, conversation):
    return message_entity.getFrom() == conversation


def remove_conversation_from_queue(conversation):
    ack_queue[:] = [entity for entity in ack_queue if not same_conversation(entity, conversation)]


def decode_string(message):
    try:
        if type(message) is bytes:
            message = message.decode(encoding='latin1', errors='ignore')
        return message
    except:
        return message.decode('utf-8', 'ignore').encode("utf-8")


def send_message(convo_id, text, disconnect_after=True):
    msg = decode_string(text)

    # Prepare mac to answer (Human behavior)
    prepare_answer(entity, convo_id, disconnect_after)
    entity.toLower(TextMessageProtocolEntity(msg, to=convo_id))


def send_message_to(str_message, phone_number, disconnect_after=True):
    jid = Jid.normalize(phone_number)
    send_message(str_message, jid)


def send_image(path, convo_id, caption=None):
    if os.path.isfile(path):
        media_send(entity, convo_id, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE, caption)
    else:
        print("Image doesn't exists")


def send_image_to(path, phone_number, caption=None):
    jid = Jid.normalize(phone_number)
    send_image(path, jid, caption)


def send_video(path, convo_id, caption=None):
    if os.path.isfile(path):
        media_send(entity, convo_id, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO)
    else:
        print("Video doesn't exists")


def send_video_to(path, phone_number, caption=None):
    jid = Jid.normalize(phone_number)
    send_video(path, jid, caption)


# Still not supported

# def send_document(path, convo_id):
#     if os.path.isfile(path):
#         media_send(entity, convo_id, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_DOCUMENT)
#     else:
#         print("Document doesn't exists")
#
#
# def send_audio(path, conversation):
#     if os.path.isfile(path):
#         media_send(entity, conversation, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO)
#     else:
#         print("Audio file doesn't exists")
#
#
# def send_audio_to(path, phone_number):
#     jid = Jid.normalize(phone_number)
#     send_audio(path, jid)


# End of Not Supported


def media_send(wbot, jid, path, media_type, caption=None):
    media_entity = RequestUploadIqProtocolEntity(media_type, filePath=path)
    fn_success = lambda success_entity, original_entity: on_request_upload_result(wbot, jid, media_type, path,
                                                                                  success_entity, original_entity,
                                                                                  caption)
    fn_error = lambda error_entity, original_entity: on_request_upload_error(wbot, jid, path, error_entity,
                                                                             original_entity)
    wbot._sendIq(media_entity, fn_success, fn_error)


# CONTACTS / PROFILES
def set_status(text):
    def on_success(resultIqEntity, originalIqEntity):
        # print("Status updated successfully")
        pass

    def on_error(errorIqEntity, originalIqEntity):
        # print("Error updating status")
        pass

    entity._sendIq(SetStatusIqProtocolEntity(text[:250]), on_success, on_error)


def contact_picture(conversation, success_fn=None, preview=False):
    iq = GetPictureIqProtocolEntity(conversation, preview=preview)

    def got_picture(result_picture, picture_protocol_entity):
        path = os.path.join(config['download_dir'], 'profiles/%s_%s.jpg' % (
            picture_protocol_entity.getTo(), "preview" if result_picture.isPreview() else "full"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        result_picture.writeToFile(path)
        if success_fn:
            success_fn(picture_protocol_entity.getTo(), path)

    entity._sendIq(iq, got_picture)


def contact_picture_from(number, success_fn=None, preview=False):
    jid = Jid.normalize(number)
    contact_picture(jid, success_fn, preview)


def set_profile_pricture(path, success=None, error=None):
    picture, preview = make_picture_and_preview(path)
    entity._sendIq(SetPictureIqProtocolEntity(entity.getOwnJid(), preview, picture), success, error)


def set_group_picture(path, group_jid, success=None, error=None):
    picture, preview = make_picture_and_preview(path)
    entity._sendIq(SetPictureIqProtocolEntity(group_jid, preview, picture), success, error)


def set_group_subject(group_jid, subject):
    entity.toLower(SubjectGroupsIqProtocolEntity(group_jid, subject))


def make_picture_and_preview(path):
    with PILOptionalModule(failMessage="No PIL library installed, try install pillow") as imp:
        image = imp("Image")
        src = image.open(path)
        picture = src.resize((640, 640)).tobytes("jpeg", "RGB")
        preview = src.resize((96, 96)).tobytes("jpeg", "RGB")
        return picture, preview


def contact_status(jids, fn=None):
    def success(result, original):
        if fn:
            fn(result.statuses)

    if isinstance(jids, list):
        iq = GetStatusesIqProtocolEntity(jids)
        entity._sendIq(iq, success)
    else:
        iq = GetStatusesIqProtocolEntity([jids])
        entity._sendIq(iq, success)


def contact_status_from(number, fn=None):
    jid = Jid.normalize(number)
    contact_status(jid, fn)


# Groups
def leave_group(group_jid):
    entity.toLower(LeaveGroupsIqProtocolEntity(group_jid))


# callback - Leave as it
def on_request_upload_result(wbot, jid, media_type, file_path, result_request_upload_entity,
                             request_upload_entity, caption=None):
    if result_request_upload_entity.isDuplicate():
        do_send_media(wbot, media_type, file_path, result_request_upload_entity.getUrl(), jid,
                      result_request_upload_entity.getIp(), caption)
    else:
        success_fn = lambda file_path, jid, url: do_send_media(wbot, media_type, file_path, url, jid,
                                                               result_request_upload_entity.getIp(), caption)
        media_uploader = MediaUploader(jid, wbot.getOwnJid(), file_path, result_request_upload_entity.getUrl(),
                                       result_request_upload_entity.getResumeOffset(), success_fn,
                                       on_upload_error(wbot, file_path, jid),
                                       on_upload_progress(wbot, file_path, jid,
                                                          result_request_upload_entity.getResumeOffset()), async=True)
        media_uploader.start()


def on_request_upload_error(wbot, jid, path, error_request_upload_iq_entity, request_upload_iq_entity):
    return


def do_send_media(wbot, media_type, file_path, url, to, ip=None, caption=None):
    if media_type == RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE:
        media_entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, ip, to, caption=caption)
        wbot.toLower(media_entity)
    elif media_type == RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO:
        media_entity = AudioDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, ip, to)
        wbot.toLower(media_entity)
    elif media_type == RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO:
        media_entity = VideoDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, ip, to, caption=caption)
        wbot.toLower(media_entity)


def on_upload_error(wbot, filePath, jid):
    return


def on_upload_progress(wbot, filePath, jid, progress):
    return


def user_insert(message):
    msg_type, convo_id, user_id = utils.glance(message)
    db.db_query(
        "INSERT INTO user (user_id, phone_number, display_name, user_type) VALUES ('{}', '{}', '{}', '{}')".format(
            user_id, message.phone_number, message.display_name, 'user'), 'commit')
    db.db_query("INSERT INTO preference (user_id, phone_number, display_name, state, pref_data) VALUES "
                "('{}', '{}', '{}', '{}', '{}')".format(user_id, message.phone_number, message.display_name, 'init',
                                                        json.dumps({})), 'commit')


def user_chat_insert(message):
    db.db_query(
        "INSERT INTO user (user_id, phone_number, display_name, user_type) VALUES ('{}', '{}', '{}', '{}')".format(
            message.chat_id, message.phone_number, message.chat_id, 'group'), 'commit')
    db.db_query("INSERT INTO preference (user_id, phone_number, display_name, state, pref_data) VALUES "
                "('{}', '{}','{}', '{}', '{}')".format(message.chat_id, message.phone_number, message.chat_id, 'init',
                                                       json.dumps({})))


def user_validation(message):
    chat_data, user_data = db.user_check(message)
    if message.message_entity.isGroupMessage():
        if chat_data:
            pass
        else:
            user_chat_insert(message)
        if not user_data:
            user_insert(message)
    else:
        if user_data:
            pass
        else:
            user_insert(message)
    return utils.ChatAndUserData(chat_data) if chat_data else None, utils.ChatAndUserData(
        user_data) if user_data else None


def is_sudo(user_id):
    if user_id in config['sudo_user']:
        return True
    return False


def process_message(message):
    chat_data, user_data = user_validation(message)
    msg_type, convo_id, user_id = utils.glance(message)
    # print(msg_type)
    if not chat_data or not user_data:
        print('Just registering to database')
        chat_data, user_data = user_validation(message)
    for plugin in plugins:
        if plugin['sudo']:
            if is_sudo(user_id):
                pass
            else:
                continue
        if msg_type == 'text':
            for pattern in plugin['patterns']:
                if re.search(pattern, message.text, re.IGNORECASE | re.MULTILINE):
                    matches = re.findall(pattern, message.text, re.IGNORECASE)
                    match = matches[0] if type(matches[0]) is tuple else (matches[0],)
                    plugin['run'](message, match, convo_id, chat_data, user_data)
                    break
        else:
            if msg_type in plugin['action']:
                plugin['run'](message, (msg_type,), convo_id, chat_data, user_data)


@message_received.connect
def handle(message):
    process_message(message)


load_plugins()
