'''
Created on July, 27, 2018

@author: Lian Tongda

'''

#FPRun.py

# import the GPIO and time package
import os
import time
import sys
import Fingerprint
import FPSconstants
import RPi.GPIO as GPIO
#Drive of BME280, the sensor of temperature, pressure and humidity
from Adafruit_BME280 import *

#Pin7 is unoccupied, Idon't know why they define this....
inputPinExit = 7
#BlueLED
outputPin = 40
#RedLED
redpin = 38

#GreenLED
ledPin = 36
#PIR sensor
butPin = 12

#Pin Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#BlueLED
GPIO.setup(outputPin, GPIO.OUT, initial=GPIO.LOW)
#RedLED
GPIO.setup(redpin, GPIO.OUT, initial = GPIO.HIGH)
#I don't know
GPIO.setup(inputPinExit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#Green LED, show if person detected by PIR SENSOR
GPIO.setup(ledPin, GPIO.OUT)
#PIR SENSOR
GPIO.setup(butPin, GPIO.IN)


def PIRdetect():
    try:
        while True:
            if (GPIO.input(butPin)== False):
			# Nobody is detected
                GPIO.output(ledPin, False)
                print("Vaccant")
            else:
			# Somebody is detected
                GPIO.output(ledPin, True)
                print("Who's there???")
            #Check the state every 0.1 second
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Program terminated!")


#Temperature Pressure and Humidity
def TempPreHum():
    #Codes provided by Github
    sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

    degrees = sensor.read_temperature()
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    print ('Temp      = {0:0.3f} deg C'.format(degrees))
    print ('Pressure  = {0:0.2f} hPa'.format(hectopascals))
    print ('Humidity  = {0:0.2f} %'.format(humidity))


#Get ID # from operator and enroll
def enrollIDLoop():
    #userInput = input("ID # to store the finger as:")
    while(True):
        fID = input("ID # to store the finger or Q to quit:")
        
        if(fID.isdigit()):
            break
        elif((fID == 'q') or (fID == 'Q')):
            fID = ''
            main()
        else:
            print ("Must enter digit only")
    
    print ("Enrolling ID #" + fID)
    
    fRun = False
    while(not fRun):
        fRun = enrollFingerprint(fID)
        if(GPIO.input(inputPinExit) == False):
            main()


#Input Finger Print
def enrollFingerprint(enrollID):
    print ("Waiting for valid finger to enroll")
    time.sleep(0.5)
    
    p = False
    while (not p):
        p = Fingerprint.getImage()
        if(p):
            print ("Image taken")
            break
        elif(not p):
            print (".")
        else:
            print ("Unknown Error")
    
    time.sleep(0.5)
    p = Fingerprint.image2Tz(1)
    
    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p
    
    print ("Remove Finger")
    time.sleep(2.0)
    
    p = False
    print ("Place same finger again")
    time.sleep(1.0)
    while(not p):
        p = Fingerprint.getImage()
        
        if(p):
            print ("Image taken")
            break
        elif(not p):
            print (".")
        else:
            print ("Unknown Error")

    time.sleep(0.5)
    p = Fingerprint.image2Tz(2)
    
    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p

    #Converted
    time.sleep(0.5)
    p = Fingerprint.createModel()
    
    if(p):
        print ("Fingerprints match")
    elif(not p):
        print ("Fingerprints did not match")
        return p
    else:
        print ("Unknown Error")
        return p
    
    time.sleep(0.5)
    enrollIDbytes = int(enrollID, 16)
    p = Fingerprint.storeModel(enrollIDbytes, 1)
    
    if(p):
        print ("Stored fingerprint template")
        enrollIDLoop()
    elif(not p):
        print ("Store Fingerprint Error")
        return p
    else:
        print ("Unknown Error")
        return p
    
#Run fingerprint sensor
def runLoop(outputTimeout):
    print ("Waiting for valid finger...")
    #Finger Print Matched
    while(GPIO.input(inputPinExit) == True):
        if(getFingerprintIDez() == 1):
            LEDState(1,outputTimeout)
            
        #No match
        elif (getFingerprintIDez() == 2):
            
            LEDState(2,outputTimeout)
            
        #Other Case    
        elif(getFingerprintIDez() == -1):
            LEDState(3,outputTimeout)
            
    LEDflag = 0

            
    main()
    
#Finger Print Control LED
def LEDState(LEDflag, outputTimeout):
    #Finger Print matched , BlueLED is on (for "outputTimeout" seconds)
    if(LEDflag == 1):
        GPIO.output(outputPin, GPIO.HIGH)
        GPIO.output(redpin,GPIO.LOW)
        time.sleep(outputTimeout)
        
    #No match, Red LED blink for 10 times
    elif(LEDflag == 2):
        for i in range(10):
                GPIO.output(redpin, GPIO.HIGH)
                time.sleep(0.15)
                GPIO.output(redpin, GPIO.LOW)
                time.sleep(0.15)
    #Other cases
    else:
        LEDflag = 0
    
    GPIO.output(outputPin, GPIO.LOW)
    GPIO.output(redpin, GPIO.HIGH)

    
    
                

#Get fingerprint
def getFingerprintID():
    p = False
    while(not p):
        p = Fingerprint.getImage()
        if(p):
            print ("Image Taken")
            break
        elif(not p):
            print ("No finger detected")
        else:
            print ("Unknown Error")
    
    p = Fingerprint.image2Tz(1)
    
    if(p):
        print ("Image converted")
    elif(not p):
        print ("Image not converted")
        return p
    else:
        print ("Unknown Error")
        return p
    
    p = Fingerprint.fingerSearch()
    
    if(p):
        print ("Found fingerprint")
    elif(not p):
        print ("No fingerprint found")
        return p
    else:
        print ("Unknown Error")
        return p
    
#Get fingerprint quick
def getFingerprintIDez():
    
    p = Fingerprint.getImage()
    if(not p):
        return 0
    
    p = Fingerprint.image2Tz(1)
    if(not p):
        return -1

    #No Match Finger Print
    p = Fingerprint.fingerSearch()
    if(not p):
        return 2
    
    #print ("Found fingerprint")
    return (1)




#Main Function of FingerPrint Module
def main():
    
    #Time wait after Finger Print confirmed
    lockOnTime = 1
    #set-up output pin
    '''GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(outputPin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(redpin, GPIO.OUT, initial = GPIO.HIGH)
    GPIO.setup(inputPinExit, GPIO.IN, pull_up_down=GPIO.PUD_UP)'''
    # They are moved in the front
    
    #Set serial port and baudrate
    Fingerprint.begin()
    
    if(Fingerprint.checkFPComms()):
        print ("Found Fingerprint Sensor")
    else:
        print ("Did not find Fingerprint Sensor")
        main()
    while(True):
        print("1 - Enroll Fingerprints")
        print("2 - Run Fingerprint Sensor")
        print("3 - Save Notepad to File")
        print("4 - Load Notepad from File")
        print("5 - Erase Library")

        print("E - Exit")
        menuInput = input ("Please select option ")
        
        if((menuInput.isdigit()) and (menuInput == '1')):
            enrollIDLoop()
            break
        elif((menuInput.isdigit()) and (menuInput == '2')):
            lockOnTime = 3
            runLoop(lockOnTime)
            break
        elif((menuInput.isdigit()) and (menuInput == '3')):
            totalCount = Fingerprint.getTemplateCount()
            print ("Template count is " + str(totalCount))
            for i in range(1, totalCount + 1):
                if(Fingerprint.getNotepad(i) == True):
                    print("Success Writing ID File for " + str(i))
                else:
                    print("Error Writing ID File")
                    break
        elif((menuInput.isdigit()) and (menuInput == '4')):
            #run Fingerprint.writeNotepad(ID) until False (returns false when no ID found)
            writeID = 1
            while((Fingerprint.writeNotepad(writeID)) == True):
                writeID += 1
            print("Total ID's entered " + str(writeID - 1))
        elif((menuInput.isdigit()) and (menuInput == '5')):
            if(Fingerprint.emptyDatabase() == True):
                pass
            else:
                print("Error erasing library")
        elif((menuInput.isdigit()) and (menuInput == '6')):
            if(imageUpload() == True):
                pass
            else:
                print("Error uploading image and saving to file")
        elif((menuInput.isdigit()) and (menuInput == '7')):
            if(imageDownload() == True):
                pass
            else:
                print("Error opening file and downloading to sensor")
        elif((menuInput == 'E') or (menuInput == 'e')):
            menuInput = ''
            GPIO.cleanup()
            sys.exit()
        else:
            print ("Must select from the menu")
    
    GPIO.cleanup()    
    return 0
   
if __name__ == '__main__':
    main()
    
#End
