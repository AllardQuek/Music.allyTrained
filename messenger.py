#!/usr/bin/env python
# coding:utf-8
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

# Messenger API integration example
# We assume you have:
# * a Wit.ai bot setup (https://wit.ai/docs/quickstart)
# * a Messenger Platform setup (https://developers.facebook.com/docs/messenger-platform/quickstart)
# You need to `pip install the following dependencies: requests, bottle.
#
# 1. pip install requests bottle
# 2. You can run this example on a cloud service provider like Heroku, Google Cloud Platform or AWS.
#    Note that webhooks must have a valid SSL certificate, signed by a certificate authority and won't work on your localhost.
# 3. Set your environment variables e.g. WIT_TOKEN=your_wit_token
#                                        FB_PAGE_TOKEN=your_page_token
#                                        FB_VERIFY_TOKEN=your_verify_token
# 4. Run your server e.g. python examples/messenger.py {PORT}
# 5. Subscribe your page to the Webhooks using verify_token and `https://<your_host>/webhook` as callback URL.
# 6. Talk to your bot on Messenger!

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import requests
from sys import argv
from wit import Wit
from bottle import Bottle, request, debug
import mingus.core.intervals as intervals
import mingus.core.chords as chords
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Wit.ai parameters
WIT_TOKEN = os.environ.get('WIT_TOKEN')
# Messenger API parameters
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')

# Setup Spotify Credentials
spotify_cid = '06175aec93d14903bad4abb8ea0f16c7'
spotify_secret = '45be25e4ab4a4f7888cd3b18e0d49983'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=spotify_cid, client_secret=spotify_secret))

# Setup Bottle Server
debug(True)
app = Bottle()


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get('hub.verify_token')
    # check whether the verify tokens match
    if verify_token == FB_VERIFY_TOKEN:
        # respond with the challenge to confirm
        challenge = request.query.get('hub.challenge')
        return challenge
    else:
        return 'Invalid Request or Verification Token'

# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """

    data = request.json

    if data['object'] == 'page':
        for entry in data['entry']:
            # get all the messages
            messages = entry['messaging']
            # print(messages)
            if messages[0]:
                # Get the first message
                message = messages[0]
                # Yay! We got a new message!
                # We retrieve the Facebook user ID of the sender
                fb_id = message['sender']['id']
                # We retrieve the message content
                text = message['message']['text']
                response = client.message(text)
                print("RESPONSE:", response)
                
                # Let's forward the message to Wit /message
                # and customize our response to the message in handle_message
                # response = client.message(msg=text, context={'session_id':fb_id})
                handle_message(response=response, fb_id=fb_id)
    else:
        # Returned another event
        return 'Received Different Event'
    return None

def fb_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN

    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content

def quick_reply(sender_id, text_list):
    """
    Generate a quick reply with 3 options. Text list must contain 4 items; 1 text message and 3 text options
    """
    data = {
          'recipient': {'id': sender_id},
          'message': {
              'text': text_list[0],
              'quick_replies': [
                {
                  "content_type":"text",
                  "title":text_list[1],
                  "payload":"<POSTBACK_PAYLOAD>",
                  # "image_url":"http://example.com/img/red.png"
                },{
                  "content_type":"text",
                  "title":text_list[2],
                  "payload":"<POSTBACK_PAYLOAD>",
                  # "image_url":"http://example.com/img/green.png"
                },{
                  "content_type":"text",
                  "title":text_list[3],
                  "payload":"<POSTBACK_PAYLOAD",
                }
              ]
          }
    }
    
    qs = 'access_token=' + FB_PAGE_TOKEN
    
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content
    
def first_trait_value(traits, trait):
    """
    Returns first trait value
    """
    if trait not in traits:
        return None
    val = traits[trait][0]['value']
    if not val:
        return None
    return val

def handle_start(fb_id):
    """
    Handle starting interaction
    """
    res = requests.get(f"https://graph.facebook.com/v7.0/{fb_id}?fields=id%2Cname&access_token=EAAEcGDMoZAxMBAIVxwA7ODhUGGQjjJcZAbQcivRbZCfZB0qsS92nqoCrvTWlj8wzC2gGMiNGi9XJCFpc8XsMhlXPuzbxz1OiWZBuZBxhfvF94vU0OtMR588hXUTdTETyPZA2ujjnPeucaQOVOp0nVSZA2yeK9uZAF2EqcIa4OzM65gwZDZD")
    name = res.json()['name']
    first_name = name.split(' ')[0]
    text = f"Greetings {first_name}! You can ask me about music theory or history, I would be happy to help!"
    text_list = ["What would you like to get?", "Interval", "Notes", "Songs"]
    fb_message(fb_id, text)
    quick_reply(fb_id, text_list)
    
