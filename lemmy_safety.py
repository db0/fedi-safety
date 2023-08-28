import time
import logging
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import argparse

from loguru import logger
import sys

from lemmy_safety.check import check_image
from lemmy_safety.object_storage import get_all_images_after, get_all_images, delete_image
from lemmy_safety import database

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', level=logging.WARNING)


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--all', action="store_true", required=False, default=False, help="Check all images in the storage account")
arg_parser.add_argument('-t', '--threads', action="store", required=False, default=100, type=int, help="How many threads to use. The more threads, the more VRAM requirements, but the faster the processing.")
arg_parser.add_argument('-m', '--minutes', action="store", required=False, default=20, type=int, help="The images of the past how many minutes to check.")
arg_parser.add_argument('--dry_run', action="store_true", required=False, default=False, help="Will check and reprt but will not delete")
args = arg_parser.parse_args()


def check_and_delete_filename(key):
    is_csam = check_image(key)
    if is_csam and not args.dry_run:
        delete_image(key)
    return is_csam, key


def check_and_delete_object(obj):
    is_csam = check_image(obj.key)
    if is_csam and not args.dry_run:
        obj.delete()
    return is_csam, obj



if args.all:
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for obj in get_all_images():
            if not database.is_image_checked(obj.key):
                futures.append(executor.submit(check_and_delete_object, obj))
            if len(futures) >= args.threads:
                for future in futures:
                    result, obj = future.result()
                    database.record_image(obj.key,csam=result)
                logger.info(f"Safety Checked Images: {len(futures)}")
                futures = []
        for future in futures:
            future.result()
        logger.info(f"Safety Checked Images: {len(futures)}")    
    sys.exit()

# This is only called if --all is not set
while True:
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=args.minutes)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for key in get_all_images_after(cutoff_time):
                if not database.is_image_checked(key):
                    futures.append(executor.submit(check_and_delete_filename, key))
                if len(futures) >= args.threads:
                    for future in futures:
                        result, key = future.result()
                        database.record_image(key,csam=result)
                    logger.info(f"Safety Checked Images: {len(futures)}")
                    futures = []
            for future in futures:
                future.result()
            logger.info(f"Safety Checked Images: {len(futures)}")    
        time.sleep(30)
    except:
        time.sleep(30)

