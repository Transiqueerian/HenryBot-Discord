import os
from dotenv import load_dotenv
import pyimgur

load_dotenv()
CLIENT_ID = os.getenv('IMGUR_API_ID')
#client_secret = os.getenv('IMGUR_API_SECRET')

client = pyimgur.Imgur(CLIENT_ID)

#class Client:
#    def __init__(self, client):
#        self.client = pyimgur.Imgur(CLIENT_ID)

def upload_url(link, name=None):
    if not name:
        name = "noname"
    uploaded_image = client.upload_image(url=link, title=name)
    print(uploaded_image.title)
    print(uploaded_image.link)
    print(uploaded_image.size)
    print(uploaded_image.type)
    return uploaded_image.link

def upload_file(PATH, name=None):
    if not name:
        name = "noname"
    uploaded_image = client.upload_image(path=PATH, title=name)
    print(uploaded_image.title)
    print(uploaded_image.size)
    print(uploaded_image.type)
    return uploaded_image.link

#link = upload_url('https://online-go.com/api/v1/games/43068987/png/43068987.png', '43068987')

#print(link)

