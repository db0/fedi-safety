
from dotenv import load_dotenv
from loguru import logger
import PIL.Image

from horde_safety.csam_checker import check_for_csam
from horde_safety.interrogate import get_interrogator_no_blip    
from lemmy_safety import object_storage
from PIL import UnidentifiedImageError

interrogator = get_interrogator_no_blip()

def check_image(key):
    try:
        image: PIL.Image.Image = object_storage.download_image(key)
    except UnidentifiedImageError:
        logger.warning("Image could not be read. Returning it as CSAM to be sure.")
        return True
    if not image:
        return None
    try:
        is_csam, results, info = check_for_csam(
            interrogator=interrogator,
            image=image,
            prompt='',
            model_info={"nsfw": True, "tags": []},
        )
    except OSError:
        logger.warning("Image could not be read. Returning it as CSAM to be sure.")
        return True
    if is_csam:
        logger.warning(f"{key} rejected as CSAM")
    else:
        logger.info(f"{key} is OK")
    return is_csam
