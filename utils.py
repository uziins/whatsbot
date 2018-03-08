# Media Decrypter
import datetime
import json

import os
import pymysql
import sys


def pad(stream):
    x = (16 - len(stream) % 16) * chr(16 - len(stream) % 16)
    return stream + x.encode()


# Utils
def get_sender_id(message_entity):
    user_id = message_entity.getFrom()
    if message_entity.isGroupMessage():
        user_id = message_entity.getParticipant()

    return user_id


def get_phone_number(message_entity):
    user_id = message_entity.getFrom().split('@')
    return user_id[0] if not message_entity.isGroupMessage() else None


def sender_name(message_entity):
    name = message_entity.getNotify()
    name = name.encode('latin-1')
    name = name.decode('utf-8')
    return name


def get_conversation(message_entity):
    return message_entity.getFrom()


"""
Detects if the message entity is text type.
"""


def is_text_message(message_entity):
    return message_entity.getType() == "text"


def is_media_message(message_entity):
    return message_entity.getType() == "media"


def is_image_media(message_entity):
    if is_media_message(message_entity):
        return message_entity.getMediaType() == "image"


def is_location_media(message_entity):
    if is_media_message(message_entity):
        return message_entity.getMediaType() == "location"


def is_vcard_media(message_entity):
    if is_media_message(message_entity):
        return message_entity.getMediaType() == "vcard"


"""
Cleans all the garbage and non-ASCII characters in the message (idk why whatsapp appends all that garbage)
"""


def clean_message(message_entity):
    message = message_entity.getBody()
    message = message.strip()
    # message = ''.join(filter(lambda x: x in string.printable, message))
    return message


"""
Get chat_id, so group is only group id, without user number.
It can't be used for sending message or other action, just make it clear and easy use when identity needed
"""


def get_chat_id(message_entity):
    if message_entity.isGroupMessage():
        chat_id = message_entity.getFrom().split('-')[1]
    else:
        chat_id = message_entity.getFrom()
    return chat_id


# Downloader

"""
Downloads file
"""


def get_file(message_entity, download_dir):
    if is_image_media(message_entity):
        ts = int(datetime.datetime.now().timestamp())
        file_path = os.path.join(download_dir, 'images/%s.jpg' % ts)
        try:
            f = open(file_path, 'wb')
            f.write(message_entity.getMediaContent())
            f.close()
            return file_path
        except Exception as e:
            print(e)
            return None
    else:
        return None


def glance(message):
    msg_type = message.message_entity.getMediaType() if is_media_message(message.message_entity) else 'text'
    if message.message_entity.isGroupMessage():
        user_id = message.message_entity.getParticipant()
    else:
        user_id = message.message_entity.getFrom()
    convo_id = message.message_entity.getFrom()
    return msg_type, convo_id, user_id


class MySQL:
    __doc__ = 'MySQL bridge'
    query = None
    method = None
    message = None

    def __init__(self, db_host=None, db_name=None, db_user=None, db_password=None):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password

    def db_query(self, query, method=None):
        self.query = query
        self.method = method
        result = False
        conn = pymysql.connect(self.db_host, self.db_user, self.db_password, self.db_name,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        try:
            if method == 'commit' or method == 'insert':
                with conn.cursor() as cursor:
                    cursor.execute(query)
                conn.commit()
                result = cursor.lastrowid
            elif method == 'fetchall':
                with conn.cursor() as cursor:
                    cursor.execute(query)
                result = cursor.fetchall()
            elif method == 'update':
                with conn.cursor() as cursor:
                    cursor.execute(query)
                conn.commit()
                result = cursor.rowcount
            else:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                result = cursor.fetchone()
        finally:
            conn.close()
            return result

    def init_database(self):
        if not self.db_host or not self.db_name or not self.db_user or not self.db_password:
            sys.exit("Need to specify mysql config")
        if not self.db_query("SHOW DATABASES LIKE '{}'".format(self.db_name)):
            self.db_query("CREATE DATABASE IF NOT EXISTS {} CHARACTER SET utf8mb4 "
                          "COLLATE utf8mb4_unicode_ci;".format(self.db_name), "commit")
        if not self.db_query("SHOW TABLES LIKE 'user'"):
            print("Attempting to create table 'user'")
            self.db_query("CREATE TABLE IF NOT EXISTS user("
                          "user_id VARCHAR(50) PRIMARY KEY, "
                          "phone_number VARCHAR(15),"
                          "display_name VARCHAR(50),"
                          "user_type VARCHAR(10),"
                          "updated_at DATETIME,"
                          "created_at TIMESTAMP DEFAULT current_timestamp NOT NULL)ENGINE = INNODB", "commit")
        if not self.db_query("SHOW TABLES LIKE 'preference'"):
            print("Attempting to create table 'preference'")
            self.db_query("CREATE TABLE IF NOT EXISTS preference("
                          "id INT PRIMARY KEY AUTO_INCREMENT,"
                          "user_id VARCHAR(50), "
                          "phone_number VARCHAR(15),"
                          "display_name VARCHAR(50),"
                          "state VARCHAR(100), "
                          "pref_data JSON DEFAULT NULL ,"
                          "updated_at DATETIME,"
                          "created_at TIMESTAMP DEFAULT current_timestamp,"
                          "FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE)ENGINE=INNODB", "commit")

    def user_check(self, message=None):
        self.message = message
        result = False
        if not self.message:
            return result
        sql = "SELECT * FROM user LEFT JOIN preference ON user.user_id = preference.user_id WHERE user.user_id = '{}'"
        if message.message_entity.isGroupMessage():
            chat_data = self.db_query(sql.format(message.chat_id))
            user_data = self.db_query(sql.format(message.user_id))
            return chat_data, user_data
        else:
            chat_data = self.db_query(sql.format(message.chat_id))
            user_data = chat_data
            return chat_data, user_data


class ChatAndUserData:
    def __init__(self, data):
        self.user_id = data['user_id']
        self.phone_number = data['phone_number']
        self.display_name_default = data['display_name']
        self.user_type = data['user_type']
        self.updated_at_default = data['updated_at']
        self.created_at_default = data['created_at']
        self.id = data['id']
        self.display_name = data['preference.display_name']
        self.state = data['state']
        self.pref_data = json.loads(data['pref_data']) if data['pref_data'] else json.loads('{}')
        self.updated_at = data['preference.updated_at']
        self.created_at = data['preference.created_at']

    def user_id(self):
        return self.user_id

    def phone_number(self):
        return self.phone_number

    def display_name_default(self):
        return self.display_name_default

    def user_type(self):
        return self.user_type

    def updated_at_default(self):
        return self.updated_at_default

    def created_at_default(self):
        return self.created_at_default

    def id(self):
        return self.id

    def display_name(self):
        return self.display_name

    def state(self):
        return self.state

    def pref_data(self):
        return self.pref_data

    def updated_at(self):
        return self.updated_at

    def created_at(self):
        return self.created_at

