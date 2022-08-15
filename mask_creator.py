import numpy as np
import cv2
import time

mask = np.full((512, 512, 3), (0, 0, 0)).astype(np.uint8)
mask = cv2.circle(mask, (255, 255), 250, (255, 255, 255), thickness=-1)
mask = mask[:, :, 1]
mask.dump('mask.dat')

frame = np.full((512, 512, 3), (0, 0, 0)).astype(np.uint8)
frame = cv2.circle(frame, (255, 255), 250, (255, 255, 255), thickness=3)
cv2.imwrite('frame.png', frame)
frame = frame[:, :, 1]
frame.dump('frame.dat')

t = time.time()
mask = np.full((512, 512, 4), (0, 0, 0, 0)).astype(np.uint8)
mask = cv2.circle(mask, (255, 255), 250, (255, 255, 255, 255), thickness=-1)
frame_circle = np.load('frame.dat', allow_pickle=True)
blurred = cv2.GaussianBlur(mask, (7, 7), 0)
mask[frame_circle == 255] = blurred[frame_circle == 255]

mask = cv2.resize(mask, (384, 384))
cv2.imwrite('mask.png', mask)
print(time.time() - t)