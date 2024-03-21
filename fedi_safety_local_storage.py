# This script is going to clean up images stored in the same system it's running on

import time
import logging
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import PIL.Image
from PIL import UnidentifiedImageError

from loguru import logger

from fedi_safety import local_storage
from fedi_safety import database
from fedi_safety.check import check_image
from fedi_safety.args import args

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', level=logging.WARNING)


def check_and_delete_filename(file_details):
    is_csam = False
    try:
        image: PIL.Image.Image = local_storage.load_image(str(file_details["filepath"]))
        if not image:
            is_csam = None
        else:
            is_csam = check_image(image,args.skip_unreadable)
    except UnidentifiedImageError:
        if args.skip_unreadable:
            logger.warning("Image could not be read. Skipping it.")
            is_csam = None
        else:
            logger.warning("Image could not be read. Returning it as CSAM to be sure.")
            is_csam = True
    if is_csam and not args.dry_run:
        local_storage.delete_image(str(file_details["filepath"]))
    return is_csam, file_details

def run_cleanup(cutoff_time = None):
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for file_details in local_storage.get_all_images(cutoff_time):
            if not database.is_image_checked(file_details["key"]):
                futures.append(executor.submit(check_and_delete_filename, file_details))
            if len(futures) >= 500:
                for future in futures:
                    result, fdetails = future.result()
                    if result is not None or not args.skip_unreadable:
                        database.record_image(fdetails["key"],csam=result)
                logger.info(f"Safety Checked Images: {len(futures)}")
                futures = []
        for future in futures:
            result, fdetails = future.result()
            if result is not None or not args.skip_unreadable:
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

