import os
import uuid
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from mallard import Mallard
from stickers import file2sticker, FilePreprocessType

mallard = Mallard(random_answer_rate=250)


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
    if update.message.text == '/q':
        quote(update, context)


def quote(update: Update, context: CallbackContext):
    message = update.message
    if (False):  # TODO: check if quotly is in chat
        pass
    else:
        sticker = None
        if (original_message := message.reply_to_message) is not None:
            if (video_note := original_message.video_note) is not None:  # circle video
                if (thumb := video_note.thumb) is not None:
                    if (file_id := thumb.file_id) is not None:
                        sticker = file2sticker(file_id, context, preprocess_type=FilePreprocessType.circle)
            elif (
                    video := original_message.document if original_message.document is not None else original_message.video) is not None:  # circle video
                if (thumb := video.thumb) is not None:
                    if (file_id := thumb.file_id) is not None:
                        sticker = file2sticker(file_id, context)
            elif (photo := original_message.photo) is not None and len(photo) > 0:
                if (file_id := photo[-1].file_id) is not None:
                    sticker = file2sticker(file_id, context)
        if sticker is None:
            return
        uid = str(uuid.uuid4())
        uid = uid.replace("-", "")
        sticker_set_name = f"s{uid}_by_krya_test_bot"

        context.bot.create_new_sticker_set(update.message.from_user.id,
                                           sticker_set_name, "Sticker by @cryakwa_bot",
                                           png_sticker=sticker,
                                           emojis="\U0001F60C")
        sticker_set = context.bot.get_sticker_set(sticker_set_name)
        update.message.reply_sticker(reply_to_message_id=update.effective_message.message_id,
                                     sticker=sticker_set.stickers[-1])


def main():
    token = os.environ.get('TG_API_KEY')
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    handler = MessageHandler((Filters.text | Filters.caption) & (~Filters.command), echo)
    command_handler = MessageHandler(Filters.command, command)
    dispatcher.add_handler(handler)
    dispatcher.add_handler(command_handler)

    print('STARTED')
    updater.start_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
