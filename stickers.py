import enum
from telegram.ext import CallbackContext
import cv2
import numpy as np
from io import BytesIO
import tempfile


class FilePreprocessType(enum.Enum):
    none = 0
    circle = 1
    video_thumb = 2
    animation = 3
    default = 4


def file2animated_sticker(file_id: str, context: CallbackContext):
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

        cap.set(3, new_w)
        cap.set(4, new_h)

        fourcc = cv2.VideoWriter_fourcc(*'WEBM')
        with tempfile.NamedTemporaryFile() as out_temp:
            out = cv2.VideoWriter(out_temp, fourcc, 14.0, (new_w, new_h))
            while True:
                ret, frame = cap.read()
                if frame.empty():
                    break
                out.write(frame)
            out.release()
            cap.release()


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
