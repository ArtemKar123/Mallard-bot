import os
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import telegram
from mallard import Mallard
from stickers import file2sticker, file2animated_sticker, quote2sticker, FilePreprocessType
from content.emoji_dict import EMOJI_LIST
import random
import re
from stickers import VideoQuoteArguments
from exceptions import ProcessingException

mallard = Mallard(random_answer_rate=250)

token = os.environ.get('TG_API_KEY')
admin_id = os.environ.get('TG_ADMIN_ID')


def echo(update: Update, context: CallbackContext):
    text = update.message.text if update.message.text is not None else update.message.caption
    if text is None:
        return
    reply, reply_is_sticker = mallard.process(text)
    if reply is not None:
        if reply_is_sticker:
            context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=reply,
                                     reply_to_message_id=update.effective_message.message_id)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply,
                                     reply_to_message_id=update.effective_message.message_id)


def command(update: Update, context: CallbackContext):
    # print(update)
    if update.message.text == '/snap':  # you are going to my collection
        quote(update, context)
    elif update.message.text[:4] == '/qwa' or update.message.text[:4] == '/qva':
        video_quote(update, context)
    elif update.message.text == f'/help{context.bot.name}':
        help(update, context)


def help(update: Update, context: CallbackContext):
    reply = 'Кряква умеет превращать кружочки, гифки, видео и картинки в стикеры.\n' \
            'Используйте /qva для анимированных стикеров и /snap для обычных.\n' \
            'кря-кря.'
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply,
                             reply_to_message_id=update.effective_message.message_id)


def edit_exception(wait_message: telegram.message = None, exception: ProcessingException = None):
    if wait_message is not None and exception is not None:
        wait_message.edit_text(text=str(exception))


def reply_exception(reply_message: telegram.message = None, exception: ProcessingException = None,
                    context: CallbackContext = None, update: Update = None):
    if reply_message is not None and exception is not None and context is not None and update is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message,
                                 reply_to_message_id=update.effective_message.message_id)


def parse_arguments(line: str) -> VideoQuoteArguments:
    result = VideoQuoteArguments()
    counts = VideoQuoteArguments(0, 0, 0)
    words = line.split()
    for word in words[1:]:
        if (it := re.search(r's\d+', word)) is not None:
            counts.starting_point += 1
            if counts.starting_point > 1:
                raise ProcessingException(
                    exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                    additional_message="Несколько вхождений аргумента 's*', не знаю, что делать :(")
            result.starting_point = int(it.string[1:])
        elif (it := re.search(r'e\d+', word)) is not None:
            counts.end_point += 1
            if counts.end_point > 1:
                raise ProcessingException(
                    exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                    additional_message="Несколько вхождений аргумента 'e*', не знаю, что делать :(")
            result.end_point = int(it.string[1:])
        elif (it := re.search(r'x\d+\.?\d*', word)) is not None:
            counts.speed = 1 if counts.speed is None else counts.speed + 1
            if counts.speed > 1:
                raise ProcessingException(
                    exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                    additional_message="Несколько вхождений аргумента 'x*', не знаю, что делать :(")
            result.speed = float(it.string[1:])
        else:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message=f'"{word}" не подходит как аргумент для команды.')
        if counts.final_length == 1 and counts.speed == 1:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message=f'Параметры "x*" и "l*" не могут использоваться вместе, используйте что-то одно.')

    return result


