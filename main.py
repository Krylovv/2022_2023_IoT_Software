#!/usr/bin/python3

import configparser
import json
import requests
import re
from telethon.sync import TelegramClient


# для корректного переноса времени сообщений в json
from datetime import datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest


# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id = int(config['Telegram']['api_id'])
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, api_id, api_hash)

client.start()


async def dump_all_participants(channel):
    """Записывает json-файл с информацией о всех участниках канала/чата"""
    offset_user = 0    # номер участника, с которого начинается считывание
    limit_user = 100   # максимальное число записей, передаваемых за один раз

    all_participants = []   # список всех участников канала
    filter_user = ChannelParticipantsSearch('')

    while True:
        participants = await client(GetParticipantsRequest(channel,
                                    filter_user, offset_user, limit_user, hash=0))
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset_user += len(participants.users)

    all_users_details = []   # список словарей с интересующими параметрами участников канала

    for participant in all_participants:
        all_users_details.append({"id": participant.id,
                                  "first_name": participant.first_name,
                                  "last_name": participant.last_name,
                                  "user": participant.username,
                                  "phone": participant.phone,
                                  "is_bot": participant.bot})

    with open('channel_users.json', 'w', encoding='utf8') as outfile:
        json.dump(all_users_details, outfile, ensure_ascii=False, indent=4)


async def dump_all_messages(channel):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    offset_msg = 0    # номер записи, с которой начинается считывание
    limit_msg = 100   # максимальное число записей, передаваемых за один раз

    all_messages = []   # список всех сообщений
    total_count_limit = 500  # поменяйте это значение, если вам нужны не все сообщения

    class DateTimeEncoder(json.JSONEncoder):
        # Класс для сериализации записи дат в JSON
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        all_messages.reverse()
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    with open('channel_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder, indent=4)


def remove_newlines(value):
    value = value.replace("\n", " ").replace('\r\n', ' ').replace("\"", "").replace("»", "").replace("«", "")
    return value


def json_parser(filename):
    text = ""
    with open(filename, 'r') as file:
        chat = json.loads(file.read())
        for i in chat:
            keys = list(i.keys())
            if 'message' in keys:
                if i['message'] != "":
                    if datetime.today().strftime('%Y-%m-%d') in i['date']:
                        tmp = i['message']
                        tmp = remove_newlines(tmp)
                        text += (tmp + " ")
        return text

    
def summary_text():
    url = "https://api.aicloud.sbercloud.ru/public/v2/summarizator/predict"
    f = open("text.txt", "r", encoding='utf8')
    text = f.read()
    payload = json.dumps({
      "instances": [
          {"text": text,
           "num_beams": 5,
           "num_return_sequences": 20,
           "length_penalty": 1.0
           }
        ]
      })
    headers = {
      'Content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_obj = json.loads(response.text)
    print(response_obj['prediction_best']['bertscore'])
    return response_obj['prediction_best']['bertscore']

def get_link():
    f = open("link.txt", "r", encoding='utf8')
    text = f.read()
    return text

async def parse():
    url = get_link()
    channel = await client.get_entity(url)
    await dump_all_messages(channel)
    text = json_parser('channel_messages.json')
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
                               
    text = (emoji_pattern.sub(r'', text))  # no emoji
    f = open("text.txt", "w")
    f.write(text)
    f.close()
    summary = summary_text()
    r = open("result.txt", "w", encoding='utf8')
    r.write(summary)
    r.close()

with client:
    client.loop.run_until_complete(parse())
