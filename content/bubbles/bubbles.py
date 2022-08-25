import os

BUBBLE_NAMES = sorted(['content/bubbles/bubble_images/' + name for name in os.listdir('content/bubbles/bubble_images')])
print(BUBBLE_NAMES)

BUBBLES_COUNT = len(BUBBLE_NAMES)
