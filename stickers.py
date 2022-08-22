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


class FilePreprocessType(enum.Enum):
    none = 0
    circle = 1
    video_thumb = 2
    animation = 3
    default = 4


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


def file2animated_sticker(file_id: str, context: CallbackContext,
                          preprocess_type: FilePreprocessType = FilePreprocessType.default,
                          video_arguments: VideoQuoteArguments = VideoQuoteArguments()) -> BytesIO:
    file_bytes = context.bot.getFile(file_id).download_as_bytearray()
    sticker = None
    with tempfile.NamedTemporaryFile(suffix='.mp4') as temp:
        temp.write(file_bytes)
        t = time.time()
        cap = cv2.VideoCapture(temp.name)

        # count the number of frames
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # calculate duration of the video
        video_length_seconds = round(frames / fps)

        if video_arguments.starting_point is None:
            video_arguments.starting_point = 0
        elif video_arguments.starting_point > video_length_seconds:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message='Секунда начала должна быть меньше чем длина видео.')
        if video_arguments.speed is None:
            video_arguments.speed = 1
        if video_arguments.final_length is None:
            video_arguments.final_length = 2.9

        if video_arguments.end_point is not None and video_arguments.end_point <= video_arguments.starting_point:
            raise ProcessingException(
                exception_type=ProcessingException.ProcessingExceptionType.arguments_parsing_error,
                additional_message='Секунда завершения должна быть строго больше секунды начала.')

        video_arguments.starting_point = round(
            video_arguments.starting_point * float(1 / video_arguments.speed))

        if video_arguments.end_point is not None:
            video_arguments.end_point = max(video_arguments.starting_point + float(1 / video_arguments.speed),
                                            round(video_arguments.end_point * float(1 / video_arguments.speed)))
            video_arguments.final_length = (video_arguments.end_point - video_arguments.starting_point)
        print(video_arguments.final_length)
        video_arguments.final_length = max(0.1, min(video_arguments.final_length, 2.9))
        if video_arguments.speed < 1:
            fps = int(fps * video_arguments.speed)
        w = int(cap.get(3))
        h = int(cap.get(4))
        if w >= h:
            new_h = int(h * (512 / w))
            new_w = 512
        else:
            new_w = int(w * (512 / h))
            new_h = 512
        cap.release()
        print(new_w, new_h)
        with tempfile.NamedTemporaryFile(suffix='.webm') as out_temp:
            starting_second = str(video_arguments.starting_point)
            if len(starting_second) == 1:
                starting_second = '0' + starting_second
            if preprocess_type == FilePreprocessType.circle:
                with tempfile.NamedTemporaryFile(suffix='.png') as mask_temp:
                    mask = np.full((512, 512, 4), (0, 0, 0, 0)).astype(np.uint8)
                    mask = cv2.circle(mask, (255, 255), 250, (255, 255, 255, 255), thickness=-1)
                    frame_circle = np.load('frame.dat', allow_pickle=True)
                    blurred = cv2.GaussianBlur(mask, (7, 7), 0)
                    mask[frame_circle == 255] = blurred[frame_circle == 255]
                    mask = cv2.resize(mask, (w, h))
                    cv2.imwrite(mask_temp.name, mask)

                    query = f'ffmpeg -nostats \
                            -loglevel error \
                            -y \
                            -i {temp.name} \
                            -loop 1 \
                            -i {mask_temp.name} -filter_complex "[1:v]alphaextract[alf];[0:v][alf]alphamerge[res];[res]setpts={float(1 / video_arguments.speed):.2f}*PTS"\
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
                    subprocess.call(query
                                    ,
                                    shell=True)
            else:
                print('Starting from', starting_second)
                query = f'ffmpeg -nostats \
                    -loglevel error \
                    -y \
                    -i {temp.name} \
                    -c:v libvpx-vp9 \
                    -pix_fmt yuva420p \
                    -preset ultrafast \
                    -ss 00:00:{starting_second} '
                if video_arguments.end_point is not None:
                    ending_point = str(video_arguments.end_point)
                    if len(ending_point) == 1:
                        ending_point = '0' + ending_point
                    query += f'-to 00:00:{ending_point} '
                query += f'-r {fps} \
                    -filter:v "setpts={float(1 / video_arguments.speed):.2f}*PTS" \
                    -s {new_w}x{new_h} \
                    -t {video_arguments.final_length} {out_temp.name}'
                print(query)
                subprocess.call(
                    query,
                    shell=True)
            sticker = BytesIO(out_temp.read())
            sticker.seek(0)
    return sticker


def file2sticker(file_id: str, context: CallbackContext,
                 preprocess_type: FilePreprocessType = FilePreprocessType.default) -> BytesIO:
    file_bytes = context.bot.getFile(file_id).download_as_bytearray()
    image = None
    if preprocess_type == FilePreprocessType.video_thumb:
        file_bytes = context.bot.getFile(file_id).download_as_bytearray()
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(file_bytes)

            cap = cv2.VideoCapture(temp.name)
            ret, image = cap.read()
            cap.release()
    else:
        inp = np.asarray(bytearray(file_bytes), dtype=np.uint8)
        image = cv2.imdecode(inp, cv2.IMREAD_COLOR)

    if image is None:
        return BytesIO()
    if preprocess_type == FilePreprocessType.circle:
        image = cv2.resize(image, (512, 512))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        thresh = np.load('mask.dat', allow_pickle=True)
        image = cv2.bitwise_and(image, image, mask=thresh)
    elif preprocess_type in [FilePreprocessType.default, FilePreprocessType.video_thumb]:
        h, w = image.shape[:2]
        if w >= h:
            new_h = int(h * (512 / w))
            new_w = 512
        else:
            new_w = int(w * (512 / h))
            new_h = 512
        image = cv2.resize(image, (new_w, new_h))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)

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

    quote = ImageFont.truetype(font_file if font_file else "fonts/JMH Typewriter-Bold.otf",
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
