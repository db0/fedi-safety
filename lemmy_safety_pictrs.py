# This script is going to continuously pick up images that are attempted to be uploaded to pict-rs and check them for CSAM

import time
import logging
from concurrent.futures import ThreadPoolExecutor
import argparse

from loguru import logger

from fedi_safety import pictrs_safety

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', level=logging.WARNING)


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--threads', action="store", required=False, default=10, type=int, help="How many threads to use. The more threads, the more VRAM requirements, but the faster the processing.")
args = arg_parser.parse_args()
should_stop = False

def start_polling(executor):
    running_jobs = []
    logger.info("Starting main loop")
    while not should_stop:
        running_jobs.append(executor.submit(pictrs_safety.pop_and_check))
        time.sleep(0.1)

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        try:
            start_polling(executor)
            time.sleep(1)
        except:
            time.sleep(1)

