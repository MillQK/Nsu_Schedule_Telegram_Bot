# -*- coding: utf-8 -*-
import config
import telebot
from telebot import types
from random import randint
import json
import pickledb


bot = telebot.TeleBot(config.token, threaded=config.bot_threaded)
groups_storage = pickledb.load('groups_storage.db', False)
with open('sch.txt', 'r') as inp:
    sch = json.load(inp)


def is_command(text):
    return text[0] == '/'


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
              '7': '6',
              'первая (9:00)': '0',
              'вторая (10:50)': '1',
              'третья (12:40)': '2',
              'четвертая (14:30)': '3',
              'пятая (16:20)': '4',
              'шестая (18:10)': '5',
              'седьмая (20:00)': '6'}

subjects_list = ['0', '1', '2', '3', '4', '5', '6']

EMPTY_SUBJ = 'empty_pair'
GROUP_NAME = 'group_name'

EMPTY_DAY_MESSAGE = 'В этот день пар нет.'
EMPTY_SUBJ_MESSAGE = 'Пустая пара.'


@bot.message_handler(func=lambda msg: len(msg.text.split()) > 1, commands=['sch'])
def get_schedule(message):
    information = message.text.split()

    if not check_and_correct_request(information):
        send_sch_error_message(message.chat.id)
        return

    answer = ''
    if len(information) == 2:
        dialog_group(message.chat.id, information[1])
    elif len(information) == 3:
        day = sch[information[1]][information[2]]
        for i in range(0, 7):
            answer += make_subject_message(day[str(i)]) + '\n\n'
    elif len(information) == 4:
        answer = make_subject_message(sch[information[1]][information[2]][information[3]])
    else:
        send_sch_error_message(message.chat.id)
        return

    # print(answer)
    bot.send_message(message.chat.id, answer)


chat_history = dict()


@bot.message_handler(commands=['sch'])
def schedule_custom_keyboard(message):
    sent = bot.send_message(message.chat.id, 'Введите вашу группу.', reply_markup=types.ReplyKeyboardHide())
    bot.register_next_step_handler(sent, dialog_group_check)


def dialog_group_check(message):
    group_num = message.text
    if is_command(message.text):
        return
    if group_num not in sch:
        bot.send_message(message.chat.id, 'Нет такой группы. Попробуйте еще раз.',
                         reply_markup=types.ReplyKeyboardHide())
        return
    dialog_group(message.chat.id, group_num)


def dialog_group(mchat_id, group):
    chat_history[mchat_id] = sch[group]
    markup = types.ReplyKeyboardMarkup()
    markup.row('Понедельник', 'Вторник')
    markup.row('Среда', 'Четверг')
    markup.row('Пятница', 'Суббота')
    # markup.row('Все дни')
    sent = bot.send_message(mchat_id, 'Выберете день недели', reply_markup=markup)
    bot.register_next_step_handler(sent, dialog_weekday)


def dialog_weekday(message):
    if is_command(message.text):
        return
    weekday = message.text.lower()
    if weekday not in days_dict:
        bot.send_message(message.chat.id, 'Нет такого дня недели. Попробуйте еще раз.',
                         reply_markup=types.ReplyKeyboardHide())
        return

    chat_history[message.chat.id] = chat_history[message.chat.id][days_dict[weekday]]

    if is_day_empty(chat_history[message.chat.id]):
        bot.send_message(message.chat.id, EMPTY_DAY_MESSAGE,
                         reply_markup=types.ReplyKeyboardHide())
        return

    markup = types.ReplyKeyboardMarkup()
    markup.row('Первая (9:00)', 'Вторая (10:50)')
    markup.row('Третья (12:40)', 'Четвертая (14:30)')
    markup.row('Пятая (16:20)', 'Шестая (18:10)')
    markup.row('Седьмая (20:00)', 'Все пары')
    sent = bot.send_message(message.chat.id, 'Выберете пару', reply_markup=markup)
    bot.register_next_step_handler(sent, dialog_answer)


def dialog_answer(message):
    if is_command(message.text):
        return
    subj = message.text.lower()
    if subj not in subjs_dict and subj != 'все пары':
        bot.send_message(message.chat.id, 'Нет такой пары. Попробуйте еще раз.', reply_markup=types.ReplyKeyboardHide())
        return

    day = chat_history[message.chat.id]
    if subj == 'все пары':
        answer = make_day_subjects_message(day)
    elif day[subjs_dict[subj]][1] == '':  # Пустая пара
        answer = '*{0}*: {1}'.format(day[subjs_dict[subj]][0], EMPTY_SUBJ_MESSAGE)
    else:
        answer = make_subject_message(day[subjs_dict[subj]])

    bot.send_message(message.chat.id, answer, reply_markup=types.ReplyKeyboardHide(), parse_mode='Markdown')


