# bot.py

import discord
import firebase_admin
import threading
from firebase_admin import credentials
from firebase_admin import firestore

import tensorflow as tf
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

model = tf.keras.models.load_model('./mood_detector')
model.summary()

TOKEN = 'ODk5MDE2MTE3NDYzNDQ5NjEw.YWsoAQ.vjtAuskcZnZzs75ECJYXNpX7OwY'

cred = credentials.Certificate('/Users/clarajeon/Downloads/Coding/stereo_ml/firebase.json')
default_app = firebase_admin.initialize_app(cred)

client = discord.Client()

prefix = "!"
db = firestore.client()

# loading
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

label_arr = ['sadness', 'enthusiasm', 'love', 'hate', 'happiness', 'anger']

def prepare(texts):
  sequences = tokenizer.texts_to_sequences(texts)
  padded = pad_sequences(sequences, maxlen=100, padding='post', truncating='post')
  max_mood = predictIt(padded)
  return max_mood 

def predictIt(padded):
  prediction = model.predict(padded)
  max_mood = use_predict(prediction)
  return max_mood

def use_predict(prediction):
  prediction_human = []
  for text in prediction:
    current_max = 0
    max_index = -1
    for idx, num in enumerate(text):
      if num > current_max:
          current_max = num
          max_index = idx
    prediction_human.append(label_arr[max_index])
  label_dict = {'sadness': 0, 'enthusiasm': 0, 'love': 0, 'hate': 0, 'happiness': 0, 'anger': 0}
  for mood in prediction_human:
    label_dict[mood] = label_dict[mood] + 1
  max_mood = max(label_dict, key=label_dict. get)
  return max_mood

# Create an Event for notifying main thread.
callback_done = threading.Event()

# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f'Received document snapshot: {doc.id}')
        text = doc.to_dict()
        texts = text['text']
        print(texts)
        overall_mood = prepare(texts)
        print(overall_mood)
    callback_done.set()

doc_ref = db.collection(u'Entries').document(u'one')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    print("hello")

    # Watch the document
    message_content = str(message.content)

    if(message_content.startswith(prefix)):
        doc_ref.on_snapshot(on_snapshot)
        await message.channel.send('hi')    

client.run(TOKEN)