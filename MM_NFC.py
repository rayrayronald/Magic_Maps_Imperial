# 2018 - 2019 Imperial College London Biomedical Engineering Year 2 Engineering Design Project
# Ronald Hsu

# features to be added for users
# wifi connection
# reboot wifi
# wpa_cli -i wlan0 reconfigure
# reboot app
# GSM
# tutorial speech and button

# recently added
# audio loudness
# speaker
# on/off button
# Write tag
# Read tag and auto update coordinates
# faster reboot
# soft ware update



# Imports
import array
import urllib
import os
import struct
import RPi.GPIO as GPIO
import MFRC522

# GPIO setup
GPIO.setmode(GPIO.BOARD)

button_places = 16 #23  OOPS 12 #18
button_roads = 38 #20  OOPS 40 #21
#button_exit = 13 #27 IN LOOP SCRIPT
button_exit = 15 #22 TRIGGERS NFC RE-READ
button_UP = 29 #5
button_DOWN = 31 #6
GPIO.setup(button_places, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_roads, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_exit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

MIFAREReader = MFRC522.MFRC522()

# Constant Variables
TOTAL_X_CAP = 1016
TOTAL_Y_CAP = 762
#Radius = 100
#START_X = -0.1736854
#START_Y = 51.4966478
#END_X = -0.1640704
#END_Y = 51.5006107
NUMBER_READOUTS = 3
name = [0,0,0,0,0,0]
corner = [0,0,0,0,0,0]
ROAD_BUFFER = 40
NFC = True
KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
BLOCK_ADDRS = [8, 9, 10]


# Auto update
os.system("(cd ~/Magic_Maps_Imperial && git pull)")

# Main function
print ("IP Adress for SSH:")
os.system('hostname -I')
os.system('iwgetid')
os.system('espeak "Welcome to V I map by Group 12" 2>/dev/null')
file = open( "/dev/input/mice", "rb" );
print ("PROGRAM LOADED!\n")

def vol_up(channel):
#    	amixer scontrols
	os.system('amixer sset PCM 20+')
def vol_down(channel):
        os.system('amixer sset PCM 20-')
def wifi_add(channel):
        SSID = raw_input(os.system('espeak "Enter Wifi name" 2>/dev/null'))
        PSK = raw_input(os.system('espeak "Enter Wifi password" 2>/dev/null'))
def NFC_SCAN(channel):
	NFC = True
def places(channel):
        global Long
        global Lat
        print ("LOADING DATABASE...")
        URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?radius="+str(Radius)+"&key=AIzaSyA3aYU6UKfZkp8QfafB2WCfouPjxVrFx2A&location="+str(Lat)+","+str(Long)
        print URL, "\nPLACES DATABASE UPDATED!\n"
        html=urllib.urlopen(URL)
        htmltext=html.read()
        postname = 1
        for i in range(NUMBER_READOUTS+1):
                phrase =  "\"name\" : \""
                prename = htmltext.find(phrase,postname)
                postname =  htmltext.find("\"", prename+len(phrase)+1)
                name[i] = htmltext[prename+len(phrase):postname]
                if name[i] == "l_attributions":
                        os.system('espeak "There are no more places nearby" 2>/dev/null')
                        break
                if i == 0:
                            os.system('espeak "{0}, Top {1} places" 2>/dev/null'.format(name[i],NUMBER_READOUTS))
                else:
                        print i,": ", name[i]
                        os.system('espeak -s150 "{0}" 2>/dev/null'.format(name[i]))
def exit(channel):
        print ("QUITING PROGRAM...\nIP Address for SSH:")
        IP = os.system('hostname -I')
        wifi = os.system('iwgetid')
#        os.system('espeak "IP Address {0}, wifi {1)" 2>/dev/null'.format(IP,wifi))
        os.system('espeak "Refreshing" 2>/dev/null')
        raise SystemExit
def roads(channel):
        global Long
        global Lat
        URL_road = "https://roads.googleapis.com/v1/snapToRoads?&interpolate=true&key=AIzaSyA3aYU6UKfZkp8QfafB2WCfouPjxVrFx2A&path="
        #URL_road ="https://roads.googleapis.com/v1/nearestRoads?&key=AIzaSyA3aYU6UKfZkp8QfafB2WCfouPjxVrFx2A&points="
        for i in range(ROAD_BUFFER):
		print "GETTING ROAD DATA BUFFER...",i,"out of", ROAD_BUFFER
                buf = file.read(3)
                x,y = struct.unpack( "bb", buf[1:] );
                Long += x*X_SCALE
                Lat += y*Y_SCALE
                print ("Coord: x: %8f, y: %8f" % (Long, Lat));
                if i > 20:
                    URL_road += str(Lat)+","+str(Long)
                if i < ROAD_BUFFER-1 and i > 20:
                    URL_road += "|"
        print URL_road
        html=urllib.urlopen(URL_road)
        htmltext=html.read()
        print("ROAD SNAPPING LOADED!\n")
        postname = 1
        phrase =  "\"placeId\": \""
        prename = htmltext.find(phrase,postname)
        postname = htmltext.find("\"", prename+len(phrase)+1)
        placeId = htmltext[prename+len(phrase):postname]
        URL = "https://maps.googleapis.com/maps/api/place/details/json?&key=AIzaSyA3aYU6UKfZkp8QfafB2WCfouPjxVrFx2A&placeid="+placeId
        print "Place Id: ", placeId, "\n" , URL, "\nROAD NAME UPDATED!\n"
        html=urllib.urlopen(URL)
        htmltext=html.read()
        postname = 1
        phrase =  "\"formatted_address\" : \""
        prename = htmltext.find(phrase,postname)
        postname =  htmltext.find(",", prename+len(phrase)+1)
        road_address = htmltext[prename+len(phrase):postname]
        print("Road name: "),
        print(road_address)
        os.system('espeak -s150 "{0}" 2>/dev/null'.format(road_address))

GPIO.add_event_detect(button_places, GPIO.FALLING, callback=places, bouncetime=700)
GPIO.add_event_detect(button_exit, GPIO.FALLING, callback=exit, bouncetime=700)
GPIO.add_event_detect(button_roads, GPIO.FALLING, callback=roads, bouncetime=700)
GPIO.add_event_detect(button_UP, GPIO.FALLING, callback=vol_up, bouncetime=700)
GPIO.add_event_detect(button_DOWN, GPIO.FALLING, callback=vol_down, bouncetime=700)



while True:
        NFC_count = 0
        while NFC:
            while NFC_count < 10:
                NFC_count += 1
                print ("Waiting NFC...")
                (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
                if status == MIFAREReader.MI_OK:
                    print "Card detected"
                    (status, uid) = MIFAREReader.MFRC522_Anticoll()
                    MIFAREReader.MFRC522_SelectTag(uid)
                    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 11, KEY, uid)
                data = []
                coord = ''
                if status == MIFAREReader.MI_OK:
                    for block_num in BLOCK_ADDRS:
                        block = MIFAREReader.MFRC522_Read(block_num)
                        if block:
                            data += block
                    if data:
                        coord = ''.join(chr(i) for i in data)
                    MIFAREReader.MFRC522_StopCrypto1()
                    print coord
                    sep_pos_A = -1
                    separator =  ","
                    for i in range(4):
                        sep_pos_B =  coord.find(separator,sep_pos_A+1)
                        corner[i] = coord[sep_pos_A+1:sep_pos_B]
                        sep_pos_A = sep_pos_B
                        print i,": ", corner[i]
                    NFC = False
                    NFC_count = 10
                    START_X = float(corner[0])
                    START_Y = float(corner[1])
                    END_X = float(corner[2])
                    END_Y = float(corner[3])
                    X_SCALE = abs(START_X - END_X)/TOTAL_X_CAP
                    Y_SCALE = abs(START_Y - END_Y)/TOTAL_Y_CAP
                    Long = (END_X - START_X) /2 + START_X
                    Lat = (END_Y - START_Y) /2 + START_Y
                    Radius = abs(START_X - END_X)*15000
                    URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?radius="+str(Radius)+"&key=AIzaSyA3aYU6UKfZkp8QfafB2WCfouPjxVrFx2A&location="+str(Lat)+","+str(Long)
                    html=urllib.urlopen(URL)
                    htmltext=html.read()
                    phrase =  "\"name\" : \""
                    prename = htmltext.find(phrase,1)
                    postname =  htmltext.find("\"", prename+len(phrase)+1)
                    city = htmltext[prename+len(phrase):postname]
                    os.system('espeak -s150 "Chosen map is {0}" 2>/dev/null'.format(city))
            NFC = False
            Radius = 100
            START_Y =51.4966478
            START_X =-0.1736854
            END_Y =51.5006107
            END_X =-0.1640704
            TOTAL_X_CAP =1016
            TOTAL_Y_CAP =762
            X_SCALE = abs(START_X - END_X)/TOTAL_X_CAP
            Y_SCALE = abs(START_Y - END_Y)/TOTAL_Y_CAP
            Long = (END_X - START_X) /2 + START_X
            Lat = (END_Y - START_Y) /2 + START_Y
            print ("No NFC detcted, using default parameters")
        buf = file.read(3)
        x,y = struct.unpack( "bb", buf[1:] );
        Long += x*X_SCALE
        Lat += y*Y_SCALE
        print ("Coord: x: %8f, y: %8f" % (Long, Lat));

