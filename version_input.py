import os
from pathlib import Path

import cv2
import pytesseract
from bing_image_downloader import downloader


def download_images(query, limit, output):
    try:
        print("Downloading started..")
        downloader.download(query, limit, output, adult_filter_off=True,
                            force_replace=False, timeout=15, verbose=True)

    except OSError as error:
        print("Downloader error! " + str(error))


def move_wanted_images(query, output, required_text, must_required_text, unwanted_text):
    path = output + "/" + query
    wanted_images_path = path + "/" + "wanted"
    images_list = os.listdir(path)
    wanted_counter = 0

    if not os.path.exists(wanted_images_path):
        try:
            os.mkdir(wanted_images_path)
            print(wanted_images_path + " is created")
        except OSError as error:
            print("Creating directory error! " + str(error))

    for image in images_list:
        image_path = path + "/" + image
        if image_path.lower().endswith(".png") or \
                image_path.lower().endswith(".jpg") or \
                image_path.lower().endswith(".jpeg"):
            text = ""
            try:
                img_raw = cv2.imread(image_path)
                img_raw = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
                img = cv2.bilateralFilter(img_raw, 9, 75, 75)
                text = pytesseract.image_to_string(img).lower()
            except OSError as error:
                print("PyTesseract error! " + str(error))
            if required_text in text and must_required_text in text and unwanted_text not in text:
                wanted_counter += 1
                try:
                    wanted_image_path = wanted_images_path + "/" + image
                    Path(image_path).rename(wanted_image_path)
                    print(image + " is moved to wanted directory")
                except OSError as error:
                    print("Image moving error! " + str(error))

            else:
                try:
                    os.remove(image_path)
                    print(image + " is deleted")
                except OSError as error:
                    print("Image deleting error! " + str(error))
        elif image_path.lower().endswith(".gif"):
            try:
                os.remove(image_path)
                print(image + " is deleted")
            except OSError as error:
                print("Image deleting error! " + str(error))

    print(f"Total {wanted_counter} images are moved to wanted directory")


my_query = input("Query: ")
my_limit = int(input("Limit: "))
# my_output = input("Output: ")
my_output = "downloaded_images"

my_required_text = input("Required Text: ")
my_must_required_text = input("Required Text 2: ")
my_unwanted_text = input("Unwanted Text: ")

download_images(my_query, my_limit, my_output)
move_wanted_images(my_query, my_output, my_required_text, my_must_required_text, my_unwanted_text)
