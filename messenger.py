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
    Customizes our first response to the message and sends it
    """
    # Checks if user's message is a greeting
    # Otherwise we will just repeat what they sent us
    greetings = first_trait_value(response['traits'], 'wit$greetings')
    thanks = first_trait_value(response['traits'], 'wit$thanks')
    bye = first_trait_value(response['traits'], 'wit$bye')
    
    if greetings:
        handle_start(fb_id)
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
        elif intent == 'GetInterval':
            # TODO: Identify the 2 notes user sent. Input to library function and return identified interval as response back to user.
            text = "GETTING INTERVAL..."
            fb_message(fb_id, text)
        elif intent == 'getChords':
            # TODO: Identify the notes user sent. Input to library function and return identified chord as response back to user.
            # TODO: AND/OR Identify the chord user sent. Input to libary function and return chord's notes as response back to user.
            text = "GETTING CHORDS..."
            fb_message(fb_id, text)
            pass
        else:
            text = "Sorry, we couldn't quite understand. Please rephrase your question?"

            
def handle_intents(response, fb_id):
    """
    Scripted replies based on user intent
    
    
    composer=
    majorKey=
    minorKey = first_trait_value(response['traits'], 'wit$bye')
    chords = 
    """
    
    intent = response['intents'][0]['name']
    entity = response['entities'][0]['name'] """check!!"""
    role = response['entities'][0]['role']
    if intent == 'getComposer' and entity == 'Baroque_Composer':
        text = "\"{response['text']}\" was a composer from the Baroque era, marked by little variations in tempo and 4/4 timings. Read more here: https://en.wikipedia.org/wiki/List_of_Baroque_composers"
    elif intent == 'getComposer' and entity == 'Romantic_Composer':
        text = "\"{response['text']}\" was a composer from the Romantic era. Read more here: https://en.wikipedia.org/wiki/List_of_Romantic-era_composers"
    
    elif intent == 'getChords' and entity == 'Key_C_major':
        text = "This is C major, comprised of the notes C E and G."
    

# Setup Wit Client
client = Wit(access_token=WIT_TOKEN)

if __name__ == '__main__':
    # Run Server
    app.run()                                   # Need gunicorn !!!        
    # app.run(host='0.0.0.0', port=8080)        WORKS
    # app.run(host='0.0.0.0', port=argv[1])     Procfile how?
