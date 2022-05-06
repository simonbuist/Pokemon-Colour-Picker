from random import randint
from PIL import Image, ImageFont, ImageDraw
from operator import itemgetter
from get_image import get_image


# get the image ready for processing
def prepare_image(img):
    # crop out as much background as possible
    img = img.crop(img.getbbox())
    # stretch it out to 256x256 - distorts a lot of them, but that doesn't change function
    img = img.resize((256, 256))
    # convert PNG to PNG with only 256 colours (necessary for extracting colours)
    img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
    # convert to RGB image (like a JPG)
    return img.convert('RGB')


# the actually cool part of the program
def choose_colour(img):
    # affects how much saturated colours are prioritized (even if there's a slight larger
    # grey area, the results "feel" better if colours are prioritized)
    rgb_difference_boost = 0.5

    # tolerance for including slightly different colours into score of a colour
    hue_tolerance = 30

    # get all the colours in the image, and how many pixels of each
    colour_list = img.getcolors()

    # find the background colour from pixel (0, 0)
    bg_colour = img.getpixel((0, 0))
    # remove that background colour from the list of colours
    colour_list = list(filter(lambda tup: tup[1] != bg_colour, colour_list))
    
    # increase the coverage score of colours with large differences in RGB channels
    # basically check the differences between RGB levels, and increase or decrease
    # score based on how different (multiply by 1 +- 1/2 boost)
    colour_list = [(tup[0] * ((1 - rgb_difference_boost/2) + max(
        abs(tup[1][0]-tup[1][1]),
        abs(tup[1][1]-tup[1][2]),
        abs(tup[1][2]-tup[1][0])
        ) * rgb_difference_boost / 255), tup[1]) for tup in colour_list]

    # find the 5 most prominent colours
    colour_list.sort(key=itemgetter(0), reverse=True)
    top_five = colour_list[:4]

    # add scores of very similar colours to the top 5
    for i in range(0, 4):
        colour = top_five[i]
        # list all colours with cumulative differences in RBG channels less thatn the hue tolerance
        similar_list = list(filter(
            lambda tup: abs(colour[1][0] - tup[1][0]) 
            + abs(colour[1][1] - tup[1][1]) 
            + abs(colour[1][2] - tup[1][2]) < hue_tolerance 
            and colour != tup, colour_list
            ))
        # add the scores of similar colours
        top_five[i] = (colour[0] + sum(similar[0] for similar in similar_list), colour[1])

    # sort them again with the new scores
    top_five.sort(key=itemgetter(0), reverse=True)
    
    # return the highest scoring colour
    return top_five[0][1]


# adds a margin to the image in the new colour
def add_margin(img, color):
    # get new size
    width, height = img.size
    width_add = round(width * 0.25)
    height_add = round(height * 0.25)
    new_width = width + width_add * 2
    new_height = height + height_add * 2
    # create a new image with the right size and slap the old image in the middle
    result = Image.new(img.mode, (new_width, new_height), color)
    result.paste(img, (width_add, height_add))
    return result


# simple function to find the total difference between 2 RGB values
def tuple_diff(tup1, tup2):
    return abs(tup1[0] - tup2[0]) + abs(tup1[1] - tup2[1]) + abs(tup1[2] - tup2[2])


# finds the nearest colour name to the RGB value
def name_colour(value):
    # colour_dict = {
    #     "red":(255, 0, 0), "orange":(255, 127, 0), "yellow":(255, 255, 0),
    #     "green":(0, 255, 0), "blue":(0, 0, 255), "purple":(125, 0, 255),
    #     "pink":(255, 0, 255), "brown":(165, 42, 42), "white":(255, 255, 255)
    # }

    # dictionary of colour values - arrived on most of them by lowering the contrast
    # on a rainbow gradient until the greyscale value was the same
    equalized_dict = {
        "red":(255, 74, 57), "orange":(255, 127, 0), "yellow":(155, 138, 0),
        "green":(0, 220, 0), "blue":(110, 110, 255), "purple":(195, 69, 255),
        "pink":(255, 35, 255), "brown":(100, 70, 36), "white":(255, 255, 255)
    }

    # empty dict of matching scores
    match_dict = {}

    # see how close each named colour is to the RGB value
    for colour in equalized_dict.keys():
        match_dict[colour] = tuple_diff(value, equalized_dict[colour])

    # sort by closeness and return closest
    match_list = list(sorted(match_dict.keys(), key=lambda val: match_dict[val]))
    return match_list[0]


# adds a label with the colour name to the image - it looks a bit silly but I think that's charming
def label(img, colour):

    # create a new image with some white space at the bottom and copy old image in
    result = Image.new(img.mode, (img.size[0], round(img.size[1] * 1.2)), (255, 255, 255))
    result.paste(img, (0, 0))

    # add text
    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype("arial.ttf", 32)
    draw.text((img.size[0] / 8, img.size[1] * 1.1 - 16), colour, (0, 0, 0), font=font)

    return result



#main function for now
def generate_image(num, gen, shiny=False, gender="f", form=""):

    # function to get the image from bulbapedia
    img = get_image(num, gen, shiny, gender, form)

    # error checks
    if img == 0 or img == 1:
        print("failed\n")
    else:
        # adjusts the image - see 1st function
        img = prepare_image(img)

        # chooses the main colour - see 2nd function
        main_colour = choose_colour(img)

        # adds a margin of the main colour - see 3rd function
        border_img = add_margin(img, main_colour)

        # gets a name for the colour - see 4th function
        # this is the bit that currently isn't good - update to come
        main_colour_name = name_colour(main_colour)

        # adds a label with the colour name - see 5th function
        img_final = label(border_img, main_colour_name)

        # shows the image
        img_final.show()

    print("done!\n\n")


# to run the program a bunch of times
# good tests 227, 643, 69, 758, 553, 500, 329, 339, 348
for i in range(100):
    generate_image(randint(1, 806), "ultrasun", False)
# for i in range(300, 350):
#     generate_image(i, "shield", False, "")