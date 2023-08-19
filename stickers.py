import enum
import subprocess
from telegram.ext import CallbackContext
import cv2
import numpy as np
from io import BytesIO
import tempfile
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from dataclasses import dataclass
from exceptions import ProcessingException
from content.bubbles.bubbles import BUBBLE_NAMES, BUBBLES_COUNT


class FilePreprocessType(enum.Enum):
    none = 0
    circle = 1
    video_thumb = 2
    animation = 3
    default = 4


def validate_speech_bubble(value):
    if value < 1:
        raise ProcessingException(
            exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
            additional_message="Номер не может быть меньше 1.")
    if value > BUBBLES_COUNT:
        raise ProcessingException(
            exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
            additional_message=f"Количество пузырьков в коллекции: {BUBBLES_COUNT}.")


@dataclass
class VideoQuoteArguments:
    """
    1. Crop video from starting_point to end_point
    2. Change video speed to `speed`
    """
    starting_point: int = None  # s
    end_point: int = None  # e
    speed: float = None  # x
    final_length: float = None  # l
    reverse: bool = None  # r
    speech_bubble: int = None  # b
    is_emoji: bool = None  # j

    def field_name_to_flag(self, field_name):
        mp = {name: flag for (name, flag) in zip(self.__annotations__.keys(), ('s', 'e', 'x', 'l', 'r', 'b', 'j'))}
        return mp[field_name]

    def set_field(self, field, value):
        if getattr(self, field) is not None:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message=f"Несколько вхождений аргумента '{self.field_name_to_flag(field)}*', не знаю, что делать :(")
        if field == 'speech_bubble':
            validate_speech_bubble(value)
        setattr(self, field, value)

    def validate(self):
        if self.end_point is not None and self.starting_point is None:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message=f'Параметр "e*" должен использоваться только вместе с "s*".')


@dataclass
class PhotoQuoteArguments:
    speech_bubble: int = None  # b
    is_emoji: bool = None  # j

    def field_name_to_flag(self, field_name):
        mp = {name: flag for (name, flag) in zip(self.__annotations__.keys(), ('b', 'j'))}
        return mp[field_name]

    def set_field(self, field, value):
        if getattr(self, field) is not None:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message=f"Несколько вхождений аргумента '{self.field_name_to_flag(field)}*', не знаю, что делать :(")
        if field == 'speech_bubble':
            validate_speech_bubble(value)
        setattr(self, field, value)


def video2emoji(file_id: str, context: CallbackContext):
    print('video2emoji')
    file_bytes = context.bot.getFile(file_id).download_as_bytearray()
    emoji = None

    with tempfile.NamedTemporaryFile(suffix='.mp4') as temp:
        temp.write(file_bytes)

        cap = cv2.VideoCapture(temp.name)

        # count the number of frames
        fps = cap.get(cv2.CAP_PROP_FPS)
        final_length = 2.9
        new_w = new_h = 100
        with tempfile.NamedTemporaryFile(suffix='.webm') as out_temp:
            query = f'ffmpeg -nostats \
                                -loglevel error \
                                -y \
                                -i {temp.name} \
                                -loop 1 \
                                -c:v libvpx-vp9 \
                                -preset ultrafast \
                                -r {fps} \
                                -s {new_w}x{new_h} \
                                -t {final_length} \
                                -an \
                                {out_temp.name}'
            print(query)
            subprocess.call(query, shell=True, timeout=75)

            emoji = BytesIO(out_temp.read())
            emoji.seek(0)
    return emoji

def image2emoji(file_id: str, context: CallbackContext):
    file_bytes = context.bot.getFile(file_id).download_as_bytearray()
    image = None

    inp = np.asarray(bytearray(file_bytes), dtype=np.uint8)
    image = cv2.imdecode(inp, cv2.IMREAD_UNCHANGED)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)

    image = cv2.resize(image, (100, 100))

    is_success, buffer = cv2.imencode(".png", image)
    emoji = BytesIO(buffer)
    emoji.seek(0)
    return emoji


