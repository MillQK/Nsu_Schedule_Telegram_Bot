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

subjs_dict = {'первая': '0',
              'вторая': '1',
              'третья': '2',
              'четвертая': '3',
              'пятая': '4',
              'шестая': '5',
              'седьмая': '6',
              '1': '0',
              '2': '1',
              '3': '2',
              '4': '3',
              '5': '4',
              '6': '5',
              '7': '6'}

EMPTY_SUBJ = 'empty_pair'


@bot.message_handler(commands=['sch'])
def get_schedule(message):
    information = message.text.split()

    if not check_and_correct_request(information):
        send_sch_error_message(message.chat.id)
        return

    answer = ''
    if len(information) == 3:
        day = sch[information[1]][information[2]]
        for i in range(0, 7):
            answer += make_subject_message(day[str(i)]) + '\n\n'
    elif len(information) == 4:
        answer = make_subject_message(sch[information[1]][information[2]][information[3]])
    else:
        send_sch_error_message(message.chat.id)
        return

    print(answer)
    bot.send_message(message.chat.id, answer)


def send_sch_error_message(mid):
    error_massage = 'Использование: /sch <номер группы> <день недели (например: пн или понедельник или 1)' \
                    '(опционально)> <номер пары (цифрой, только если есть день недели)(опционально)>' \
                    '\nНапример: /sch 16202 пт 3'
    bot.send_message(mid, error_massage)


def check_and_correct_request(split_request):

    if len(split_request) == 1 or not split_request[1] in sch:
        return False

    if len(split_request) > 2:
        split_request[2] = split_request[2].lower()
        if not split_request[2] in days_dict:
            return False
        else:
            split_request[2] = days_dict[split_request[2]]

    if len(split_request) > 3:
        split_request[3] = split_request[3].lower()
        if not split_request[3] in subjs_dict:
            return False
        else:
            split_request[3] = subjs_dict[split_request[3]]

    return True


def make_subject_message(subj):

    if len(subj) == 2:
        return subj[0] + ':\n' + subj[1]
    elif len(subj) == 3:
        return '{0}:\nНечетная неделя:\n{1}\nЧетная неделя:\n{2}'.format(subj[0],
                'Пустая пара' if subj[1] == EMPTY_SUBJ else subj[1],
                'Пустая пара' if subj[2] == EMPTY_SUBJ else subj[2])



@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(content_types=["start"])
def repeat_all_messages(message):
    send_sch_error_message(message.chat.id)

if __name__ == '__main__':
    with open('sch.txt', 'r') as inp:
        sch = json.load(inp)
    bot.polling(none_stop=True)
