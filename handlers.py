from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from helpers import *
from aiogram.types import ParseMode
from functools import reduce, partial
import asyncio
import logging
import re
import html
import api_300


def setup(dp: Dispatcher):
    dp.register_message_handler(bot_help, CommandHelp())
    dp.register_message_handler(bot_help, CommandStart())
    dp.register_message_handler(summarize_reply, commands=['theses'])
    dp.register_message_handler(fix_reply, commands=['fix'])
    dp.register_message_handler(improve_reply, commands=['improve'])
    dp.register_message_handler(shorten_reply, commands=['shorten'])


async def bot_help(msg: types.Message):
    text = [
        'Привет, я простой бот для обработки текста. Отправьте какой-нибудь текст, а затем отправьте команду-реплай.\n'
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