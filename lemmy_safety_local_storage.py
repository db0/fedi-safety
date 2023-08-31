import time
import logging
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import argparse
import PIL.Image

from loguru import logger
import sys

from lemmy_safety.check import check_image
from lemmy_safety import local_storage
from lemmy_safety import database
from PIL import UnidentifiedImageError

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', level=logging.WARNING)


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--all', action="store_true", required=False, default=False, help="Check all images in the storage account")
arg_parser.add_argument('-t', '--threads', action="store", required=False, default=100, type=int, help="How many threads to use. The more threads, the more VRAM requirements, but the faster the processing.")
arg_parser.add_argument('-m', '--minutes', action="store", required=False, default=20, type=int, help="The images of the past how many minutes to check.")
arg_parser.add_argument('--dry_run', action="store_true", required=False, default=False, help="Will check and reprt but will not delete")
args = arg_parser.parse_args()


def check_and_delete_filename(file_details):
    try:
        image: PIL.Image.Image = local_storage.download_image(str(file_details["filepath"]))
    except UnidentifiedImageError:
        logger.warning("Image could not be read. Returning it as CSAM to be sure.")
        is_csam = True
    if not image:
        is_csam = None
    else:
        is_csam = check_image(image)
    if is_csam and not args.dry_run:
        local_storage.delete_image(str(file_details["filepath"]))
    return is_csam, file_details

def run_cleanup(cutoff_time = None):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for file_details in local_storage.get_all_images(cutoff_time):
            if not database.is_image_checked(file_details["key"]):
                futures.append(executor.submit(check_and_delete_filename, file_details))
            if len(futures) >= args.threads:
                for future in futures:
                    result, fdetails = future.result()
                    database.record_image(fdetails["key"],csam=result)
                logger.info(f"Safety Checked Images: {len(futures)}")
                futures = []
        for future in futures:
            result, fdetails = future.result()
            database.record_image(fdetails["key"],csam=result)
        logger.info(f"Safety Checked Images: {len(futures)}")    

if __name__ == "__main__":
    if args.all:
        run_cleanup()
    else:
        while True:
            try:
                cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=args.minutes)
                run_cleanup(cutoff_time)
                time.sleep(30)
            except:
                time.sleep(30)

