import os
from typing import Union

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram import ParseMode, Message, VideoNote, Document, Video
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters, InlineQueryHandler
import telegram
from mallard import Mallard
from stickers import file2sticker, file2animated_sticker, quote2sticker, video2emoji, image2emoji, FilePreprocessType
from content.emoji_dict import EMOJI_LIST
import random
import re
from stickers import VideoQuoteArguments, PhotoQuoteArguments
from exceptions import ProcessingException
from content.bubbles.bubbles import BUBBLES_COUNT
from uuid import uuid4
from responses import *

mallard = Mallard(random_answer_rate=150)

token = os.environ.get('TG_API_KEY')
admin_id = os.environ.get('TG_ADMIN_ID')


def sticker2emoji_echo(update: Update, context: CallbackContext):
    if update.message.reply_to_message is None or update.message.reply_to_message.sticker is None \
            or update.message.reply_to_message.sticker.is_animated or update.message.chat.type != 'private':
        return

    sticker = update.message.reply_to_message.sticker
    print(sticker)
    if sticker.is_video:
        arguments = parse_video_arguments(update.message.text)
        emoji = video2emoji(sticker.file_id, context)
        update.message.reply_document(document=emoji, filename=str(uuid4()) + '.webm')

    fid = sticker.file_id
    if sticker.is_video and sticker.thumb is not None and sticker.thumb.file_id is not None:
        fid = sticker.thumb.file_id
    emoji = image2emoji(fid, context)
    update.message.reply_document(document=emoji)


def download_voice(update: Update, context: CallbackContext, name=str(uuid4())):
    print(update.message)
    if update.message.reply_to_message is None or update.message.reply_to_message.voice is None \
            or update.message.chat.type != 'private':
        return
    print('ok')
    original_message = update.message.reply_to_message
    file_bytes = context.bot.getFile(original_message.voice.file_id).download_as_bytearray()
    with open(f'voices/{name}.ogg', 'wb') as f:
        f.write(file_bytes)


def echo(update: Update, context: CallbackContext):
    text = update.message.text if update.message.text is not None else update.message.caption
    if text is None:
        return
    reply, reply_type = mallard.process(text)
    if reply is not None and reply_type is not None:
        if reply_type == ResponseType.STICKER:
            context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=reply,
                                     reply_to_message_id=update.effective_message.message_id)
        elif reply_type == ResponseType.TEXT:
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply,
                                     reply_to_message_id=update.effective_message.message_id)
        elif reply_type == ResponseType.VOICE:
            with open(f'voices/{reply}.ogg', 'rb') as f:
                context.bot.send_voice(chat_id=update.effective_chat.id, voice=f.read(),
                                       reply_to_message_id=update.effective_message.message_id)


def command(update: Update, context: CallbackContext):
    # print(update)
    if update.message.text[:5] == '/snap':  # you are going to my collection
        quote(update, context)
    elif update.message.text[:4] == '/qwa' or update.message.text[:4] == '/qva':
        video_quote(update, context)
    elif update.message.text == f'/help{context.bot.name}' \
            or (update.message.text == f'/help' and update.message.chat.type == 'private'):
        help(update, context)
    elif update.message.text == '/id':
        get_sticker_id(update, context)
    elif update.message.text.split(' ')[0] == '/voice':
        download_voice(update, context, name=update.message.text.split(' ')[1])
    elif update.message.text == '/emoji':
        sticker2emoji_echo(update, context)


def help(update: Update, context: CallbackContext):
    reply = 'Кряква умеет превращать кружочки, гифки, видео и картинки в стикеры.\n\
Используйте /qva для анимированных стикеров и /snap для обычных.\n\
Используйте /emoji в ответ на стикер, чтобы преобразовать его в формат, подходящий для кастомных эмодзи (реакций).\n\
При использовании /qva вы также можете использовать параметры:\n\
* s<sec> обрежет видео начиная с sec, sec должно быть целым\n\
* e<sec> обрежет видео до sec, sec должно быть целым\n\
* x<speed> изменит скорость видео на speed, speed может иметь вид 123.123\n\
* r — если указан, видео будет инвертировано\n\
* b<id> — добавляет пузырёк, 1 — справа, 2 — сверху\n\
* j — если указан, преобразует видео/фото в формат, подходящий для кастомных эмодзи\n\
* например /qva s5 e7 x2.5 r обрежет видео с 5 по 7 секунды, инвертирует полученный фрагмент и ускорит его в два с половиной раза\n\
кря-кря.'
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply,
                             reply_to_message_id=update.effective_message.message_id)


