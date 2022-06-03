import argparse
import os
import queue
import threading
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

queue = queue.Queue()

path = ""
images_list = []


def download_images():
    global path, images_list
    force_replace = False

    try:
        print("Downloading started..")
        downloader.download(args["query"], args["limit"], args["output"], adult_filter_off=True,
                            force_replace=force_replace, timeout=15, verbose=True)

        path = args["output"] + "/" + args["query"]
        images_list = os.listdir(path)

    except OSError as error:
        print("An exception occured: " + str(error))


def move_wanted_images(q):
    global images_list, path
    wanted_images_path = path + "/" + "wanted"
    wanted_counter = 0

    if not os.path.exists(wanted_images_path):
        try:
            os.mkdir(wanted_images_path)
            print(wanted_images_path + " is created")
        except OSError as error:
            print("Error! " + str(error))

    while not q.empty():
        image = q.get()
        image_path = path + "/" + image
        if image_path.lower().endswith(".png") or \
                image_path.lower().endswith(".jpg") or \
                image_path.lower().endswith(".jpeg"):
            img_raw = cv2.imread(image_path)
            img_raw = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
            img = cv2.bilateralFilter(img_raw, 9, 75, 75)
            text = pytesseract.image_to_string(img).lower()
            if args["required_text"] in text and args["must_required_text"] in text and args["unwanted_text"] not in text:
                wanted_counter += 1
                try:
                    wanted_image_path = wanted_images_path + "/" + image
                    Path(image_path).rename(wanted_image_path)
                    print(f"{image} is moved to wanted directory")
                except OSError as error:
                    print("Error! " + str(error))

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
        q.task_done()

    print(f"Total {wanted_counter} images are moved to wanted directory")


download_images()

for i in images_list:
    queue.put(i)

for i in range(2):
    worker = threading.Thread(target=move_wanted_images, args=(queue,), daemon=True)
    worker.start()

queue.join()
