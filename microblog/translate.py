import json, requests, uuid
import requests
from flask_babel import _
from microblog import app


def translate(text, source_language, dest_language):
   
    key = app.config['MS_TRANSLATOR_KEY']
    if key is None:
        return _('Error: the translation service is not configured!')

    endpoint = "https://api.cognitive.microsofttranslator.com"

   
   

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': f'{source_language}',
        'to': [f'{dest_language}']
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
       
        'Ocp-Apim-Subscription-Region': 'germanywestcentral',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

   
    body = [{
        'text': f'{text}'
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    if request.status_code != 200:
        return _('Error: The translation service failed!')
    response = request.json()
    return response[0]['translations'][0]['text']

   