def handle_gibberish(response, fb_id):
    """
    Handle whatever random gibberish user sends
    """
    text = f"Sorry! We did not quite understand \"{response['text']}\" :("
    text_1 = "Try asking me about music theory or history!"
    fb_message(fb_id, text)
    fb_message(fb_id, text_1)

def get_interval(response, fb_id):
    """
    Identify the 2 notes user sent. Input to library function and return identified interval as response back to user
    """
    try:
        notes = response['entities']["Note:Note"]
        note1 = notes[0]['value']
        note2 = notes[1]['value']
    except (KeyError, IndexError) as e:
        text = "Sorry, I don't think you provided enough notes :/"
        return text     # Exit early

    try:
        interval = intervals.determine(note1, note2)
        text = f"The interval between {note1} and {note2} is {interval}."
    except Exception as e:
        print("EXCEPTION", e)
        text = f"Sorry! I don't know the interval between {note1} and {note2} :/"

    return text 

def get_notes_from_chord(response, fb_id):
    """
    Identify the chord user sent. Input to libary function and return chord's notes as response back to user
    """
    # ? AND/OR: Identify the notes user sent. Input to library function and return identified chord as response back to user
    # ? When user requests 7th chord, check if trait "7th" is present
    # ? When user requests inversions, check if trait "inversion" and get it's value, then use inversion function on chord
    try:
        kq_entity = response['entities']["Key_Quality:Key_Quality"][0]
    except KeyError as e:
        text = "Sorry! I couldn't identify the chord name :/"
        return text     # Exit early

    key_quality = kq_entity['value']
    key_quality = key_quality.lower()
    key_quality = key_quality.capitalize()

    try:
        note = kq_entity['entities'][0]['value']
    except (KeyError, IndexError) as e:
        # Could arise when user joins key with quality (e.g. Fmajor)
        text = "Sorry! I'm not sure what the key is :/"
        return text     # Exit early
    
    if 'maj' in key_quality or 'major' in key_quality:
        key_quality = note + 'maj' 
    elif 'min' in key_quality or 'minor' in key_quality:
        key_quality = note + 'min'
    else:
        key_quality = note

    try:
        notes_list = chords.from_shorthand(key_quality)
        notes_str = ', '.join(notes_list)
        text = f"The notes in a {key_quality} chord are {notes_str}."
    except Exception as e:
        print("EXCEPTION:", e)
        text = f"Sorry! I can't identify a {kq_entity['body']} chord :/"    

    return text 

def get_songs_from_progression(response, fb_id):
    """
    Get songs from chord progression (e.g. 1,4,5)
    """
    try:
        prog = response['entities']["Progression:Progression"][0]['body']
    except KeyError:
        text = "Sorry, I couldn't identify your progression :/ Please try again!"
        return text     # Exit early

    prog_list = prog.split(',')
    prog_csv = ','.join(i.strip() for i in prog_list)
    res = requests.get("https://api.hooktheory.com/v1/" + f"trends/songs?cp={prog_csv}",
                    headers={'Authorization': 'Bearer 06e6698541901e71cece0b359c6077b3'},
                    )
    result = res.json()
    text = ""
    count = 1

    # Limit to 5 songs for readability
    if len(result) > 5:
        result = result[:5]

    for song in result:
        title = song['song']
        artist = song['artist']
        section = song['section']

        query = f"{title} {artist}"
        q_result = sp.search(q=query, type="track", limit=1)
        q_items = q_result['tracks']['items']
        if len(q_items) == 0:
            song_url = "Sorry, this song is not on Spotify :/"
        else:
            song_url = q_items[0]['external_urls']['spotify']

        item = f"{count}. {title} ({section}) by {artist}\n{song_url}\n"
        text += item
        count += 1

    return text

