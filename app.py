import os
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from mallard import Mallard

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


def main():
    token = os.environ.get('TG_API_KEY')
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    handler = MessageHandler((Filters.text | Filters.caption) & (~Filters.command), echo)
    dispatcher.add_handler(handler)

    print('STARTED')
    updater.start_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
