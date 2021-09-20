
# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
from gpiozero import PWMLED
from time import sleep

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
guess = 0
value = 0
#global pwm
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
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        print("Value is " + str(value))
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
    numScores = eeprom.read_byte(0)

    for i in range(1, numScores):
        if i > 3:
            break
        lists = eeprom.read_block(i, 4)
        print(chr(lists[0]), chr(lists[1]), chr(lists[2]), " took ", lists[3], " guesses ", sep="")
    pass


# Setup Pins
def setup():
	print("Setting up...")
    # Setup board mode
	GPIO.setmode(GPIO.BCM)
    # Setup regular GPIO

	for i in range(len(LED_value)):
		GPIO.setup(LED_value[i], GPIO.OUT)
		GPIO.output(LED_value[i], GPIO.LOW)
		
	
	GPIO.setup(LED_accuracy, GPIO.OUT)
	GPIO.output(LED_accuracy, GPIO.LOW)
	#Buttons
	GPIO.setup(btn_increase, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(btn_submit, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        # Buzzer
	GPIO.setup(buzzer, GPIO.OUT)
        # Setup PWM channels
	global pwm,  pwmB
	pwm = GPIO.PWM(LED_accuracy, 1000)
	pwm.start(0)
        # Buzzer PWM 
	pwmB = GPIO.PWM(buzzer, 1)
	pwmB.start(0)
	# Setup debouncing and callbacks
	GPIO.add_event_detect(btn_increase, GPIO.RISING, callback=btn_increase_pressed, bouncetime=300)
	GPIO.add_event_detect(btn_submit, GPIO.RISING, callback=btn_guess_pressed, bouncetime=300)
	

    # Setup PWM channels
	#pwm = GPIO.PWM(LED_accuracy, 100)
	#pwm.start(0)
	print("Setup complete")
	pass
# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_byte(0)
    # Get the scores
    scores = []

    # convert the codes back to ascii
    for i in range(1, score_count):
        scores.append(eeprom.read_block(i, 4))
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)

def increment():
    global guess
    guess = guess+1

# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
# increment guess val
    if GPIO.event_detected(channel):
        increment()
        print("Button Increase pressed")
        print("Guess:" + str(guess))
        update_LEDs()
    pass
# Update Green LEDs based on current guess
def update_LEDs():
    current_guess = [GPIO.LOW, GPIO.LOW, GPIO.LOW]
    if(guess==1):
        current_guess[2] = GPIO.HIGH
    elif(guess==2):
        current_guess[1] = GPIO.HIGH
    elif(guess==3):
        current_guess[1] = GPIO.HIGH
        current_guess[2] = GPIO.HIGH
    elif(guess==4):
        current_guess[0] = GPIO.HIGH
    elif(guess==5):
        current_guess[0] = GPIO.HIGH
        current_guess[2] = GPIO.HIGH
    elif (guess==6):
        current_guess[0] = GPIO.HIGH
        current_guess[1] = GPIO.HIGH
    elif(guess==7):
        current_guess[0] = GPIO.HIGH
        current_guess[1] = GPIO.HIGH
        current_guess[2] = GPIO.HIGH

    # Set LEDs
    print("Updating values according to guess....")
    for i in range(len(LED_value)):
        GPIO.output(LED_value[i], current_guess[i])
# Guess button
def btn_guess_pressed(channel):
    global numGuesses
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    if GPIO.event_detected(channel):
        # Compare the actual value with the user value displayed on the LEDs
        if(guess == value):
             pwmB.ChangeDutyCycle(0)
             GPIO.output(LED_accuracy, GPIO.LOW) # set to low
             
             print("Guess correct!")
             userName = input("Please enter your name \n")


            # Starting block for EEPROM
             start_block = eeprom.read_byte(0)
             block = start_block
             if start_block == 0:
                 # Go to next
                 block += 1
                 eeprom.write_block(block,[ord(userName[0]), ord(userName[2]), ord(userName[2]), numGuesses])
             eeprom.write_byte(0, start_block+1) #next block


             scores = []

             for i in range(1, start_block+1):
                 scores.append(eeprom.read_block(i, 4))
             sortedScores = sorted(scores, key = lambda score: score[3])
             for i in range(len(sortedSscores)):
                 eeprom.write_block(i+1, sortedScores[i])
             GPIO.cleanup()
             menu()
        else:
            trigger_buzzer()
            pwm.ChangeDutyCycle(accuracy_leds())
            GPIO.output(LED_accuracy, GPIO.HIGH)
            numGuesses += 1
            print("Incorrect")
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass

# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    global closeness
    closeness = abs(((value - guess) / (value+1) * 100))

    if closeness > 100:
        closeness = 95
    return 100 - closeness

# Sound Buzzer
def trigger_buzzer():
    diff = value - guess
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%

    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    if(abs(diff)==3):
        pwmB.ChangeFrequency(1)
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    if(abs(diff)==2):
        pwmB.ChangeFrequency(2)
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    if(abs(diff)==1):
        pwmB.ChangeFrequency(4)

    pwmB.ChangeDutyCycle(50)
    time.sleep(0.3)
    GPIO.output(buzzer, GPIO.HIGH)
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        #welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
