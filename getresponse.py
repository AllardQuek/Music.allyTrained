# https://stackoverflow.com/questions/45868120/python-post-request-with-bearer-token?rq=1
import requests

text = "<PUT YOUR TEST TEXT HERE>"

response = requests.get(f"https://api.wit.ai/message?v=20200622&q={text}", headers={'Authorization': 'Bearer 4NQZLEUIKILQHV6PS7YPA3F5GXQ7GYLC'})
response = response.json()
print(response)