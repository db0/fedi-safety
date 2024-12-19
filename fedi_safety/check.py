
from fedi_safety.config import Config
from loguru import logger

from horde_safety.csam_checker import check_for_csam
from horde_safety.interrogate import get_interrogator_no_blip
from horde_safety.deep_danbooru_model import get_deep_danbooru_model

interrogator = get_interrogator_no_blip()
deep_danbooru_model = None
nsfw_checker = None
if Config.use_new_safety:
    deep_danbooru_model = get_deep_danbooru_model()
    try:
        from horde_safety.nsfw_checker_class import NSFWChecker

        nsfw_checker = NSFWChecker(
            interrogator,
            deep_danbooru_model,  # Optional, significantly improves results for anime images
        )
    except Exception as e:
        logger.error(f"Failed to initialise NSFWChecker: {type(e).__name__} {e}")
        raise
def check_image(image, skip_unreadable=False):
    try:
        image.thumbnail((512, 512))
        if Config.use_new_safety is False:
            is_csam, _results, _info = check_for_csam(
                interrogator=interrogator,
                image=image,
                prompt='',
                model_info={"nsfw": True, "tags": []},
            )
        else:
            nsfw_result = nsfw_checker.check_for_nsfw(
                            image=image,
                            prompt='',
                            model_info={"nsfw": True, "tags": []},
            )
            is_csam = nsfw_result.is_csam
    except OSError:
        if skip_unreadable:
            logger.warning("Image could not be read. Skipping it.")
            return None
        logger.warning("Image could not be read. Returning it as CSAM to be sure.")
        return True
    return is_csam
