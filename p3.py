 
# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
guessnum=0 # guessed number
scoreArray=[]
Totoalscore=0
scoreCount=0      #number of guesses
value = 0 #Randomly generated number
# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
#eeprom.clear(4096)
cnt=0
pwm1 = None
pwm2 =None

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

    global end_of_game,btn_submit, btn_increase,cnt, value, scoreCount, guessnum
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    scoreCount = 0
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
<<<<<<< HEAD
        print(value)
        print(scoreCount)
=======
>>>>>>> parent of 7c18eb9 (Tracing values error)
        while not end_of_game:
             if GPIO.input(btn_increase) == 0:
                btn_increase_pressed(btn_increase)
             if GPIO.input(btn_submit) == 0:
                btn_guess_pressed(btn_submit)
                #break
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    counter=1
    cunt=0
    for data in raw_data:
        if cunt==1:
            cunt=cunt+1
        else:
            print("{} - {} took {} guesses".format(counter,data[0],data[1]))
            counter+=1
        if counter == 4:
            break

# print out the scores in the required format
    pass


# Setup Pins
def setup():
    global LED_value, LED_accuracy,buzzer, btn_increase,btn_submit,pwm1,pwm2
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    GPIO.setup(LED_value[0], GPIO.OUT)
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.setup(LED_value[2], GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    # Setup PWM channels
    pwm1 = GPIO.PWM(LED_accuracy, 50)
    pwm2 = GPIO.PWM(buzzer, 0.00000001)
    GPIO.output(buzzer, GPIO.LOW)
    # Setup debouncing and callbacks

    GPIO.add_event_detect(btn_increase,GPIO.FALLING, callback=btn_increase_pressed, bouncetime=200)
    GPIO.add_event_detect(btn_submit,GPIO.FALLING, callback=btn_guess_pressed, bouncetime=200)

    pass


# Load high scores
def fetch_scores():

    # get however many scores there are
    score_count = (eeprom.read_byte(0))
    # Get the scores
    # convert the codes back to ascii
    scores = []
    for i in range(1, score_count+1):
        sub=[]
        score = eeprom.read_block(i, 4)
        char1= chr(score[0]);
        #print("Char1 =",char1)
        char2= chr(score[1]);
        #print("Char2 =",char2)
        char3= chr(score[2]);
        #print("Char3 =",char3)
        outString= char1+char2+char3
        sub.append(outString)
        sub.append(score[3])
        scores.append(sub)

    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    global scoreCount, totalScore, scoreArray
    # fetch scores
    totalScore,scoreArray =fetch_scores()                  #first fetch the scores
    # include new score
    print("ScoreArray from fetch scores" ,scoreArray)
    eeprom.write_byte(0, totalScore+1)                     #Increment the total number of scores
    Name= input("Enter name with 3 bits or less: \n")      ##Prompt user fo Name
    inputScore = [Name[:3], scoreCount]
    print("New score", inputScore)
    scoreArray.append(inputScore)
    sortedScoreArray = sorted(scoreArray,key=lambda x: x[1])
    print(sortedScoreArray)
    data_to_write= []
    for Writescore in sortedScoreArray:
        # get the string
        for i in range(3):
            data_to_write.append(ord(Writescore[0][i]))
        data_to_write.append(Writescore[1])
    eeprom.write_block(1, data_to_write)

    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)



# Increase button pressed
def btn_increase_pressed(channel):
    global guessnum
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess,
    # or just pull the value off the LEDs when a user makes a guess
    if guessnum == 8:
        guessnum = 0
    if GPIO.event_detected(channel):
        guessnum = guessnum + 1
        GPIO.output(LED_value[0], guessnum & 0x01) #set bit 0
        GPIO.output(LED_value[1], guessnum & 0x02)
        GPIO.output(LED_value[2], guessnum & 0x04)
    pass


# Guess button
def btn_guess_pressed(channel):
    global guessnum, LED_value, buzzer, value,scoreCount
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    start_time= time.time()
    while GPIO.input(channel) == 0:
        pass
    buttonTime= time.time()- start_time
    if GPIO.event_detected(channel):
        if buttonTime>2:
            GPIO.cleanup()
            menu()
        elif (guessnum!= value) :
            scoreCount+=1
            accuracy_leds() # Change the PWM LED
            if (abs(value)-abs(guessnum)<=3):
                trigger_buzzer()
        else:
            scoreCount+=1
            GPIO.output(LED_value, False)
            GPIO.output(buzzer,GPIO.LOW)
            save_scores()
            menu()
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
    global guessnum, value, pwm1

    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pwm1.start(0)
    if (guessnum< value):        # Set the brightness of the LED based on how close the guess is to the answer
        dc= guessnum/value *100
        pwm1.ChangeDutyCycle(dc);

    else:
        dc= ((8-guessnum)/(8-value))*100
        pwm1.ChangeDutyCycle(dc);

    pass

# Sound Buzzer
def trigger_buzzer():
    global guessnum, value, pwm2
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    pwm2.start(50)
    if abs(guessnum-value)== 1:
        pwm2.ChangeFrequency(4)
    if abs(guessnum-value)== 2:
        pwm2.ChangeFrequency(2)
    if abs(guessnum-value)== 3:
        pwm2.ChangeFrequency(1)
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass


if __name__ == "__main__":
    try:
        # Call setup function


        setup()

        welcome()
        print("from fecth score: ",fetch_scores())
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
