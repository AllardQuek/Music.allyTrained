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
    """Handler for webhook (currently for postback and messages)."""
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
    """Function for returning response to messenger."""
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
    Generate a quick reply with 3 options. 
    
    Parameters --
        :sender_id: Sender's Facebook ID
        :text_list: A list of 4 strings (1 text message and 3 text options)
    
    Returns --
        :resp.content: Text message sent to the user
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
    """Returns first trait value."""
    if trait not in traits:
        return None
    val = traits[trait][0]['value']
    if not val:
        return None
    return val

def handle_start(fb_id):
    """Handle starting interaction."""
    res = requests.get(f"https://graph.facebook.com/v7.0/{fb_id}?fields=id%2Cname&access_token=EAAEcGDMoZAxMBAIVxwA7ODhUGGQjjJcZAbQcivRbZCfZB0qsS92nqoCrvTWlj8wzC2gGMiNGi9XJCFpc8XsMhlXPuzbxz1OiWZBuZBxhfvF94vU0OtMR588hXUTdTETyPZA2ujjnPeucaQOVOp0nVSZA2yeK9uZAF2EqcIa4OzM65gwZDZD")
    name = res.json()['name']
    first_name = name.split(' ')[0]
    text = f"Greetings {first_name}! My name is Cally and I love music! Feel free to ask me about anything from music theory, songs, composers, instruments and even jokes! :D"
    text_list = ["Here are a few suggestions:", "Interval", "Notes", "Songs"]
    fb_message(fb_id, text)
    quick_reply(fb_id, text_list)
    
def handle_gibberish(response, fb_id):
    """Handle any random gibberish user sends."""
    text = f"Sorry! We did not quite understand \"{response['text']}\" :("
    text_1 = "You can ask me about music theory, songs, composers, instruments, or even jokes!"
    fb_message(fb_id, text)
    fb_message(fb_id, text_1)

def get_interval(response, fb_id):
    """Determnine the interval between 2 notes."""
    try:
        # Extract the 2 notes user sent
        notes = response['entities']["Note:Note"]
        note1 = notes[0]['value']
        note2 = notes[1]['value']
    except (KeyError, IndexError) as e:
        text = "Sorry, I don't think you provided enough notes :/"
        return text     # Exit early

    try:
        # Determine interval between notes
        interval = intervals.determine(note1, note2)
        text = f"The interval between {note1} and {note2} is {interval}."
    except Exception as e:
        print("EXCEPTION", e)
        text = f"Sorry! I don't know the interval between {note1} and {note2} :/"

    return text 

def get_notes_from_chord(response, fb_id):
    """Determine notes in a chord given the chord's name."""
    # ? AND/OR: Extract the notes user sent. Input to library function and return identified chord as response back to user
    # ? When user requests 7th chord, check if trait "7th" is present
    # ? When user requests inversions, check if trait "inversion" and get it's value, then use inversion function on chord
    try:
        # Extract Key-Quality (e.g. F major)
        kq_entity = response['entities']["Key_Quality:Key_Quality"][0]
    except KeyError as e:
        text = "Sorry! I couldn't identify the chord name :/"
        return text     # Exit early

    # Handle the various valid forms of key quality (e.g. f maj)
    key_quality = kq_entity['value']
    key_quality = key_quality.lower()
    key_quality = key_quality.capitalize()

    try:
        # Extract the key of the chord
        note = kq_entity['entities'][0]['value']
    except (KeyError, IndexError) as e:
        # Could arise when user joins key with quality (e.g. Fmajor)
        text = "Sorry! I'm not sure what the key is :/"
        return text     # Exit early
    
    # Format user input to requirement of from_shorthand() method
    if 'maj' in key_quality or 'major' in key_quality:
        key_quality = note + 'maj' 
    elif 'min' in key_quality or 'minor' in key_quality:
        key_quality = note + 'min'
    else:
        key_quality = note

    try:
        # Determine the notes in requested chord
        notes_list = chords.from_shorthand(key_quality)
        notes_str = ', '.join(notes_list)
        text = f"The notes in a {key_quality} chord are {notes_str}."
    except Exception as e:
        print("EXCEPTION:", e)
        text = f"Sorry! I can't identify a {kq_entity['body']} chord :/"    

    return text 

def get_songs_from_progression(response, fb_id):
    """Return songs using given chord progression (e.g. 1,4,5)."""
    try:
        # Extract chord progression from user input 
        prog = response['entities']["Progression:Progression"][0]['body']
    except KeyError:
        text = "Sorry, I couldn't identify your progression :/ Please try again!"
        return text     # Exit early

    # Handle case where user types a space between commas
    prog_list = prog.split(',')
    prog_csv = ','.join(i.strip() for i in prog_list)

    # Make GET request to Hooktheory API to obtain songs with requested chord progression
    res = requests.get("https://api.hooktheory.com/v1/" + f"trends/songs?cp={prog_csv}",
                    headers={'Authorization': 'Bearer 06e6698541901e71cece0b359c6077b3'},
                    )
    result = res.json()
    text = f"Here you go! These songs contain the {prog_csv} chord progression: :)\n"
    count = 1

    # Limit to first 5 songs for readability
    if len(result) > 5:
        result = result[:5]

    for song in result:
        title = song['song']
        artist = song['artist']
        section = song['section']

        # Make GET request to Spotify API to obtain the song's Spotify URL
        query = f"{title} {artist}"
        q_result = sp.search(q=query, type="track", limit=1)
        q_items = q_result['tracks']['items']

        if len(q_items) == 0:
            # If no Spotify URL is found, return error message instead
            song_url = "Sorry, this song is not on Spotify :/"
        else:
            song_url = q_items[0]['external_urls']['spotify']

        # Format text response so it appears neatly on Messenger
        item = f"{count}. {title} ({section}) by {artist}\n{song_url}\n"
        text += item
        count += 1

    return text