# FIXME: auto-alt-ref makes ffmpeg read video without alpha channel which should be fixed
def file2animated_sticker(file_id: str, context: CallbackContext,
                          preprocess_type: FilePreprocessType = FilePreprocessType.default,
                          video_arguments: VideoQuoteArguments = VideoQuoteArguments()) -> BytesIO:
    if file_id is None:
        raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)
    file_bytes = context.bot.getFile(file_id).download_as_bytearray()
    sticker = None
    original_arguments = video_arguments
    with tempfile.NamedTemporaryFile(suffix='.mp4') as temp:
        temp.write(file_bytes)
        t = time.time()
        cap = cv2.VideoCapture(temp.name)

        # count the number of frames
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # calculate duration of the video
        video_length_seconds = round(frames / fps)

        if video_arguments.speed is None:
            video_arguments.speed = 1

        if original_arguments.end_point is not None and original_arguments.end_point <= original_arguments.starting_point:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message='Секунда завершения должна быть строго больше секунды начала.')

        if video_arguments.reverse is None:
            video_arguments.reverse = False

        if video_arguments.starting_point is None:
            video_arguments.starting_point = 0
        elif video_arguments.starting_point > video_length_seconds:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message='Секунда начала должна быть меньше чем длина видео.')
        else:

            if video_arguments.reverse:
                video_arguments.starting_point = video_length_seconds - video_arguments.starting_point

            video_arguments.starting_point = round(
                video_arguments.starting_point * float(1 / video_arguments.speed))

        if video_arguments.final_length is None:
            video_arguments.final_length = 2.9

        if video_arguments.end_point is not None:
            if video_arguments.reverse:
                video_arguments.end_point = video_length_seconds - video_arguments.end_point
            video_arguments.end_point = round(video_arguments.end_point * float(1 / video_arguments.speed))
            if video_arguments.reverse:
                video_arguments.starting_point, video_arguments.end_point = video_arguments.end_point, video_arguments.starting_point

            video_arguments.final_length = abs(video_arguments.end_point - video_arguments.starting_point)

        print(video_arguments.final_length)
        video_arguments.final_length = max(0.1, min(video_arguments.final_length, 2.9))
        if video_arguments.speed < 1:
            fps = int(fps * video_arguments.speed)
        w = int(cap.get(3))
        h = int(cap.get(4))
        desired_size = 100 if video_arguments.is_emoji else 512
        if w >= h:
            new_h = int(h * (desired_size / w))
            new_w = desired_size
        else:
            new_w = int(w * (desired_size / h))
            new_h = desired_size
        cap.release()
        print(new_w, new_h)
        with tempfile.NamedTemporaryFile(suffix='.webm') as out_temp:
            starting_second = str(video_arguments.starting_point)
            if len(starting_second) == 1:
                starting_second = '0' + starting_second
            if preprocess_type == FilePreprocessType.circle:
                with tempfile.NamedTemporaryFile(suffix='.png') as mask_temp, tempfile.NamedTemporaryFile(
                        suffix='.png') as speech_bubble_temp:
                    if video_arguments.speech_bubble is not None:
                        bubble = cv2.imread(BUBBLE_NAMES[video_arguments.speech_bubble], cv2.IMREAD_UNCHANGED)
                        bubble = cv2.resize(bubble, (w, h))
                        cv2.imwrite(speech_bubble_temp.name, bubble)
                    side_size = 100 if video_arguments.is_emoji else 512
                    mask = np.full((side_size, side_size, 4), (0, 0, 0, 0)).astype(np.uint8)
                    mask = cv2.circle(mask, (side_size // 2, side_size // 2), int(side_size * 0.976) // 2,
                                      (255, 255, 255, 255), thickness=-1)
                    frame_circle = np.load('frame.dat', allow_pickle=True)
                    frame_circle = cv2.resize(frame_circle, (desired_size, desired_size))
                    blurred = cv2.GaussianBlur(mask, (7, 7), 0)
                    mask[frame_circle == 255] = blurred[frame_circle == 255]
                    mask = cv2.resize(mask, (w, h))
                    cv2.imwrite(mask_temp.name, mask)
                    filter_complex = f'-filter_complex "[1:v]alphaextract[alf];' \
                                     f'[0:v][alf]alphamerge[res];' \
                                     f'{"[res][2:v]overlay[res];" if video_arguments.speech_bubble is not None else ""}' \
                                     f'{"[res]reverse[res];" if video_arguments.reverse else ""}' \
                                     f'[res]setpts={float(1 / video_arguments.speed):.2f}*PTS"'
                    query = f'ffmpeg -nostats \
                            -loglevel error \
                            -y \
                            -i {temp.name} \
                            -loop 1 \
                            -i {mask_temp.name} \
                            {"-i " + speech_bubble_temp.name if video_arguments.speech_bubble is not None else ""} \
                            {filter_complex} \
                            -c:v libvpx-vp9 -auto-alt-ref 0 \
                            -preset ultrafast \
                            -ss 00:00:{starting_second} '
                    if video_arguments.end_point is not None:
                        ending_point = str(video_arguments.end_point)
                        if len(ending_point) == 1:
                            ending_point = '0' + ending_point
                        query += f'-to 00:00:{ending_point} '
                    query += f'-r {fps} \
                            -s {new_w}x{new_h} \
                            -t {video_arguments.final_length} \
                            -an \
                            {out_temp.name}'
                    print(query)
                    subprocess.call(query, shell=True, timeout=75)
            else:
                with tempfile.NamedTemporaryFile(suffix='.png') as speech_bubble_temp:
                    if video_arguments.speech_bubble is not None:
                        bubble = cv2.imread(BUBBLE_NAMES[video_arguments.speech_bubble], cv2.IMREAD_UNCHANGED)
                        bubble = cv2.resize(bubble, (w, h))
                        cv2.imwrite(speech_bubble_temp.name, bubble)

                    print('Starting from', starting_second)
                    filter_complex = f'-filter_complex "[0:v]setpts={float(1 / video_arguments.speed):.2f}*PTS[res];' \
                                     f'{"[res][1:v]overlay[res];" if video_arguments.speech_bubble is not None else ""}' \
                                     f'{"[res]reverse[res];" if video_arguments.reverse else ""}' \
                                     '"'
                    if filter_complex[-7:] == '[res];"':
                        filter_complex = filter_complex[:-7] + '"'
                    query = f'ffmpeg -nostats \
                                                -loglevel error \
                                                -y \
                                                -i {temp.name} \
                                                -loop 1 \
                                                {"-i " + speech_bubble_temp.name if video_arguments.speech_bubble is not None else ""} \
                                                {filter_complex} \
                                                -c:v libvpx-vp9 -auto-alt-ref 0 \
                                                -preset ultrafast \
                                                -ss 00:00:{starting_second} '
                    if video_arguments.end_point is not None:
                        ending_point = str(video_arguments.end_point)
                        if len(ending_point) == 1:
                            ending_point = '0' + ending_point
                        query += f'-to 00:00:{ending_point} '
                    query += f'-r {fps} \
                                                -s {new_w}x{new_h} \
                                                -t {video_arguments.final_length} \
                                                -an \
                                                {out_temp.name}'
                    print(query)
                    subprocess.call(query, shell=True, timeout=75)
            sticker = BytesIO(out_temp.read())
            sticker.seek(0)
    return sticker


def file2sticker(file_id: str, context: CallbackContext,
                 preprocess_type: FilePreprocessType = FilePreprocessType.default,
                 photo_arguments: PhotoQuoteArguments = PhotoQuoteArguments()) -> BytesIO:
    if file_id is None:
        raise ProcessingException(exception_type=ProcessingException.ProcessingExceptionType.wrong_source_type)
    # print(photo_arguments.speech_bubble)
    file_bytes = context.bot.getFile(file_id).download_as_bytearray()
    if preprocess_type == FilePreprocessType.video_thumb:
        # file_bytes = context.bot.getFile(file_id).download_as_bytearray()
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(file_bytes)

            cap = cv2.VideoCapture(temp.name)
            ret, image = cap.read()
            cap.release()
    else:
        inp = np.asarray(bytearray(file_bytes), dtype=np.uint8)
        image = cv2.imdecode(inp, cv2.IMREAD_UNCHANGED)

    desired_size = 100 if photo_arguments.is_emoji else 512
    if image is None:
        return BytesIO()
    if preprocess_type == FilePreprocessType.circle:
        image = cv2.resize(image, (desired_size, desired_size))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        thresh = np.load('mask.dat', allow_pickle=True)
        thresh = cv2.resize(thresh, (desired_size, desired_size))
        image = cv2.bitwise_and(image, image, mask=thresh)
    elif preprocess_type in [FilePreprocessType.default, FilePreprocessType.video_thumb]:
        h, w = image.shape[:2]
        if w >= h:
            new_h = int(h * (desired_size / w))
            new_w = desired_size
        else:
            new_w = int(w * (desired_size / h))
            new_h = desired_size
        image = cv2.resize(image, (new_w, new_h))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)

    if photo_arguments.speech_bubble is not None:
        bubble = cv2.imread(BUBBLE_NAMES[photo_arguments.speech_bubble], cv2.IMREAD_UNCHANGED)
        bubble = cv2.resize(bubble, image.shape[:2][::-1])
        image = cv2.addWeighted(image, 1, bubble, 1, 0)

    is_success, buffer = cv2.imencode(".png", image)
    sticker = BytesIO(buffer)
    sticker.seek(0)
    return sticker