def edit_exception(wait_message: telegram.message = None, exception: ProcessingException = None):
    if wait_message is not None and exception is not None:
        wait_message.edit_text(text=str(exception))


def reply_exception(reply_message: telegram.message = None, exception: ProcessingException = None,
                    context: CallbackContext = None, update: Update = None):
    if reply_message is not None and exception is not None and context is not None and update is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(exception),
                                 reply_to_message_id=update.effective_message.message_id)


def parse_video_arguments(line: str) -> VideoQuoteArguments:
    result = VideoQuoteArguments()
    words = line.split()
    for word in words[1:]:
        if (it := re.search(r's\d+', word)) is not None:
            result.set_field('starting_point', int(it.string[1:]))
        elif (it := re.search(r'e\d+', word)) is not None:
            result.set_field('end_point', int(it.string[1:]))
        elif (it := re.search(r'x\d+\.?\d*', word)) is not None:
            result.set_field('speed', float(it.string[1:]))
        elif (it := re.search(r'b\d*', word)) is not None:
            result.set_field('speech_bubble',
                             random.randint(0, BUBBLES_COUNT - 1) if it.string == 'b' else int(it.string[1:]) - 1)
        elif word == 'r':
            result.set_field('reverse', True)
        elif word == 'j':
            result.set_field('is_emoji', True)
        else:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message=f'"{word}" не подходит как аргумент для команды.')
    result.validate()
    return result


def parse_photo_arguments(line: str) -> PhotoQuoteArguments:
    result = PhotoQuoteArguments()
    words = line.split()
    for word in words[1:]:
        if (it := re.search(r'b\d*', word)) is not None:
            result.set_field('speech_bubble',
                             random.randint(0, BUBBLES_COUNT - 1) if it.string == 'b' else int(it.string[1:]) - 1)
        elif word == 'j':
            result.set_field('is_emoji', True)
        else:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message=f'"{word}" не подходит как аргумент для команды.')

    return result


def get_video(message: Message) -> Union[VideoNote, Document, Video]:
    if message is None:
        raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)
    video = message.video_note if message.video_note else message.document if message.document else message.video
    if video is None:
        raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)
    if video.file_size > 10485760:  # 10mb
        raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.file_too_large)
    return video


def add_and_delete_sticker(update: Update, context: CallbackContext, sticker, animated: bool = False):
    sticker_set_name = f"{'animated' if animated else 'image'}_stickerpack_by_{context.bot.name[1:]}"
    if context.bot.get_sticker_set(sticker_set_name) is None:
        context.bot.create_new_sticker_set(user_id=admin_id, name=sticker_set_name, title='Sticker by @cryakwa_bot',
                                           webm_sticker=sticker,
                                           emojis="\U0001F60C")
    kwargs = {'user_id': admin_id,
              'name': sticker_set_name,
              'webm_sticker' if animated else 'png_sticker': sticker,
              'emojis': EMOJI_LIST[random.randint(0, len(EMOJI_LIST) - 1)]}
    context.bot.addStickerToSet(**kwargs)
    sticker_set = context.bot.get_sticker_set(sticker_set_name)
    update.message.reply_sticker(reply_to_message_id=update.effective_message.message_id,
                                 sticker=sticker_set.stickers[-1])
    for sticker in sticker_set.stickers[1:]:
        context.bot.delete_sticker_from_set(sticker.file_id)


