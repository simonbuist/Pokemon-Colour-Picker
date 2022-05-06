from random import randint
from PIL import Image, ImageFont, ImageDraw
from operator import itemgetter
from get_image import get_image

def add_margin(pil_img, color):
    width, height = pil_img.size
    width_add = round(width * 0.25)
    height_add = round(height * 0.25)
    new_width = width + width_add * 2
    new_height = height + height_add * 2
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (width_add, height_add))
    return result


def label(img, colour):
    print(img.size)

    result = Image.new(img.mode, (img.size[0], round(img.size[1] * 1.2)), (255, 255, 255))
    result.paste(img, (0, 0))

    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype("arial.ttf", 32)
    draw.text((img.size[0] / 8, img.size[1] * 1.1 - 16), colour, (0, 0, 0), font=font)

    return result

def prepare_image(img):
    print(img.size)
    img = img.crop(img.getbbox())
    # img = img.crop(img.getbbox()).resize((img.size[0] * 4, img.size[1] * 4)).filter(ImageFilter.BoxBlur(1))
    img = img.resize((256, 256))
    # img = img.convert('RGB').filter(ImageFilter.BoxBlur(1))
    img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
    return img.convert('RGB')

def choose_colour(img):
    sensitivity = 0.5

    colour_list = img.getcolors()

    # remove background (0,0,0 or 255, 255, 255) from colour_list
    bg_colour = img.getpixel((0, 0))
    print(bg_colour)    
    colour_list = list(filter(lambda tup: tup[1] != bg_colour, colour_list))
    # colour_list = list(filter(lambda tup: tup[1] != (0, 0, 0) and tup[1] != (255, 255, 255), colour_list))

    # increase the coverage score of colours with large differences in RGB channels
    colour_list = [(tup[0] * ((1 - sensitivity/2) + max(
        abs(tup[1][0]-tup[1][1]),
        abs(tup[1][1]-tup[1][2]),
        abs(tup[1][2]-tup[1][0])
        ) * sensitivity / 255), tup[1]) for tup in colour_list]

    # print(colour_list)

    colour_list.sort(key=itemgetter(0), reverse=True)
    top_five = colour_list[:4]

    # add scores of very similar colours to the top 5
    for i in range(0, 4):
        colour = top_five[i]
        print("Colour: " + str(colour))
        similar_list = list(filter(lambda tup: abs(colour[1][0] - tup[1][0]) + abs(colour[1][1] - tup[1][1]) + abs(colour[1][2] - tup[1][2]) < 30 and colour != tup, colour_list))
        print("Similar: " + str(similar_list))
        # print("Prev Score: " + str(colour[0]))
        top_five[i] = (colour[0] + sum(similar[0] for similar in similar_list), colour[1])
        # print(" New Score: " + str(top_five[i][0]))
        # print("\n\n")

    top_five.sort(key=itemgetter(0), reverse=True)
    

    # colour_list_sorted = sorted(colour_list, key=lambda tup: tup[0])
    # print(colour_list)
    return top_five[0][1]


# img = get_image(20, "sun", True, "f", "alolan")
def generate_image(num, gen, shiny=False, gender="f", form=""):
    img = get_image(num, gen, shiny, gender, form)

    if img == 0:
        print("failed\n")
    else:
        # img.show()
        img = prepare_image(img)
        # img.show()

        # colour_list = img.getcolors()
        
        # colour_list = reduce_colours(colour_list)
        # main_colour = colour_list[0][1]

        main_colour = choose_colour(img)
        print("#" + str(num))
        print(main_colour)

        border_img = add_margin(img, main_colour)

        main_colour_name = name_colour(main_colour)

        img_final = label(border_img, main_colour_name)
        img_final.show()
        # for color in colour_list:
        #     print(color)

    print("done!\n\n")

    
def tuple_diff(tup1, tup2):
    return abs(tup1[0] - tup2[0]) + abs(tup1[1] - tup2[1]) + abs(tup1[2] - tup2[2])


def name_colour(value):
    colour_dict = {
        "red":(255, 0, 0), "orange":(255, 127, 0), "yellow":(255, 255, 0),
        "green":(0, 255, 0), "blue":(0, 0, 255), "purple":(125, 0, 255),
        "pink":(255, 0, 255), "brown":(165, 42, 42), "white":(255, 255, 255)
    }

    equalized_dict = {
        "red":(255, 74, 57), "orange":(255, 127, 0), "yellow":(155, 138, 0),
        "green":(0, 220, 0), "blue":(110, 110, 255), "purple":(195, 69, 255),
        "pink":(255, 35, 255), "brown":(100, 70, 36), "white":(255, 255, 255)
    }

    match_dict = {}

    for colour in equalized_dict.keys():
        match_dict[colour] = tuple_diff(value, equalized_dict[colour])

    match_list = list(sorted(match_dict.keys(), key=lambda val: match_dict[val]))

    print(match_list[0])

    return match_list[0]

    


# good tests 227, 643, 69, 758, 553, 500, 329, 339, 348
for i in range(50):
    generate_image(randint(1, 600), "sun", False)
# for i in range(300, 350):
#     generate_image(i, "shield", False, "")