import argparse
import os
from pathlib import Path

import cv2
import pytesseract
from bing_image_downloader import downloader

ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True, help="string to be searched")
ap.add_argument("-l", "--limit", required=False, type=int, default=100,
                help="(optional, default is 100) number of images to download")
ap.add_argument("-o", "--output", required=False, type=str, default="downloaded_images",
                help="(optional, default is 'downloaded_images') name of output dir")
ap.add_argument("-m", "--must_required_text", required=True, help="must required text on images")
ap.add_argument("-r", "--required_text", required=True, help="required text on images")
ap.add_argument("-u", "--unwanted-text", required=False, help="unwanted text on images")
args = vars(ap.parse_args())


def download_images():
    force_replace = False

    '''
    if os.path.isdir(args["output"]):
        force_replace_selection = input("Output dir already exists, do you want to delete contents in it? [y/n]: ")
        if force_replace_selection == "y":
            force_replace = True
        elif force_replace_selection == "n":
            force_replace = False
        else:
            force_replace = False
            print("Force replace is set false")
    '''

    try:
        print("Downloading started..")
        downloader.download(args["query"], args["limit"], args["output"], adult_filter_off=True,
                            force_replace=force_replace, timeout=15, verbose=True)

    except OSError as error:
        print("An exception occured: " + str(error))


def move_wanted_images():
    path = args["output"] + "/" + args["query"]
    wanted_images_path = path + "/" + "wanted"
    images_list = os.listdir(path)
    wanted_counter = 0

    if not os.path.exists(wanted_images_path):
        try:
            os.mkdir(wanted_images_path)
            print(wanted_images_path + " is created")
        except OSError as error:
            print("Error! " + str(error))

    for image in images_list:
        image_path = path + "/" + image
        if image_path.lower().endswith(".png") or \
                image_path.lower().endswith(".jpg") or \
                image_path.lower().endswith(".jpeg"):
            img_raw = cv2.imread(image_path)
            img = cv2.cvtColor(img_raw, cv2.COLOR_BGR2RGB)
            text = pytesseract.image_to_string(img).lower()
            if args["required_text"] in text and args["must_required_text"] in text and args["unwanted_text"] not in text:
                wanted_counter += 1
                try:
                    wanted_image_path = wanted_images_path + "/" + image
                    Path(image_path).rename(wanted_image_path)
                    print(f"{image} is moved to wanted directory")
                except OSError as error:
                    print("Error! " + str(error))

    print(f"Total {wanted_counter} images are moved to wanted directory")


download_images()
move_wanted_images()
