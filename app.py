import os
import uuid
from io import BytesIO

import cv2
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from mallard import Mallard
from stickers import file2sticker, FilePreprocessType
import tempfile

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
    if update.message.text == '/qwa':
        quote(update, context)
    if update.message.text == '/krya':
        video_quote(update, context)


def video_quote(update: Update, context: CallbackContext):
    message = update.message

    file_id = None
    if (original_message := message.reply_to_message) is not None:
        if (
                video := original_message.document if original_message.document is not None else original_message.video) is not None:  # circle video
            if video.file_size > 10485760:  # 10mb
                return
            file_id = video.file_id

    file_bytes = context.bot.getFile(file_id).download_as_bytearray()
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(file_bytes)

        cap = cv2.VideoCapture(temp.name)
        w = int(cap.get(3))  # float `width`
        h = int(cap.get(4))
        if w >= h:
            new_h = int(h * (512 / w))
            new_w = 512
        else:
            new_w = int(w * (512 / h))
            new_h = 512

        print(new_w, new_h)

        with tempfile.NamedTemporaryFile() as out_temp:

            fourcc = cv2.VideoWriter_fourcc(*'vp90')
            out = cv2.VideoWriter(out_temp.name, fourcc, 10.0, (new_w, new_h))
            frame_count = 0
            while frame_count < 20:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                frame = cv2.resize(frame, (new_w, new_h))
                out.write(frame)

            out.release()
            cap.release()
            uid = str(uuid.uuid4())
            uid = uid.replace("-", "")
            sticker_set_name = f"s{uid}_by_cryakwa_bot"
            # print(message.from_user.id)
            context.bot.create_new_sticker_set(user_id=admin_id, name=sticker_set_name, title="Sticker by @cryakwa_bot",
                                               webm_sticker=open(out_temp.name, 'rb'),
                                               emojis="\U0001F60C")
            sticker_set = context.bot.get_sticker_set(sticker_set_name)
            update.message.reply_sticker(reply_to_message_id=update.effective_message.message_id,
                                         sticker=sticker_set.stickers[-1])

    pass


def quote(update: Update, context: CallbackContext):
    message = update.message
    print(message)
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
            else:
                if video.file_size > 10485760:  # 10mb
                    return
                sticker = file2sticker(video.file_id, context, preprocess_type=FilePreprocessType.video_thumb)

        elif (photo := original_message.photo) is not None and len(photo) > 0:
            if (file_id := photo[-1].file_id) is not None:
                sticker = file2sticker(file_id, context)
    if sticker is None:
        return
    uid = str(uuid.uuid4())
    uid = uid.replace("-", "")
    sticker_set_name = f"s{uid}_by_krya_test_bot"
    # print(message.from_user.id)
    context.bot.create_new_sticker_set(user_id=admin_id, name=sticker_set_name, title="Sticker by @cryakwa_bot",
                                       png_sticker=sticker,
                                       emojis="\U0001F60C")
    sticker_set = context.bot.get_sticker_set(sticker_set_name)
    update.message.reply_sticker(reply_to_message_id=update.effective_message.message_id,
                                 sticker=sticker_set.stickers[-1])


def main():
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
