import numpy as np
import cv2
from mss import mss
import math
import pynput
from pynput.keyboard import Key
import time
from enum import Enum



class State(Enum):
    IDLE = 0
    STOPPED = 1

    #True while the fish health bar is on screen
    #is attempting to kill the fish
    REELING = 2 

    #true between deciding to cast and the bobber having been cast
    #it is waiting for the bobber to appear
    CASTING = 3 

    #true while the bobber is out 
    #it is looking for when the bobber disapears
    BOBBER = 4 

    DEBUG = 5

    RECOVERY = 6


gameResolution = np.array([2560, 1440])
screenResolution = np.array([3840, 2160])
baitNumber = 0
numberOfAttempts = -1





def prompt_selection(message, options, default = None):
    prompt = f"{message}"
    if default is not None:
        prompt += f" [default: {default}]"
    prompt += ": "

    while True:
        print(prompt)
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        
        choice = input("Enter the number of your choice: ").strip()

        if choice == "":
            if default is not None:
                choice = str(default)
            else:
                print("Input is required.\n")
                continue
        
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(options):
                return options[index]
        
        print("Invalid input. Please enter a valid number.\n")
        

def prompt_integer(message, default=None, min_value=None, max_value=None):
    prompt = f"{message}"
    if default is not None:
        prompt += f" [default: {default}]"
    prompt += ": "

    while True:
        user_input = input(prompt).strip()

        if user_input == "":
            if default is not None:
                return default
            else:
                print("Input is required.\n")
                continue

        try:
            value = int(user_input)
            if (min_value is not None and value < min_value) or \
               (max_value is not None and value > max_value):
                print(f"Please enter a number between {min_value} and {max_value}.\n")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid integer.\n")


def setup():
    global screenResolution, gameResolution, baitNumber, numberOfAttempts

    print("This program expect Neir Replicant to be run in Borderless Window mode.")

    selection = prompt_selection("Please select an aspect ratio for both the screen and the game", ["16:9", "16:10", "21:9"], 1)

    aspectRatio = 0
    if selection == "16:9":
        aspectRatio = 16 / 9.0
    elif selection == "16:10":
        aspectRatio = 16 / 10.0
    elif selection == "21:9":
        aspectRatio = 21 / 9.0

    selection = prompt_selection("Please select a screen resolution", ["1080", "1440", "4k"])
    
    if selection == "1080":
        screenResolution = np.array([aspectRatio * 1080, 1080])
    elif selection == "1440":
        screenResolution = np.array([aspectRatio * 1440, 1440])
    elif selection == "4k":
        screenResolution = np.array([aspectRatio * 2160, 2160])


    selection = prompt_selection("Please select a game resolution", ["1080", "1440", "4k"])

    if selection == "1080":
        gameResolution = np.array([aspectRatio * 1080, 1080])
    elif selection == "1440":
        gameResolution = np.array([aspectRatio * 1440, 1440])
    elif selection == "4k":
        gameResolution = np.array([aspectRatio * 2160, 2160])
    
    baitNumber = prompt_integer("Please select how far down in the bait menu you want to go; 0 is the first bait ", 0)

    numberOfAttempts = prompt_integer("Please select the number of attempts to do; -1 means don't stop", -1)

    print("Press i to toggle bot activation.")
    print("Press o to stop program.")
    print("Attempt counter will reset each time the bot is started.")
    print("Approach the water before starting.")
    print()

setup()


attemptCounter = 0
state = State.IDLE
mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()


def on_press(key):
    global state, attemptCounter

    try:
        if key.char == "o":
            state = State.STOPPED

        if key.char == "i":
            if state == State.IDLE:
                attemptCounter = 0
                state = State.CASTING
            else:
                state = State.IDLE

    except AttributeError:
        pass

def on_release(key):
    pass

listener = pynput.keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

bounding_box = {'top': int(math.floor((screenResolution[1] - gameResolution[1]) / 2)), 'left': int(math.floor((screenResolution[0] - gameResolution[0]) / 2)) , 'width': int(gameResolution[0]), 'height': int(gameResolution[1])}


sct = mss()


def capture_screen():
    screenshot = sct.grab(bounding_box)
    img = np.array(screenshot)  # This includes alpha channel (RGBA)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Remove alpha for OpenCV compatibility
    return img


def pressKey(key):
    keyboard.press(key)
    time.sleep(0.05)
    keyboard.release(key)
    time.sleep(0.05)



#CIELAB
bobberLowerBound = np.array([0, 170, 135])
bobberUpperBound = np.array([255, 255, 255])

colorLowerPercentile = np.array([30, 0, 100])
colorUpperPercentile = np.array([88, 255, 183])


