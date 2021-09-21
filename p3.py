
# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = False
guess = 0
numGuesses = 0
value = 0


# DEFINE THE PINS USED HERE
LED_value = [17, 27, 22]
LED_accuracy = 12
btn_submit = 23
btn_increase = 24
buzzer = 13
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    global value
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()

    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
        menu()

    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        print("Value is ", value)
        while not end_of_game:
            pass

    elif option == "Q":
        print("Come back soon!")
        exit()

    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    for i in range(0,3):
        print((i+1),"- {} took {} guesses".format(raw_data[i][0]+raw_data[i][1]+raw_data[i][2],str(raw_data[i][3])))
    pass


# Setup Pins
def setup():
    # Setup board mode
    GPIO.setmode(GPIO.BCM)

    # Setup regular GPIO
    # Green LEDs
    for i in range(len(LED_value)):
        GPIO.setup(LED_value[i], GPIO.OUT)
    # Red LED and buzzer
    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)

    # Setup PWM channels
    global pwmLED
    pwmLED = GPIO.PWM(LED_accuracy, 1000)
    global pwm_B
    pwm_B = GPIO.PWM(buzzer, 1000)

    # Setup debouncing and callbacks
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=400)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=400)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    allScores = eeprom.read_byte(0)

    # Get the scores
    scores = []
    for i in range(1, allScores+1):
        scores.append(eeprom.read_block(i,4))

    # convert the codes back to ascii
    for r in range(0,allScores):
        for n in range(0,3):
            scores[r][n] = chr(scores[r][n])

    # return back the results
    return allScores, scores

# Save high scores
def save_scores(userName, numGuesses):
    # fetch score
    allScores, new_scores= fetch_scores()

    # include new score
    new_scores.append([userName[0],userName[1],userName[2],numGuesses])

    # sort according to scores in ascending order
    new_scores.sort(key=lambda x: x[3])

    # update total amount of scores
    allScores += 1

    # write new scores
    new_score_list =[]
    for score in new_scores:
        for char in range(0,3):
            new_score_list.append(ord(score[char]))
        new_score_list.append(score[3])
    eeprom.write_block(1, new_score_list)
    eeprom.write_byte(0, allScores)
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    
    global guess
    global LED_value
    #Initially all LOW for 0
    GPIO.output(LED_value[0], GPIO.LOW)
    GPIO.output(LED_value[1], GPIO.LOW)
    GPIO.output(LED_value[2], GPIO.LOW)

    # Increment guess
    guess += 1
    if guess > 7:   
        guess = 0

    if (guess == 1):
        GPIO.output(LED_value[0], GPIO.HIGH)
    elif (guess == 2):
        GPIO.output(LED_value[1], GPIO.HIGH)
    elif (guess == 3):
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.HIGH)
    elif (guess == 4):
        GPIO.output(LED_value[2], GPIO.HIGH)
    elif (guess == 5):
        GPIO.output(LED_value[2], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.HIGH)
    elif (guess == 6):
        GPIO.output(LED_value[2], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.HIGH)
    elif (guess == 7):
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.HIGH)

pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    global numGuesses
    global guess
    global value

    beg = time.time()
    while GPIO.input(btn_submit) == GPIO.LOW:
        time.sleep(0.05)
    timeHeld = time.time() - beg # how long the button was held for
    # checkif the button is pressed andheld
    if timeHeld > 2:
        
        #GPIO.cleanup() # clear GPIO
        pwmLED.stop() # resetting vals
        pwm_B.stop()

        guess = 0
        numGuesses = 0
        value = 0

        end_of_game = True # game over
        GPIO.cleanup() # clear GPIO
        menu() # loop to menu
        return

    # Compare the actual value with the user value displayed on the LEDs
    numGuesses += 1
    if (guess == value) == False:
    # Change the PWM LED
        accuracy_leds()

    # if it's close enough, adjust the buzzer
        if (abs(guess-value)<3):
            trigger_buzzer()
    # if it's an exact guess:
    elif guess == value:

    # - Disable LEDs and Buzzer
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.LOW)
        pwmLED.stop()
        pwm_B.stop()

    # - tell the user and prompt them for a name
        userName = input("You guessed right. Please enter your name: ") + "   "
        nickname = userName[:3] # crop to be a nick name

    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
        save_scores(nickname, numGuesses)
        guess = 0
        numGuesses = 0
        value = 0
        end_of_game = True
        GPIO.cleanup()
        menu()
    pass


# LED Brightness
def accuracy_leds():

    # Set the brightness of the LED based on how close the guess is to the answer

    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    global guess
    global pwmLED
    global value
    pwmLED.start(50)
    if (guess < value):
        pwmLED.ChangeDutyCycle(int(round((guess/value)*100)))
    else: 
       # if above guess value
        pwmLED.ChangeDutyCycle(int(round(((8-guess)/(8-value))*100)))

pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    if (abs(guess-value)>=3):
        pwm_B.ChangeFrequency(1)
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    elif (abs(guess-value)==2):
        pwm_B.ChangeFrequency(2)
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    elif (abs(guess-value)==1):
        pwm_B.ChangeFrequency(4)
    GPIO.output(buzzer, GPIO.HIGH)
  
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        pwmLED.stop()
        pwm_B.stop()
        GPIO.cleanup()
