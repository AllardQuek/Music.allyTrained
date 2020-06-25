"""
Experiment with requests and responses from Wit App.

"""

#contents = url.get("https://api.wit.ai/message?v=20200622&q=what is c major")

# https://stackoverflow.com/questions/45868120/python-post-request-with-bearer-token?rq=1
import requests
import os, sys
import subprocess


print ("Searching for:")
text = input()

#question="Enter grade for course" + str(i)
#grade=input(question) *not sure how to get the inputs on the same line as string 'searching for:'

response = requests.get(f"https://api.wit.ai/message?v=20200622&q={text}", headers={'Authorization': 'Bearer 4NQZLEUIKILQHV6PS7YPA3F5GXQ7GYLC'})
response = response.json()
print(response)

print("Chatbot Restarted. Ask another question:")
#os.execl("C:\Users\verly\Desktop\trialhttpget.py",  [""])
#os.execl(sys.executable, sys.executable, * sys.argv)
subprocess.call(sys.argv[0], shell=True)
