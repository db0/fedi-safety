import os
import datetime
import sys
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
from loguru import logger
from fedi_safety.check import check_image

pictrs_safety_url = os.getenv("PICTRS_SAFETY_URL")
if pictrs_safety_url is None:
    logger.error("You need to provide an PICTRS_SAFETY_URL var in your .env file")
    sys.exit(1)
pictrs_safety_apikey = os.getenv("PICTRS_SAFETY_APIKEY")
if pictrs_safety_apikey is None:
    logger.error("You need to provide an PICTRS_SAFETY_APIKEY var in your .env file")
    sys.exit(1)
headers = {"apikey": pictrs_safety_apikey}

def pop_and_check():
    try:
        response = requests.get(f"{pictrs_safety_url}/api/v1/pop", headers=headers, timeout=2)
        if not response.ok:
            logger.error(response.json())
            return
        if response.status_code == 200:
            if "Content-Disposition" not in response.headers:
                logger.error("Filename not found in headers")
                return
            filename = response.headers["Content-Disposition"].split('=',1)[1]
            image_data = response.content
            image = Image.open(BytesIO(image_data))
        elif response.status_code == 204:
            logger.debug("nothing to do")
            return
        else:
            logger.error(f"Failed to retrieve the image. Status code: {response.status_code}")
            return
        is_csam = check_image(image)
        result_payload = {
            "image": filename,
            "is_csam": is_csam,
            "is_nsfw": is_csam,
        }
        if is_csam:
            logger.warning(f"Submitting {filename} as csam!")
        else:
            logger.info(f"Submitting {filename} as not csam")
        response = requests.post(f"{pictrs_safety_url}/api/v1/pop", headers=headers, json=result_payload)
    except Exception as err:
        logger.error(f"Exception: {err}")