def get_joke(respones, fb_id):
    """Return a random joke from our list."""
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
                "How about a fermata joke? Never mind, it's too long.",
                "What kind of music is scary for balloons? Pop music."]
    joke = random.choice(sequence)

    return joke

def get_random_song(response, fb_id):
    """Return random song from top 20 tracks of 2020."""
    artist_name = []
    track_name = []
    popularity = []

    for i in range(0,10,20):
        track_results = sp.search(q='year:2020', type='track', limit=20) 
        for i, t in enumerate(track_results['tracks']['items']):
            artist_name.append(t['artists'][0]['name'])
            track_name.append(t['name'])
            popularity.append(t['popularity'])     

    num = random.randint(0,19)
    text = ""
    text += f"Artist: {artist_name[num]}\n"
    text += f"Track: {track_name[num]}\n"
    text += f"Popularity: {str(popularity[num])}/100\n"
    text += f"Link: {track_results['tracks']['items'][num]['external_urls']['spotify']}"

    return text

def get_composer(response, fb_id):
    """Return info about the type of composer and provide URL to more info."""
    try:
        entities = response['entities']
        if 'Baroque_Composer:Baroque_Composer' in entities:
            text = f"{entities['Baroque_Composer:Baroque_Composer'][0]['value']} was a composer from the Baroque era, marked by ostinato (i.e. persistent, repeating bassline) and has little variations in tempo in 4/4 timing. Read more here: https://en.wikipedia.org/wiki/List_of_Baroque_composers"
        elif 'Classical_Composer:Classical_Composer' in entities:
            text = f"{entities['Classical_Composer:Classical_Composer'][0]['value']} was a composer from the Classical era, marked by homophonic texture (i.e. one melodic line on top of the bass lines) and sometimes has alberti bass. Read more here: https://en.wikipedia.org/wiki/Classical_period_(music) "             
        elif 'Romantic_Composer:Romantic_Composer' in entities:
            text = f"{entities['Romantic_Composer:Romantic_Composer'][0]['value']} was a composer from the Romantic era, characterised by prolific use of rubato (i.e. varying music tempo). Read more here: https://en.wikipedia.org/wiki/List_of_Romantic-era_composers"
        elif 'Modern_Composer:Modern_Composer' in entities:
            text = f"{entities['Modern_Composer:Modern_Composer'][0]['value']} was a composer from the Modern era, characterised by dissonant (i.e. clashing) chords and sounds. Read more here: https://en.wikipedia.org/wiki/Modernism_(music)"
        else:
            text = "I don't know this composer. Yet ;)"
    except KeyError:
        text = "Sorry, we are still working on this feature. Try again next time!"
    
    return text

def get_instrument_section(response, fb_id):
    """Return the section an instrument is from."""
    if 'Instruments:Percussion' in response['entities']:
        text = "This is a percussion instrument. Read more here: https://en.wikipedia.org/wiki/Percussion_instrument"
    elif 'Instruments:Brass' in response['entities']:        
        text = "This is a brass instrument. Read more here: https://en.wikipedia.org/wiki/Brass_instrument"
    elif 'Instruments:Wind' in response['entities']:        
        text = "This is a wind instrument. Read more here: https://en.wikipedia.org/wiki/Wind_instrument"
    elif 'Instruments:String' in response['entities']:        
        text = "This is a string instrument. Read more here: https://en.wikipedia.org/wiki/String_instrument" 
    else:
        text = "Sorry! I haven't seen this instrument before :o"

    return text

def handle_message(response, fb_id):
    """Handle all messages from user and send response back to Messenger."""
    greetings = first_trait_value(response['traits'], 'wit$greetings')
    thanks = first_trait_value(response['traits'], 'wit$thanks')
    bye = first_trait_value(response['traits'], 'wit$bye')
    user_msg = response['text']
    allow_quick_reply = False
    
    if greetings:
        handle_start(fb_id)
        return
    elif user_msg == "Interval":
        # If user chose one of the inital quick replies, provide more info and allow another quick reply
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
        # Handle all other messages
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
            text = get_composer(response,fb_id)
        elif intent == 'getJokes':         
            text = get_joke(response, fb_id)
        elif intent == 'getInstrument':
            text = get_instrument_section(response, fb_id)
        elif intent == 'getRandomSong':
            text = get_random_song(response, fb_id)
        elif intent == 'getSongsByComposer':             
            text = 'This functionality is still a work in progress! Check back again soon ;)'
        else:
            # If intent detected but not scripted for yet
            text = "Sorry, I couldn't quite understand. Please rephrase your question?"   

    # Send response back to user
    fb_message(fb_id, text)

    # This would be True if user had chosen one of the inital quick replies when getting started
    if allow_quick_reply:
        quick_reply(fb_id, text_list)
        
        
# Setup Wit Client
client = Wit(access_token=WIT_TOKEN)

if __name__ == '__main__':
    # Run Server
    app.run()                                   # Need gunicorn !!!        
    # app.run(host='0.0.0.0', port=8080)        WORKS
    # app.run(host='0.0.0.0', port=argv[1])     Procfile how?