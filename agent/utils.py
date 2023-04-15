import json
import os
import re

import requests
from dotenv import load_dotenv
load_dotenv()


def is_follow_up(value: str) -> bool:
    value = {}
    try:
        value: json.loads(value)
    except:
        result = re.search(r"{(.*)}", string)

        if result:
            extracted_value = result.group(1)
            result = json.loads(extracted_value)
            return False

    return value.get("is_a_follow_up_answer") == "True"


def is_air_quality_in(text: str) -> bool:
    pattern = r"\bair\s*quality\b"
    match = re.search(pattern, text)
    if match:
        return True
    else:
        return False


def json_loader(value):
    value = json.loads(value)
    return value


def white_space_remover(value: str) -> str:
    return value.replace('\n', '')


async def get_polutant(lat, lon):
    secrate_key = os.environ.get('SECRET_KEY')
    url = 'https://api.breezometer.com/air-quality/v2/current-conditions?lat=%s&lon=%s&key=%s&features=pollutants_concentrations,breezometer_aqi,pollutants_aqi_information,local_aqi' % (
        lat, lon, secrate_key)
    response = requests.get(url)
    response_json = response.json()
    return response_json


def conversation_context_builder(context):
    value = """"""

    for conversation in context:
        value = value + "\n" + \
            conversation['role'] + ': ' + conversation["content"] + "\n"
    return value
