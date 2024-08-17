import requests
import io
import json
import time
import base64
# print("Введите ваш запрос:")
# req = input()
from random import randint as r
from random import choice as ch

import os
class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

class Photo:
    def __init__(self,api_key, secret_key):
        self.api_key = api_key
        self.secret_key=secret_key
    def getPhoto(self, description):
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', self.api_key, self.secret_key)
        
        model_id = api.get_model()
        uuid = api.generate(f"{description}", model_id)
        images = api.check_generation(uuid)
        
        # Decode the base64 image to binary data
        image_base64 = images[0]
        image_data = base64.b64decode(image_base64)

        # Use io.BytesIO to create an in-memory byte stream
        img_io = io.BytesIO()
        img_io.write(image_data)
        img_io.seek(0)  # Seek to the beginning of the BytesIO object

        return img_io
