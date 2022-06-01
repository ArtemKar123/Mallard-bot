import os
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater, ExtBot
from telegram.ext import MessageHandler, Filters
from mallard import Mallard

mallard = Mallard(random_answer_rate=250)


def echo(update: Update, context: CallbackContext):
    reply = mallard.process(update.message.text)
    if reply is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply,
                                 reply_to_message_id=update.effective_message.message_id)


def main():
    token = os.environ.get('TG_API_KEY')
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    print('STARTED')
    updater.start_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