def video_quote(update: Update, context: CallbackContext):
    waiting_text = "Ваш запрос очень кважен для нас, оставайтесь на линии!"
    message = update.message
    wait_message = context.bot.send_message(chat_id=update.effective_chat.id, text=waiting_text,
                                            reply_to_message_id=update.effective_message.message_id)
    try:
        file = get_video(message.reply_to_message)
        arguments = parse_video_arguments(message.text)
        sticker = file2animated_sticker(file.file_id, context, preprocess_type=FilePreprocessType.circle,
                                        video_arguments=arguments)
        if sticker is None:
            raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)

        if arguments.is_emoji:
            update.message.reply_document(reply_to_message_id=update.effective_message.message_id,
                                          document=sticker, filename=str(uuid4()) + '.webm')
        else:
            add_and_delete_sticker(update, context, sticker, animated=True)

        wait_message.delete()
    except ProcessingException as e:
        edit_exception(wait_message=wait_message, exception=e)
        return
    except Exception as e:
        print(e)
        edit_exception(wait_message=wait_message, exception=ProcessingException(
            exception_type=ProcessingException.ProcessingExceptionType.unexpected))
        return


def get_author(message: Message) -> str:
    if message.forward_sender_name:
        return message.forward_sender_name
    if message.from_user and message.from_user.full_name:
        return message.from_user.full_name
    return 'unknown'


def quote(update: Update, context: CallbackContext):
    message = update.message
    # print(message)
    try:
        original_message = message.reply_to_message
        if original_message is None:
            raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)

        arguments = parse_photo_arguments(message.text)
        if text := original_message.text:
            sticker = quote2sticker(text, get_author(original_message))
        elif video := get_video(original_message):
            if thumb := video.thumb:
                sticker = file2sticker(thumb.file_id, context, photo_arguments=arguments)
            else:
                sticker = file2sticker(video.file_id, context, preprocess_type=FilePreprocessType.video_thumb,
                                       photo_arguments=arguments)
        elif (photo := original_message.photo) and len(photo) > 0:
            sticker = file2sticker(photo[-1].file_id, context, photo_arguments=arguments)
        else:
            raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)

        if sticker is None:
            raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.unexpected)
        if arguments.is_emoji:
            update.message.reply_document(reply_to_message_id=update.effective_message.message_id,
                                          document=sticker, )
        else:
            add_and_delete_sticker(update, context, sticker)
    except ProcessingException as e:
        reply_exception(reply_message=message, exception=e, update=update, context=context)
        return
    except Exception as e:
        print(e)
        reply_exception(reply_message=message, exception=ProcessingException(
            exception_type=ProcessingException.ProcessingExceptionType.unexpected), context=context, update=update)
        return


def get_sticker_id(update: Update, context: CallbackContext):
    if update.message.reply_to_message.sticker is None:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Команда должна быть отправлена в ответ на стикер",
                                 reply_to_message_id=update.effective_message.message_id)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.reply_to_message.sticker.file_id,
                                 reply_to_message_id=update.effective_message.message_id)


def inline_query(update: Update, context):
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Кто ты сегодня?",
            thumb_url="https://i.ibb.co/6HPDsj7/2023-01-27-01-10-28.jpg",
            input_message_content=InputTextMessageContent(
                f"<i>{mallard.get_creature()}</i>", parse_mode=ParseMode.HTML
            ),
        ),
    ]

    update.inline_query.answer(results, cache_time=60 * 60 * 3, is_personal=True)


def main():
    updater = Updater(token=token, use_context=True, workers=6)
    dispatcher = updater.dispatcher

    handler = MessageHandler((Filters.text | Filters.caption) & (~Filters.command), echo, run_async=True)
    command_handler = MessageHandler(Filters.command, command, run_async=True)
    inline_handler = InlineQueryHandler(inline_query)

    dispatcher.add_handler(handler)
    dispatcher.add_handler(command_handler)
    dispatcher.add_handler(inline_handler)

    print('STARTED')
    updater.bot.sendMessage(chat_id=admin_id, text='Я снова здесь!')
    updater.start_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
