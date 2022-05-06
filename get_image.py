import re
from PIL import Image
import requests
from io import BytesIO

def get_image(number, game, shiny, gender = "f", form = ""):
    url = get_url(number, game, shiny, gender.lower(), get_form(form))
    response = requests.get(url)
    if response.status_code < 200 or response.status_code > 299:
        print(url)
        return 0

    image_url = get_image_url(response.text)
    response = requests.get(image_url)
    if response.status_code < 200 or response.status_code > 299: 
        print(image_url)
        return 1

    img = Image.open(BytesIO(response.content))

    return img


def get_gen(game):
    gen_dict = {
        "red":"1b", "blue":"1b", "yellow":"1y",
        "gold":"2g", "silver":"2s", "crystal":"2c",
        "ruby":"3r", "sapphire":"3r", "emerald":"3e", "firered":"3f", "leafgreen":"3f",
        "diamond":"4d", "pearl":"4d", "platinum":"4p", "heartgold":"4h", "soulsilver":"4h",
        "black":"5b", "white":"5b", "black2":"5b", "white2":"5b",
        "x":"6x", "y":"6x", "omegaruby":"6x", "alphasapphire":"6x",
        "sun":"7s", "moon":"7s", "ultrasun":"7s", "ultramoon":"7s", "letsgopikachu":"7p", "letsgoeevee":"7p",
        "sword":"8s", "shield":"8s"
    }

    return gen_dict[re.sub(r'[^a-zA-Z0-9]', '', game).lower()]

def get_form(form):
    form_dict = {
        "galarian":"G", "alolan":"A", "":""
    }

    return form_dict[form.lower()]


def get_url(num, gen, shiny, gender, form):
    num_str = str(num)
    
    while len(num_str) < 3:
        num_str = "0" + num_str

    if form != "":
        num_str = num_str + form

    if shiny:
        num_str = num_str + "_s"

    url = "https://bulbapedia.bulbagarden.net/wiki/File:Spr_" + get_gen(gen) + "_" + num_str +".png"

    response = requests.head(url)
    if response.status_code < 200 or response.status_code > 299:
        print(url)
        num_str = str(num)
        while len(num_str) < 3:
            num_str = "0" + num_str

        if shiny:
            num_str = num_str + "_" + gender + "_s"
        else:
            num_str = num_str + "_" + gender

        url = "https://bulbapedia.bulbagarden.net/wiki/File:Spr_" + get_gen(gen) + "_" + num_str +".png"
    return url


def get_image_url(text: str):
    out = text[text.find("<meta property=\"og:image\" content") : text.find("<meta property=\"og:image\" content") + 200]
    out = out[out.find("https://") : out.find(".png") + 4]
    return out
