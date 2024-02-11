from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from helpers import *
from aiogram.types import ParseMode
from functools import reduce, partial
import asyncio
import logging
import re
import html
import api_300
import uuid


def setup(dp: Dispatcher):
    dp.register_message_handler(bot_help, CommandHelp())
    dp.register_message_handler(bot_help, CommandStart())
    dp.register_message_handler(summarize_reply, commands=['theses'])
    dp.register_message_handler(fix_reply, commands=['fix'])
    dp.register_message_handler(improve_reply, commands=['improve'])
    dp.register_message_handler(shorten_reply, commands=['shorten'])
    dp.register_message_handler(
        echo, content_types=types.ContentTypes.ANY)
    dp.register_callback_query_handler(echo_callback, cb.filter())


async def bot_help(msg: types.Message):
    text = [
        'Привет, я простой бот для обработки текста. Отправьте какой-нибудь текст, а затем отправьте команду-реплай.\n\n'
        'Список команд: ',
        '/fix - исправить ошибки в тексте',
        '/improve - улучшить текст',
        '/shorten - сократить текст',
        '/theses - выделить тезисы из текста',
    ]

    await msg.reply('\n'.join(text))


def get_text(msg: types.Message) -> str:
    text = msg.caption if msg.text is None else msg.text
    if text is None:
        logging.info(msg)
        return None
    
    return text


async def summarize_reply(msg: types.Message):
    msg_reply = msg.reply_to_message

    if msg_reply is None:
        await msg.reply('Используй реплай, я не понял, что суммаризовать')
        return
    
    text = get_text(msg_reply)

    if text is None: return
    
    if len(text.split()) > 42: 
        summary = await api_300.get_summary(text)
    else:
        summary = None
                
    if summary is not None:
        await msg.reply(summary)
    else:
        await msg.reply('Сообщение слишком короткое или произошла ошибка')


async def fix_reply(msg: types.Message):
    msg_reply = msg.reply_to_message

    if msg_reply is None:
        await msg.reply('Используй реплай, я не понял с каким текстом работать')
        return
    
    text = get_text(msg_reply)

    if text is None: return
    
    
    result = await api_300.fix_text(text)
    
    await msg.reply(result)


async def improve_reply(msg: types.Message):
    msg_reply = msg.reply_to_message

    if msg_reply is None:
        await msg.reply('Используй реплай, я не понял с каким текстом работать')
        return
    
    text = get_text(msg_reply)

    if text is None: return
    
    
    result = await api_300.improve_text(text)
    
    await msg.reply(result)


async def shorten_reply(msg: types.Message):
    msg_reply = msg.reply_to_message

    if msg_reply is None:
        await msg.reply('Используй реплай, я не понял с каким текстом работать')
        return
    
    text = get_text(msg_reply)

    if text is None: return
    
    result = await api_300.short_text(text)
        
    await msg.reply(result)


async def echo(msg: types.Message):
    text = get_text(msg)

    text_id = str(uuid.uuid1())
    
    write_file(f'data/{text_id}', text)
    markup = get_inline_keyboard(text_id)

    await msg.reply('Вижу твой текст, давай начнем с ним работать:', reply_markup=markup)


cb = CallbackData('echo',"text_id", "action")
def get_inline_keyboard(text_id):
    # Creating a button
    buttons = [
        InlineKeyboardButton(text="Выделить тезисы", callback_data=cb.new(text_id=text_id, action='theses')),
        InlineKeyboardButton(text="Улучшить", callback_data=cb.new(text_id=text_id, action='improve')),
        InlineKeyboardButton(text="Сократить", callback_data=cb.new(text_id=text_id, action='shorten')),
        InlineKeyboardButton(text="Исправить", callback_data=cb.new(text_id=text_id, action='fix')),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    markup = keyboard.add(*buttons)
    return markup


async def echo_callback(call: types.CallbackQuery, callback_data: dict):
    text = read_file(f"data/{callback_data['text_id']}")
    action: str = callback_data['action']

    text_id = str(uuid.uuid1())

    try:
        match action:
            case 'theses':
                result = await api_300.get_summary(text)
            case 'improve':
                result = await api_300.improve_text(text)
            case 'shorten':
                result = await api_300.short_text(text)
            case 'fix':
                result = await api_300.fix_text(text)

        
        write_file(f'data/{text_id}', result)
        markup = get_inline_keyboard(text_id)

        await call.message.reply(result, reply_markup=markup)
    finally:
        await call.answer()