# FIXME: simple yet buggy, would be nice to make it any smarter.
def quote2sticker(quote, author, fg='black', font_file=None, font_size=None, width=512,
                  height=384):
    colors = [(248, 205, 48), (75, 151, 75), (150, 112, 159), (211, 111, 76)]
    quote_text = quote[:181]
    quote = quote_text
    sentence = f"{quote} - {author}"

    quote = ImageFont.truetype(font_file if font_file else "content/fonts/jmh-typewriter.bold.otf",
                               font_size if font_size else 28)

    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    background = Image.new("RGB", (width, height), color=(colors[random.randint(0, len(colors) - 1)]))

    img_w, img_h = background.size
    bg_w, bg_h = img.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    bback = background.filter(ImageFilter.BLUR)
    img.paste(bback, offset)

    d = ImageDraw.Draw(img)

    sum = 0
    for letter in sentence:
        sum += d.textsize(letter, font=quote)[0]
    average_length_of_letter = sum / len(sentence)

    number_of_letters_for_each_line = (width / 1.618) / average_length_of_letter
    incrementer = 0
    fresh_sentence = ""

    for letter in quote_text:
        if incrementer < number_of_letters_for_each_line:
            fresh_sentence += letter
        else:
            if letter == " ":
                fresh_sentence += "\n"
                incrementer = 0
            else:
                fresh_sentence += letter
        incrementer += 1
    fresh_sentence += "\n\n— "
    for letter in author:
        if incrementer < number_of_letters_for_each_line:
            fresh_sentence += letter
        else:
            if letter == " ":
                fresh_sentence += "\n"
                incrementer = 0
            else:
                fresh_sentence += letter
        incrementer += 1

    dim = d.textsize(fresh_sentence, font=quote)
    x2 = dim[0]
    y2 = dim[1]

    qx = width / 2 - x2 / 2
    qy = height / 2 - y2 / 2

    d.text((qx, qy), fresh_sentence, align="center", font=quote, fill=fg)
    sticker = BytesIO()
    img.save(sticker, 'PNG')
    sticker.seek(0)
    return sticker
