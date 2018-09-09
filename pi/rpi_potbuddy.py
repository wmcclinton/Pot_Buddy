import serial
import datetime
import time
import pyrebase
from gtts import gTTS
import os

# BEWARE this restarts Ard
# Arduino Serial Connection
ser=serial.Serial("/dev/ttyACM0",9600)

# Initilizing Firebase database
config = {
    "apiKey": "AIzaSyDocUV2hrCEqrywwIYaER7NVxWuV_V_q6o",
    "authDomain": "potbuddy-d1760.firebaseapp.com",
    "databaseURL": "https://potbuddy-d1760.firebaseio.com",
    "storageBucket": "potbuddy-d1760.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# User defined thresholds
global daily_light
global max_temp
global min_temp
global max_moisture
global min_moisture

daily_light = 1
max_temp = 80
min_temp = 65
max_moisture = 80
min_moisture = 20

# Init Plant Name
global plantName
plantName = None

# Get User plants and threshold listener
def stream_handler(post):
    plants = db.child("PA2/Plants").get().val()
    #print(plants)
    global plantName
    plantName = None
    
    global daily_light
    global max_temp
    global min_temp
    global max_moisture
    global min_moisture
    
    # Get Plant
    for key, val in plants.items():
        if(val == True):
            #print(key)
            plantName = key
    
    # Get Thresholds
    if(plantName != None):
        thresholds = db.child("PA2/" + plantName + "/thresholds").get().val()
        print(thresholds)
        
        daily_light = (int)(thresholds["LightDuration"])
        max_temp = (int)(thresholds["TempMax"])
        min_temp = (int)(thresholds["TempMin"])
        max_moisture = (int)(thresholds["MoistureMax"])
        min_moisture = (int)(thresholds["MoistureMin"])
           
my_stream = db.child("PA2").stream(stream_handler, None)

# Function to upload to Firebase
def upload():
    global data
    global plantName
    try:
        light_sensors = [(int)(i) for i in data[1][1].split("/")]
        temp = (float)(data[1][2])
        moisture = (float)(data[1][3].replace("\\r\\n'",""))
    except ValueError:
        light_sensors = [0, 0, 0, 0]
        temp = 0.0
        moisture = 0
    
    data_block = {
        "Light": sum(light_sensors)/4,
        "Temp": temp,
        "Moisture": moisture,
        "CurrentLight": data[2],
        "Status": data[1][0],
        "Time": data[0],
        "Raw": data[1][1]
    }
    if(plantName != None):
        result = db.child("PA2/" + plantName + "/history/" + data[0]).set(data_block)
        cresult = db.child("PA2/" + plantName + "/current").set(data_block)
        #print(result)
        #print(cresult)
    
def say(s):
    os.system("mpg321 " + s)
    print("SAY -> " + s)
    
# Prints line in Ard Setup "Arduino Init..."
print(ser.readline())
print(time.mktime(datetime.datetime.now().timetuple()))

# First Command
ser.write(str.encode("Test"))

ard_info = ""
current_daily_light = 0
last_time = 0
while(ard_info != "DONE"):
    current_time = time.mktime(datetime.datetime.now().timetuple())
    if(current_time%2 == 0):
        # Gets data command from Ard
        ard_info = ser.readline()
        ard_data = str(ard_info).split("-")
        print(ard_data)
        try:
            light_sensors = [(int)(i) for i in ard_data[1].split("/")]
            temp = (float)(ard_data[2])
            moisture = (float)(ard_data[3].replace("\\r\\n'",""))
            print(light_sensors)
        except ValueError:
            light_sensors = [0, 0, 0, 0]
            temp = 0.0
            moisture = 0
            
            
        ## Preform action based on data ##
        bad_temp = 0
        bad_moisture = 0
        bad_daily_light = 0
        in_light = 0

        # Check Temp
        if(temp > max_temp):
            bad_temp = 1
        if(temp < min_temp):
            bad_temp = -1
        
        # Check Moisture
        if(moisture > max_moisture):
            bad_moisture = 1
        if(moisture < min_moisture):
            bad_moisture = -1
        
        # Check Daily Light
        if(current_daily_light%86400 == 0):
            current_daily_light = 0
        if(current_daily_light > daily_light):
            bad_daily_light = 1
        else: 
            bad_daily_light = -1
            
        # Check if in Light
        min_light_thresh = 200
        max_light_thresh = 400
        if(light_sensors[0] > max_light_thresh and light_sensors[1] > max_light_thresh and light_sensors[2] > max_light_thresh and light_sensors[3] > max_light_thresh):
            in_light = 1
        elif(not ((light_sensors[0] >= min_light_thresh and light_sensors[1] >= min_light_thresh) \
           or (light_sensors[0] >= min_light_thresh and light_sensors[2] >= min_light_thresh) \
           or (light_sensors[0] >= min_light_thresh and light_sensors[3] >= min_light_thresh) \
           or (light_sensors[1] >= min_light_thresh and light_sensors[2] >= min_light_thresh) \
           or (light_sensors[1] >= min_light_thresh and light_sensors[3] >= min_light_thresh) \
           or (light_sensors[2] >= min_light_thresh and light_sensors[3] >= min_light_thresh))):
            in_light = -1
        else:
            in_light = 0
            
        
        # Perform Actions
        if(current_time%10 == 0):
            #if(bad_temp != 0 and bad_moisture != 0):
                #say("BOTH")
                # Fix this
            if(bad_temp == 1):
                say("hot.mp3")
            if(bad_temp == -1):
                say("cold.mp3")
            if(bad_moisture == 1):
                say("wet.mp3")
            if(bad_moisture == -1):
                say("dry.mp3")

        # Set Modes for arduino
        if(plantName != None and in_light != 1  and bad_daily_light == -1):
            # Send new Pi command to Ard
            ser.write(str.encode("GOLIGHT"))
        elif(plantName != None and in_light != -1 and bad_daily_light == 1):
            # Send new Pi command to Ard
            ser.write(str.encode("GODARK"))
        else:
            # Send new Pi command to Ard
            ser.write(str.encode("REST"))
        #
    # Uploads data to Firebase
    if(current_time%10 == 0):
        print(current_time)
        
        # Upload Ard data to Firebase
        global data
        data = (str(current_time).split(".")[0], str(ard_info).split("-"),current_daily_light)
        upload()
        
    if(current_time%60 == 0):
        if(last_time != current_time):
            current_daily_light += 1 # Minutes
        last_time = current_time       