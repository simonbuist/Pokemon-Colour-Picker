import re
from PIL import Image
import requests
from io import BytesIO

def get_image(number, game, shiny, gender = "f", form = ""):
    # generate bulbapedia page for the file
    url = get_url(number, game, shiny, gender.lower(), get_form(form))
    # make request
    response = requests.get(url)
    # check if request worked
    if response.status_code < 200 or response.status_code > 299:
        print(url)
        return 0

    # get specific file url from bulbapedia html page
    image_url = get_image_url(response.text)
    # check if request worked
    response = requests.get(image_url)
    if response.status_code < 200 or response.status_code > 299: 
        print(image_url)
        return 1

    # open image response
    img = Image.open(BytesIO(response.content))

    return img


# map game name to generation code
def get_gen(game):
    gen_dict = {
        "red":"1b", "blue":"1b", "yellow":"1y",
        "gold":"2g", "silver":"2s", "crystal":"2c",
        "ruby":"3r", "sapphire":"3r", "emerald":"3e", "firered":"3f", "leafgreen":"3f",
        "diamond":"4d", "pearl":"4d", "platinum":"4p", "heartgold":"4h", "soulsilver":"4h",
        "black":"5b", "white":"5b", "black2":"5b", "white2":"5b",
        "x":"6x", "y":"6x", "omegaruby":"6x", "alphasapphire":"6x",
        "sun":"7s", "moon":"7s", "ultrasun":"7u", "ultramoon":"7u", "letsgopikachu":"7p", "letsgoeevee":"7p",
        "sword":"8s", "shield":"8s"
    }

    # remove all non-alphanumeric chracters and make lowercase, match to dict entry
    return gen_dict[re.sub(r'[^a-zA-Z0-9]', '', game).lower()]


# match form name to form code
def get_form(form):
    form_dict = {
        "galarian":"G", "alolan":"A", "":""
    }

    return form_dict[form.lower()]


# create bulbapedia url
def get_url(num, gen, shiny, gender, form):
    num_str = str(num)
    
    # ensure pokemon number has enough 0's ahead of it
    while len(num_str) < 3:
        num_str = "0" + num_str

    # if it's a regional form, add the code
    if form != "":
        num_str = num_str + form

    # if shiny, add shiny tag
    if shiny:
        num_str = num_str + "_s"

    # create the whole url
    url = "https://bulbapedia.bulbagarden.net/wiki/File:Spr_" + get_gen(gen) + "_" + num_str +".png"

    # try requesting the image
    response = requests.head(url)

    # if the request failed, it's a pokemon with gender variants
    if response.status_code < 200 or response.status_code > 299:

        # reset the number string
        num_str = str(num)
        while len(num_str) < 3:
            num_str = "0" + num_str

        # add f or m for gender
        if shiny:
            num_str = num_str + "_" + gender + "_s"
        else:
            num_str = num_str + "_" + gender

        # recreate the url
        url = "https://bulbapedia.bulbagarden.net/wiki/File:Spr_" + get_gen(gen) + "_" + num_str +".png"
    return url


# cut through the html string to find the image url
def get_image_url(text: str):
    # i know this isn't the most elegant way to do it, but if it's stupid and it works it's not stupid
    out = text[text.find("<meta property=\"og:image\" content") : text.find("<meta property=\"og:image\" content") + 200]
    out = out[out.find("https://") : out.find(".png") + 4]
    return out