def handle_message(response, fb_id):
    """
    Customizes our first response to the message and sends it
    """
    # Checks if user's message is a greeting
    # Otherwise we will just repeat what they sent us
    greetings = first_trait_value(response['traits'], 'wit$greetings')
    thanks = first_trait_value(response['traits'], 'wit$thanks')
    bye = first_trait_value(response['traits'], 'wit$bye')
    user_msg = response['text']
    allow_quick_reply = False
    
    if greetings:
        handle_start(fb_id)
        return
    elif user_msg == "Interval":
        text = "I could tell you the interval between 2 notes :)"
        text_list = ["You might ask:", "C to G", "D to Ab", "Eb to F#"]
        allow_quick_reply = True
    elif user_msg == "Notes":
        text = "I could tell you the notes from the name of a chord :)"
        text_list = ["You might ask:", "C major chord", "D# major chord", "Ab minor chord"]
        allow_quick_reply = True
    elif user_msg == "Songs":
        text = "I could share with you songs with certain chord progressions :)"
        text_list = ["You might ask:", "1,4,5", "2,3,6", "3,5,2"]
        allow_quick_reply = True
    elif thanks:
        text = "No problem!"
    elif bye:
        text = "Goodbye! Have a nice day :)"
    else:
        if not response['intents']:
            handle_gibberish(response, fb_id)
            return

        intent = response['intents'][0]['name']
        
        if intent == 'Greetings':
            handle_start(fb_id)
            return
        elif intent == 'getInterval':
            text = get_interval(response, fb_id)
        elif intent == 'getChords':
            text = get_notes_from_chord(response, fb_id)
        elif intent == 'getSongsFromProgression':
            text = get_songs_from_progression(response, fb_id)
        elif intent == 'getComposer':
            try:
                if response['entities']['Romantic_Composer:Pyotr_Ilyich_Tchaikovsky'][0]['name'] == 'Romantic_Composer':
                    text = "\"{response['text']}\" was a composer from the Romantic era. Read more here: https://en.wikipedia.org/wiki/List_of_Romantic-era_composers"
                elif response['entities']['Baroque_Composer:Johann_Sebastian_Bach'][0]['name'] == 'Baroque_Composer':
                    text = "\"{response['text']}\" was a composer from the Baroque era, marked by little variations in tempo and 4/4 timings. Read more here: https://en.wikipedia.org/wiki/List_of_Baroque_composers"
                else:
                    text = "I don't know this composer. Yet ;)"
            except KeyError:
                text = "Looks like something went wrong o.o"
        elif intent == 'getJokes':         
            sequence = ["Why couldn't the string quartet find their composer? He was Haydn.",
                        "Arnold Schoenberg walks into a bar. 'I'll have a gin please, but no tonic.'", 
                        "Why didn't Handel go shopping? Because he was Baroque.", 
                        "How do you fix a broken brass instrument? With a tuba glue.", 
                        "Middle C, E flat and G walk into a bar. 'Sorry,' the barman said. 'We don't serve minors.'",
                        "TEMPO TANTRUM:  What an elementary school orchestra is having when it's not following the conductor.",
                        "FLUTE FLIES:  Those tiny mosquitoes that bother musicians on outdoor gigs.",
                        "ALLREGRETTO:  When you're 16 measures into the piece and realize you took too fast a tempo.",
                        "Why did the pianist keep banging his head against the keys? He was playing by ear.",
                        "Want to hear a joke about a staccato? Never mind, it's too short.",
                        "How about a fermata joke? Never mind, it's too long."]
            joke = random.choice(sequence)
            text = joke
        elif intent == 'getSongsbyComposer':
            #the below code works, lists top 10 tracks of 2020
            artist_name = []
            track_name = []
            popularity = []

            for i in range(0,10,20):
                track_results = sp.search(q='year:2020', type='track', limit=10) 
                for i, t in enumerate(track_results['tracks']['items']):
                    artist_name.append(t['artists'][0]['name'])
                    track_name.append(t['name'])
                    popularity.append(t['popularity'])                    
                print("Enter a number from 0-9: ")
                x = int(input())
                while x >= len(artist_name):
                    x = int(input("Please enter a number from 0-9: "))

                # Check if x is within range
                print(len(artist_name))

                print ("Artist: " + str(artist_name[x]))
                print("******************************")
                print("Track: " + str(track_name[x]))
                print("******************************")
                print("Popularity: " + str(popularity[x]) + "/100")
                print('END')
        elif intent == 'getRandomSong':
            results = sp.search(str(input()), limit=20)
            for idx, track in enumerate(results['tracks']['items']):
                print(idx, track['name'])
        else:
            text = "Sorry, I couldn't quite understand. Please rephrase your question?"   

    # Send response back to user
    fb_message(fb_id, text)
    if allow_quick_reply:
        quick_reply(fb_id, text_list)
        
        
# Setup Wit Client
client = Wit(access_token=WIT_TOKEN)

if __name__ == '__main__':
    # Run Server
    app.run()                                   # Need gunicorn !!!        
    # app.run(host='0.0.0.0', port=8080)        WORKS
    # app.run(host='0.0.0.0', port=argv[1])     Procfile how?
