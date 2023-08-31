
from dotenv import load_dotenv
from loguru import logger

from horde_safety.csam_checker import check_for_csam
from horde_safety.interrogate import get_interrogator_no_blip    

interrogator = get_interrogator_no_blip()

def check_image(image):
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
    return is_csam
