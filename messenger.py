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


# Wit.ai parameters
WIT_TOKEN = os.environ.get('WIT_TOKEN')
# Messenger API parameters
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')

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

def quick_reply(sender_id):
    data = {
          'recipient': {'id': sender_id},
          'message': {
              'text': "What would you like to do?",
              'quick_replies': [
                {
                  "content_type":"text",
                  "title":"Interval",
                  "payload":"<POSTBACK_PAYLOAD>",
                  # "image_url":"http://example.com/img/red.png"
                },{
                  "content_type":"text",
                  "title":"Chord",
                  "payload":"<POSTBACK_PAYLOAD>",
                  # "image_url":"http://example.com/img/green.png"
                },{
                  "content_type":"text",
                  "title":"Notes from Chord",
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
    text = "Greetings! You can ask me about music theory or history, I would be happy to help!"
    fb_message(fb_id, text)
    quick_reply(fb_id)
    
def handle_gibberish(response, fb_id):
    """
    Handle whatever random gibberish user sends
    """
    text = f"Sorry! We did not quite understand \"{response['text']}\" :("
    text_1 = "Try asking me about music theory or history!"
    fb_message(fb_id, text)
    fb_message(fb_id, text_1)

def handle_message(response, fb_id):
    """
    Customizes our response to the message and sends it
    """
    # Checks if user's message is a greeting
    # Otherwise we will just repeat what they sent us
    greetings = first_trait_value(response['traits'], 'wit$greetings')
    thanks = first_trait_value(response['traits'], 'wit$thanks')
    bye = first_trait_value(response['traits'], 'wit$bye')

    if greetings:
        handle_start(fb_id)
        return
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
            # * Identify the 2 notes user sent. Input to library function and return identified interval as response back to user
            notes = response['entities']["Note:Note"]
            note1 = notes[0]['value']
            note2 = notes[1]['value']
            print(f"Note 1 is {note1} and Note 2 is {note2}")
            try:
                interval = intervals.determine(note1, note2)
                text = f"The interval between {note1} and {note2} is {interval}."
            except Exception as e:
                print("EXCEPTION", e)
                text = f"Sorry! I don't know the interval between {note1} and {note2} :/"
        elif intent == 'getChords':
            # ? AND/OR: Identify the notes user sent. Input to library function and return identified chord as response back to user
            # ? When user requests 7th chord, check if trait "7th" is present
            # ? When user requests inversions, check if trait "inversion" and get it's value, then use inversion function on chord
            # * Identify the chord user sent. Input to libary function and return chord's notes as response back to user
            try:
                kq_entity = response['entities']["Key_Quality:Key_Quality"][0]
            except KeyError:
                text = "Sorry! I couldn't identify the chord name :/"
                fb_message(fb_id, text)
                return

            key_quality = kq_entity['value']
            key_quality = key_quality.lower()
            key_quality = key_quality.capitalize()
            note = kq_entity['entities'][0]['value']

            # If user joins key with quality
            if not note: 
                text = "Sorry! I'm not sure what the key is :/"
                fb_message(fb_id, text)
                return
            
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
                text = f"Sorry! I can't identify a {key_quality} chord :/"    
        elif intent == 'getSongsFromProgression':
            # * Get songs from chord progression
            prog = '4,1'
            res = requests.get("https://api.hooktheory.com/v1/" + f"trends/songs?cp={prog}",
                            headers={'Authorization': 'Bearer 06e6698541901e71cece0b359c6077b3'},
                            )
            result = res.json()
            text = ""
            
            for song in result:
                item = f"{song['song']} ({song['section']}) by {song['artist']}\n"
                text += item
            print(text)
        else:
            text = "NO INTENT"

    # Send response back to user
    fb_message(fb_id, text)


# Setup Wit Client
client = Wit(access_token=WIT_TOKEN)

if __name__ == '__main__':
    # Run Server
    app.run()                                   # Need gunicorn !!!        
    # app.run(host='0.0.0.0', port=8080)        WORKS
    # app.run(host='0.0.0.0', port=argv[1])     Procfile how?
