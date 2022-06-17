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
ap.add_argument("-c", "--count", required=False, type=int, default=100,
                help="(optional, default is 100) number of images to download")
ap.add_argument("-o", "--output", required=False, default="downloaded_images",
                help="(optional, default is 'download_images') name of output dir")
ap.add_argument("-l", "--language", required=True, type=str, default="eng",
                help="language for text recognition")
ap.add_argument("-w", "--wanted_texts", required=False, help="wanted text, text can be separated with commas (,)")
ap.add_argument("-u", "--unwanted_texts", required=False, help="wanted text, text can be separated with commas (,)")
ap.add_argument("-t", "--thread", required=False, type=int, default=2,
                help="(optional, default is 2) thread amount")
args = vars(ap.parse_args())

queue = queue.Queue()

path = ""
images_list = []


def download_images():
    global path, images_list
    force_replace = False

    try:
        print("Downloading started..")
        downloader.download(args["query"], args["count"], args["output"], adult_filter_off=True,
                            force_replace=force_replace, timeout=15, verbose=True)

        path = args["output"] + "/" + args["query"]
        images_list = os.listdir(path)
        print("[INFO] Downloading images is finished")

    except OSError as error:
        print("[ERROR] Downloading error: " + str(error))


def extract_wanted_images(q):
    global images_list, path
    wanted_images_path = path + "/wanted"
    wanted_texts = args["wanted_texts"].split(",")
    unwanted_texts = args["unwanted_texts"].split(",")

    if not os.path.exists(wanted_images_path):
        try:
            os.mkdir(wanted_images_path)
            print(wanted_images_path + " is created")
        except OSError as error:
            print("[ERROR] Directory creation error: " + str(error))

    while not q.empty():
        image = q.get()
        image_path = path + "/" + image
        if image_path.lower().endswith(".png") or \
                image_path.lower().endswith(".jpg") or \
                image_path.lower().endswith(".jpeg"):
            img_raw = cv2.imread(image_path)
            img_raw = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
            img = cv2.bilateralFilter(img_raw, 9, 75, 75)
            text = pytesseract.image_to_string(img, lang=args["language"]).lower()
            wanted_counter = 0
            unwanted_counter = 0
            for wanted in wanted_texts:
                if wanted in text:
                    wanted_counter += 1

            for unwanted in unwanted_texts:
                if unwanted in text:
                    unwanted_counter += 1

            verify_wanted = True if wanted_counter == len(wanted_texts) else False
            verify_unwanted = True if unwanted_counter == 0 else False

            if verify_wanted and verify_unwanted:
                try:
                    wanted_image_path = wanted_images_path + "/" + image
                    Path(image_path).rename(wanted_image_path)
                    print(f"{image} is moved to wanted directory")
                except OSError as error:
                    print("[ERROR] Image moving error: " + str(error))

            else:
                try:
                    os.remove(image_path)
                    print(image + " is deleted")
                except OSError as error:
                    print("[ERROR] Image deleting error: " + str(error))

        elif image_path.lower().endswith(".gif"):
            try:
                os.remove(image_path)
                print(image + " is deleted")
            except OSError as error:
                print("[ERROR] Image deleting error: " + str(error))

        q.task_done()

    print("[INFO] Moving images is finished")


download_images()

for i in images_list:
    queue.put(i)

for i in range(args["thread"]):
    worker = threading.Thread(target=extract_wanted_images, args=(queue,), daemon=True)
    worker.start()

queue.join()
