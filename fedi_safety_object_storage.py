# This script is going to clean up images stored in an AWS S3-compatible object storage

import time
import logging
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import PIL.Image
from PIL import UnidentifiedImageError

from loguru import logger
import sys

from fedi_safety import object_storage
from fedi_safety import database
from fedi_safety.check import check_image
from fedi_safety import args

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', level=logging.WARNING)

def check_and_delete_filename(key):
    is_csam = False
    try:
        image: PIL.Image.Image = object_storage.download_image(key)
        if not image:
            is_csam = None
        else:
            is_csam = check_image(image,args.flag_unreadable)
    except UnidentifiedImageError:
        logger.warning("Image could not be read. Returning it as CSAM to be sure.")
        is_csam = True
    if is_csam and not args.dry_run:
        object_storage.delete_image(key)
    return is_csam, key


def check_and_delete_object(obj):
    try:
        image: PIL.Image.Image = object_storage.download_image(obj.key)
        if not image:
            is_csam = None
        else:
            is_csam = check_image(image,args.flag_unreadable)
    except UnidentifiedImageError:
        logger.warning("Image could not be read. Returning it as CSAM to be sure.")
        is_csam = True
    if is_csam and not args.dry_run:
        obj.delete()
    return is_csam, obj

if __name__ == "__main__":
    if args.all:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = []
            for obj in object_storage.get_all_images():
                if not database.is_image_checked(obj.key):
                    futures.append(executor.submit(check_and_delete_object, obj))
                if len(futures) >= 1000:
                    for future in futures:
                        result, obj = future.result()
                        database.record_image(obj.key,csam=result)
                    logger.info(f"Safety Checked Images: {len(futures)}")
                    futures = []
            for future in futures:
                result, obj = future.result()
                database.record_image(obj.key,csam=result)
            logger.info(f"Safety Checked Images: {len(futures)}")    
        sys.exit()

    # This is only called if --all is not set
    while True:
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=args.minutes)
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = []
                for key in object_storage.get_all_images_after(cutoff_time):
                    if not database.is_image_checked(key):
                        futures.append(executor.submit(check_and_delete_filename, key))
                    if len(futures) >= 500:
                        for future in futures:
                            result, key = future.result()
                            database.record_image(key,csam=result)
                        logger.info(f"Safety Checked Images: {len(futures)}")
                        futures = []
                for future in futures:
                    result, key = future.result()
                    database.record_image(key,csam=result)
                logger.info(f"Safety Checked Images: {len(futures)}")    
            time.sleep(30)
        except:
            time.sleep(30)