def cast(number = 0):
    global state, attemptCounter

    if attemptCounter >= numberOfAttempts and numberOfAttempts >= 0:
        state = State.IDLE
        return
    elif numberOfAttempts >= 0:
        attemptCounter += 1

    if state != State.CASTING:
        raise RuntimeError("Cast when not in CASTING state")
    
    pressKey('f')
    for i in range(number):
        time.sleep(0.1)
        pressKey(Key.down)


    time.sleep(0.1)
    pressKey(Key.enter)

    if state != State.CASTING:
        return

    state = State.BOBBER



def isBobberOnScreen():

    # Convert BGR image to HLS (Hue, Lightness, Saturation)
    lab_image = cv2.cvtColor(capture_screen(), cv2.COLOR_BGR2Lab)

    return np.any(cv2.inRange(lab_image, bobberLowerBound, bobberUpperBound))

def bobber():
    global state
    if state != State.BOBBER:
        raise RuntimeError("Bobber when not in BOBBER state")

    bobberCounter = 0
    while bobberCounter < 10 and state == State.BOBBER:
        bobberCounter += isBobberOnScreen()

    while isBobberOnScreen() and state == State.BOBBER:
        pass
    
    if state != State.BOBBER:
        return

    pressKey(Key.enter)
    state = State.REELING


fishHealthBarLower = np.array([0, 120, 0])
fishHealthBarUpper = np.array([255, 171, 128])

def fishHealthPercent():

    # Convert BGR image to HLS (Hue, Lightness, Saturation)
    image = capture_screen()

    #pixel offsets that change with screen resolution
    temp = np.floor(image.shape[0] * 0.405)
    temp1 = int(30 / 1440.0 * gameResolution[1])
    temp2 = int(20 / 1440.0 * gameResolution[1])
    temp3 = int(10 / 1440.0 * gameResolution[1])
    #if there is a black bar on the screen then the fish is definitely gone
    A = np.mean(image[int(temp - temp1) : int(temp - temp2), :])#Above the Bar
    B = np.mean(image[int(temp + temp2) : int(temp + temp1), :])#Below the Bar
         
    if np.mean(image[int(temp - temp3) : int(temp + temp3), :]) < 10 or A  / B > 2:
        return -1

    #pixel offsets that change with screen resolution
    lV = int(1340 / 1440.0 * gameResolution[1])
    uV = int(-75 / 1440.0 * gameResolution[1])

    lH = int(775 / 2560.0 * gameResolution[0])
    uH = int(-820 / 2560.0 * gameResolution[0])
    pullBar = image[lV : uV, lH : uH]
    lab_image = cv2.cvtColor(pullBar, cv2.COLOR_BGR2Lab)

    pullBar = cv2.inRange(lab_image, fishHealthBarLower, fishHealthBarUpper)

    return np.mean(pullBar)

def reeling():
    global state

    if state != State.REELING:
        raise RuntimeError("Reeling when not in REELING state")
    
    while state == State.REELING:
        temp = fishHealthPercent()
        if temp > 100 or temp < 0:
            break
        pass

    fishHealth = fishHealthPercent()

    lastTime = time.perf_counter()
    keyboard.press("s")
    pullDirection = 0

    while state == State.REELING and fishHealth >= 0:
        newFishHealth = fishHealthPercent()

        #print(fishHealth, newFishHealth)
        if fishHealth < 0:
            break

        if newFishHealth >= fishHealth:
            now = time.perf_counter()
            if now - lastTime > 0.1:
                pullDirection += 1
                pullDirection = pullDirection % 3
                lastTime = now

                if pullDirection == 0:
                    keyboard.release("a")
                    keyboard.release("d")
                elif pullDirection == 1:
                    keyboard.press("a")
                    keyboard.release("d")
                elif pullDirection == 2:
                    keyboard.press("d")
                    keyboard.release("a")

        if newFishHealth < fishHealth:
            fishHealth = newFishHealth

    keyboard.release("s")
    keyboard.release("a")
    keyboard.release("d")

    if state != State.REELING:
        return 
    
    state = State.RECOVERY

def recovery():
    global state

    if state != State.RECOVERY:
        raise RuntimeError("Recovery when not in RECOVERY state")

    time.sleep(0.5)
    pressKey(Key.enter)
    time.sleep(0.5)
    pressKey(Key.enter)

    state = State.CASTING

while state != State.STOPPED:
    if state == State.DEBUG:
        state = State.CASTING

    if state == State.CASTING:
        if numberOfAttempts >= 0:
            if attemptCounter < numberOfAttempts:
                print("Casting " + str(attemptCounter + 1) + " / " + str(numberOfAttempts))
        else:
            print("Casting")
        
        cast(baitNumber)

    if state == State.BOBBER:
        print("Bobber")
        bobber()
    
    if state == State.REELING:
        print("Reeling")
        reeling()

    if state == State.RECOVERY:
        print("Recovery")
        recovery()
        print()