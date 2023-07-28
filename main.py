import pyautogui
import time
import os
os.makedirs("screenshots", exist_ok=True)

i = 0
while True:
    im = pyautogui.screenshot()
    im.save("screenshots/"+str(i)+".jpg")
    i += 1
    time.sleep(0.5)
