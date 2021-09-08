# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
done = False # set if the user is done guessing
presses = []

# DEFINE THE PINS USED HERE
LED_value = [27, 22, 17]
LED_accuracy = 12
btn_submit = 23
btn_increase = 24
buzzer = None
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
        print("Number: ", value)
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
    pass


# Setup Pins
def setup():
    print("Setting up...")
    # Setup board mode
    GPIO.setmode(GPIO.BCM)
    # Setup regular GPIO
    print(LED_value[0])
    for i in range(len(LED_value)):
    	GPIO.setup(LED_value[i], GPIO.OUT) #out for now to test connections and pin numbering
    	#GPIO.output(LED_value[i], GPIO.HIGH)

    GPIO.setup(LED_accuracy, GPIO.OUT)
    
    GPIO.setup(btn_increase, GPIO.IN)
    GPIO.add_event_detect(btn_increase, GPIO.RISING, callback=buttonEventHandler_rising)
    #GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=buttonEventHandler_falling)	
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


    # Setup PWM channels
    # Setup debouncing and callbacks
    print("Exiting setup...")
    pass

def button_callback(channel):
	print("Button pushed")

# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    # Get the scores

    # convert the codes back to ascii

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

def buttonEventHandler_rising(channel):
	GPIO.output(LED_value[0], GPIO.HIGH)
	raise Exception("Button pressed")
def buttonEventHandler_falling(channel):
	GPIO.output(LED_value)
# Increase button pressed
#GPIO.add_event_detect(btn_increase, GPIO.RISING, callback=buttonEventHandler_rising)
#GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=buttonEventHandler_falling)
def btn_increase_pressed(channel):
	#GPIO.add_event_detect(channel, GPIO.RISING, callback=buttonEventHandler_rising)
	#GPIO.add_event_detect(channel, GPIO.FALLING, callback=buttonEventHandler_falling)
	
	while True:
		if GPIO.event_detected(channel):
			print("Button pressed")
			sleep(1)
			#print("Button pressed")
	#	input = GPIO.input(channel)
	#	print("Input: ")
	#	if not input:
	#		startTime = time.time()
	#		GPIO.output(LED_value[0], GPIO.HIGH)
		#	while not input:
		#		input = GPIO.input(channel)
	#	else:
	#		end_time = time.time()
	#		GPIO.output(LED_value[0], GPIO.LOW)
		#GPIO.add_event_detect(channel, GPIO.RISING, callback=button_callback)
	
#print("Entering button increase")
    # Check if button has been pressed
	#if (GPIO.input(channel)):
	#	print("Button pressed")

	#try:
	#	GPIO.wait_for_edge(channel, GPIO.FALLING)
	#	print("Button pressed")
    #print("Printing guess value", guess)
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess,
    # or just pull the value off the LEDs when a user makes a guess
  #  pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
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
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
    #print("Switching on green LEDs")
#    print(len(LED_value))
        #GPIO.add_event_detect(btn_increase, GPIO.RISING, callback=button_callback)
        #welcome()
        btn_increase_pressed(btn_increase)
        while True:
          #  menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
