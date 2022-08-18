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
import enum

mallard = Mallard(random_answer_rate=250)

token = os.environ.get('TG_API_KEY')
admin_id = os.environ.get('TG_ADMIN_ID')


class ProcessingErrorType(enum.Enum):
    none = 0
    file_too_large = 1
    unexpected = 2
    wrong_source_type = 3


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
    elif update.message.text == '/qwa' or update.message.text == '/qva':
        video_quote(update, context)
    elif update.message.text == f'/help{context.bot.name}':
        help(update, context)


def help(update: Update, context: CallbackContext):
    reply = 'Кряква умеет превращать кружочки, гифки, видео и картинки в стикеры.\n' \
            'Используйте /qva для анимированных стикеров и /snap для обычных.\n' \
            'кря-кря.'
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply,
                             reply_to_message_id=update.effective_message.message_id)


def on_quote_return(original_message: telegram.message = None, wait_message: telegram.message = None,
                    success: bool = True,
                    error: ProcessingErrorType = ProcessingErrorType.unexpected):
    if success:
        if wait_message is not None:
            wait_message.delete()
    else:
        reply_text = 'Не ква!\n'
        if error == ProcessingErrorType.file_too_large:
            reply_text += 'Файл слишком большой :('
        elif error == ProcessingErrorType.wrong_source_type:
            reply_text += 'Я такое квотить не умею :('
        if wait_message is not None:
            wait_message.edit_text(text=reply_text)
        elif original_message is not None:
            original_message.reply_text(text=reply_text)


def video_quote(update: Update, context: CallbackContext):
    waiting_text = "Ваш запрос очень кважен для нас, оставайтесь на линии!"
    message = update.message
    wait_message = message.reply_text(text=waiting_text)

    sticker = None
    try:
        if (original_message := message.reply_to_message) is not None:
            if (video_note := original_message.video_note) is not None:  # circle video
                if (file_id := video_note.file_id) is not None:
                    sticker = file2animated_sticker(file_id, context, preprocess_type=FilePreprocessType.circle)
            elif (
                    video := original_message.document if original_message.document is not None
                    else original_message.video) is not None:
                if video.file_size > 10485760:  # 10mb
                    on_quote_return(wait_message=wait_message, success=False, error=ProcessingErrorType.file_too_large)
                    return
                sticker = file2animated_sticker(video.file_id, context, preprocess_type=FilePreprocessType.video_thumb)
            else:
                on_quote_return(wait_message=wait_message, success=False, error=ProcessingErrorType.wrong_source_type)
                return
    except Exception as e:
        print(e)
        on_quote_return(wait_message=wait_message, success=False)
        return

    if sticker is None:
        on_quote_return(wait_message=wait_message, success=False)
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

    on_quote_return(wait_message=wait_message, success=True)


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
                        on_quote_return(original_message=message, success=False,
                                        error=ProcessingErrorType.file_too_large)
                        return
                    sticker = file2sticker(video.file_id, context, preprocess_type=FilePreprocessType.video_thumb)
            elif (photo := original_message.photo) is not None and len(photo) > 0:
                if (file_id := photo[-1].file_id) is not None:
                    sticker = file2sticker(file_id, context)
            else:
                on_quote_return(original_message=message, success=False, error=ProcessingErrorType.wrong_source_type)
                return
    except Exception as e:
        print(e)
        on_quote_return(original_message=message, success=False)
        return
    if sticker is None:
        on_quote_return(original_message=message, success=False)
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