def video_quote(update: Update, context: CallbackContext):
    waiting_text = "Ваш запрос очень кважен для нас, оставайтесь на линии!"
    message = update.message
    wait_message = context.bot.send_message(chat_id=update.effective_chat.id, text=waiting_text,
                                            reply_to_message_id=update.effective_message.message_id)

    sticker = None
    try:
        if (original_message := message.reply_to_message) is not None:
            arguments = parse_arguments(message.text)
            if (video_note := original_message.video_note) is not None:  # circle video
                if (file_id := video_note.file_id) is not None:
                    sticker = file2animated_sticker(file_id, context, preprocess_type=FilePreprocessType.circle,
                                                    video_arguments=arguments)
            elif (
                    video := original_message.document if original_message.document is not None
                    else original_message.video) is not None:
                if video.file_size > 10485760:  # 10mb
                    raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.file_too_large)
                sticker = file2animated_sticker(video.file_id, context, preprocess_type=FilePreprocessType.video_thumb,
                                                video_arguments=arguments)
            else:
                raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)
    except ProcessingException as e:
        edit_exception(wait_message=wait_message, exception=e)
        return
    except Exception as e:
        print(e)
        edit_exception(wait_message=wait_message, exception=ProcessingException(
            exception_type=ProcessingException.ProcessingExceptionType.unexpected))
        return

    if sticker is None:
        edit_exception(wait_message=wait_message, exception=ProcessingException(
            exception_type=ProcessingException.ProcessingExceptionType.unexpected))
        return

    sticker_set_name = f"animated_stickerpack_by_{context.bot.name[1:]}"
    # context.bot.create_new_sticker_set(user_id=admin_id, name=sticker_set_name, title='Sticker by @cryakwa_bot',
    #                                    webm_sticker=sticker,
    #                                    emojis="\U0001F60C")
    context.bot.addStickerToSet(user_id=admin_id, name=sticker_set_name,
                                webm_sticker=sticker,
                                emojis=EMOJI_LIST[random.randint(0, len(EMOJI_LIST) - 1)])
    sticker_set = context.bot.get_sticker_set(sticker_set_name)
    update.message.reply_sticker(reply_to_message_id=update.effective_message.message_id,
                                 sticker=sticker_set.stickers[-1])
    for sticker in sticker_set.stickers[1:]:
        context.bot.delete_sticker_from_set(sticker.file_id)

    wait_message.delete()


def quote(update: Update, context: CallbackContext):
    message = update.message
    # print(message)
    sticker = None
    try:
        if (original_message := message.reply_to_message) is not None:
            if (text := original_message.text) is not None:
                author = 'unknown'
                if original_message.forward_from is not None and original_message.forward_from.full_name is not None:
                    author = original_message.forward_from.full_name
                elif original_message.from_user is not None and original_message.from_user.full_name is not None:
                    author = original_message.from_user.full_name
                sticker = quote2sticker(text, author)
            elif (video_note := original_message.video_note) is not None:  # circle video
                if (thumb := video_note.thumb) is not None:
                    if (file_id := thumb.file_id) is not None:
                        sticker = file2sticker(file_id, context, preprocess_type=FilePreprocessType.circle)
            elif (
                    video := original_message.document if original_message.document is not None else original_message.video) is not None:  # circle video
                if (thumb := video.thumb) is not None:
                    if (file_id := thumb.file_id) is not None:
                        sticker = file2sticker(file_id, context)
                else:
                    if video.file_size > 10485760:  # 10mb
                        raise ProcessingException(
                            exception_type=ProcessingException.ProcessingExceptionType.file_too_large)
                    sticker = file2sticker(video.file_id, context, preprocess_type=FilePreprocessType.video_thumb)
            elif (photo := original_message.photo) is not None and len(photo) > 0:
                if (file_id := photo[-1].file_id) is not None:
                    sticker = file2sticker(file_id, context)
            else:
                raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)
    except ProcessingException as e:
        reply_exception(reply_message=message, exception=e, update=update, context=context)
        return
    except Exception as e:
        print(e)
        reply_exception(reply_message=message, exception=ProcessingException(
            exception_type=ProcessingException.ProcessingExceptionType.unexpected), context=context, update=update)
        return
    if sticker is None:
        reply_exception(reply_message=message, exception=ProcessingException(
            exception_type=ProcessingException.ProcessingExceptionType.unexpected), context=context, update=update)
        return

    sticker_set_name = f"image_stickerpack_by_{context.bot.name[1:]}"
    # context.bot.create_new_sticker_set(user_id=admin_id, name=sticker_set_name, title='Sticker by @cryakwa_bot',
    #                                    png_sticker=sticker,
    #                                    emojis="\U0001F60C")
    context.bot.addStickerToSet(user_id=admin_id, name=sticker_set_name,
                                png_sticker=sticker,
                                emojis=EMOJI_LIST[random.randint(0, len(EMOJI_LIST) - 1)])
    sticker_set = context.bot.get_sticker_set(sticker_set_name)
    update.message.reply_sticker(reply_to_message_id=update.effective_message.message_id,
                                 sticker=sticker_set.stickers[-1])
    for sticker in sticker_set.stickers[1:]:
        context.bot.delete_sticker_from_set(sticker.file_id)


def main():
    updater = Updater(token=token, use_context=True, workers=6)
    dispatcher = updater.dispatcher

    handler = MessageHandler((Filters.text | Filters.caption) & (~Filters.command), echo, run_async=True)
    command_handler = MessageHandler(Filters.command, command, run_async=True)
    dispatcher.add_handler(handler)
    dispatcher.add_handler(command_handler)

    print('STARTED')
    updater.start_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
