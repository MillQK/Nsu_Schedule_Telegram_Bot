# -*- coding: utf-8 -*-
import config
import telebot
from random import randint
import json

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['fcoin'])
def flip_coin(message):
    coin = randint(0, 1)
    if coin:
        bot.send_message(message.chat.id, 'Орел')
    else:
        bot.send_message(message.chat.id, 'Решка')


days_dict = {'понедельник': '1',
                'вторник': '2',
                'среда': '3',
                'четверг': '4',
                'пятница': '5',
                'суббота': '6',
                'пн': '1',
                'вт': '2',
                'ср': '3',
                'чт': '4',
                'пт': '5',
                'сб': '6',
                '1': '1',
                '2': '2',
                '3': '3',
                '4': '4',
                '5': '5',
                '6': '6'}


@bot.message_handler(commands=['sch'])
def get_schedule(message):
    information = message.text.split()

    if len(information) == 1 or not information[1] in sch:
        send_sch_error_message(message.chat.id)
        return

    if len(information) > 2:
        information[2] = information[2].lower()

    if not information[2] in days_dict:
        send_sch_error_message(message.chat.id)
        return

    answer = ''
    if len(information) == 3:
        day = sch[information[1]][information[2]]
        for i in range(0, 7):
            answer += day[str(i)] + '\n\n'
    elif len(information) == 4:
        answer = sch[information[1]][information[2]][information[3]]
    print(answer)
    bot.send_message(message.chat.id, answer)


def send_sch_error_message(mid):
    error_massage = 'Использование: /sch <номер группы> <день недели (например: пн или понедельник или 1)' \
                    '(опционально)> <номер пары (цифрой, только если есть день недели)(опционально)>' \
                    '\nНапример: /sch 16202 пт 3'
    bot.send_message(mid, error_massage)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    with open('sch.txt', 'r') as inp:
        sch = json.load(inp)
    bot.polling(none_stop=True)
