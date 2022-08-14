import enum
from telegram.ext import CallbackContext
import cv2
import numpy as np
from io import BytesIO


class FilePreprocessType(enum.Enum):
    none = 0,
    circle = 1
    default = 2


def file2sticker(file_id: str, context: CallbackContext,
                 preprocess_type: FilePreprocessType = FilePreprocessType.default) -> BytesIO:
    file_bytes = context.bot.getFile(file_id).download_as_bytearray()
    inp = np.asarray(bytearray(file_bytes), dtype=np.uint8)
    image = cv2.imdecode(inp, cv2.IMREAD_COLOR)
    if preprocess_type == FilePreprocessType.circle:
        image = cv2.resize(image, (512, 512))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        thresh = np.load('mask.dat', allow_pickle=True)
        image = cv2.bitwise_and(image, image, mask=thresh)
    elif preprocess_type == FilePreprocessType.default:
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