def send_sch_error_message(mid):
    error_massage = 'Использование: /sch <номер группы> <день недели (например: пн или понедельник или 1)' \
                    '(опционально)> <номер пары (цифрой, только если есть день недели)(опционально)>' \
                    '\nНапример: /sch 16202 пт 3\n\n' \
                    'Либо можете просто написать /sch и дальше взаимодействовать с ботом.'
    bot.send_message(mid, error_massage, reply_markup=types.ReplyKeyboardHide())


def check_and_correct_request(split_request):

    if len(split_request) == 1 or split_request[1] not in sch:
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

    if len(subj) == 2 and subj[1] != '':
        return '*{0}*:\n{1}'.format(subj[0], subj[1])
    elif len(subj) == 3:
        return '*{0}*:\n*Нечетная неделя*:\n{1}\n*Четная неделя*:\n{2}'.format(subj[0],
                'Пустая пара' if subj[1] == EMPTY_SUBJ else subj[1],
                'Пустая пара' if subj[2] == EMPTY_SUBJ else subj[2])
    else:
        return ''


def make_day_subjects_message(day):

    if is_day_empty(day):
        return EMPTY_DAY_MESSAGE

    message = ''
    for num_subj in subjects_list:
        ans = make_subject_message(day[num_subj])
        message += '{0}\n\n'.format(ans) if ans != '' else ''

    return message


def is_day_empty(day):
    for num_subj in subjects_list:
        cur_subj = day[num_subj]
        if len(cur_subj) == 2 and cur_subj[1] != '':
            return False
        elif len(cur_subj) == 3:
            return False

    return True


@bot.message_handler(func=lambda msg: len(msg.text.split()) > 1, commands=['setgroup'])
def set_group_in_msg(message):
    text = message.text.split()
    if len(text) > 2:
        setgroup_help_message(message.chat.id)
        return

    if text[1] not in sch:
        bot.send_message(message.chat.id, 'Нет такой группы.')
        return

    if save_data_in_storage(str(message.chat.id), GROUP_NAME, text[1]):
        bot.send_message(message.chat.id, 'Группа сохранена.')
    else:
        bot.send_message(message.chat.id, 'Возникла ошибка при сохранении. Попробуйте еще раз.')


@bot.message_handler(commands=['setgroup'])
def set_group_in_msg(message):
    text = message.text.split()
    if len(text) > 1:
        setgroup_help_message(message.chat.id)
        return

    if message.text == '/setgroup':
        send = bot.send_message(message.chat.id, 'Введите вашу группу.')
        bot.register_next_step_handler(send, set_group_in_msg)
    elif is_command(message.text):
        return
    else:
        group = message.text
        if group not in sch:
            bot.send_message(message.chat.id, 'Нет такой группы.')
            return

        if save_data_in_storage(str(message.chat.id), GROUP_NAME, group):
            bot.send_message(message.chat.id, 'Группа сохранена.')
        else:
            bot.send_message(message.chat.id, 'Возникла ошибка при сохранении. Попробуйте еще раз.')


def setgroup_help_message(mid):
    text = 'Использование: /setgroup <номер группы> или /setgroup'
    bot.send_message(mid, text)


def save_data_in_storage(storage_key, data_key, data_value):
    if storage_key not in groups_storage.getall():
        return groups_storage.set(storage_key, {data_key: data_value}) and groups_storage.dump()
    else:
        data = groups_storage.get(storage_key)
        data[data_key] = data_value
        return groups_storage.set(storage_key, data) and groups_storage.dump()


@bot.message_handler(commands=["mysch"])
def dialog_mysch(message):
    chat_id_str = str(message.chat.id)
    if chat_id_str not in groups_storage.getall():
        bot.send_message(message.chat.id, 'У вас неустановленна группа. Воспользуйтесь коммандой /setgroup.')
        return

    dialog_group(message.chat.id, groups_storage.get(chat_id_str)[GROUP_NAME])


@bot.message_handler(commands=["start"])
def repeat_all_messages(message):
    send_sch_error_message(message.chat.id)

# if __name__ == '__main__':
    # bot.polling(none_stop=True)