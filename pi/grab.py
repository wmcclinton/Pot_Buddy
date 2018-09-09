import pyrebase
from PIL import Image
import time


config = {
  "apiKey": "AIzaSyB-WNogLywSkad69Ex9-ZxsJucQ0TeVYy0",
  "authDomain": "tagmosquito.firebaseapp.com",
  "databaseURL": "https://tagmosquito.firebaseio.com",
  "storageBucket": "tagmosquito.appspot.com"
}

configNew = {
    "apiKey": "AIzaSyDocUV2hrCEqrywwIYaER7NVxWuV_V_q6o",
    "authDomain": "potbuddy-d1760.firebaseapp.com",
    "databaseURL": "https://potbuddy-d1760.firebaseio.com",
    "storageBucket": "potbuddy-d1760.appspot.com"
}


firebase = pyrebase.initialize_app(config)

db = firebase.database()

ids = db.child('images/').get()
keys_dict = ids.val().keys()
keys = []
for key in keys_dict:
  keys.append(key)

storage = firebase.storage()
filename = keys[0]
storage.child(filename+'.jpg').download(filename+'.jpg')

img = Image.open(filename+'.jpg')
img.save(filename+'.bmp','bmp')

###########

found = False


def stream_handler(post):
    new_id = post["path"]
    if new_id != '/' and post["event"] == "put":
      new_id = new_id.split("/")
      new_id = new_id[1]
      db.child("images/"+ new_id+ "/result").set("Aedes")

my_stream = db.child("images/").stream(stream_handler, None)

while 1:
  time.sleep(100)
    
