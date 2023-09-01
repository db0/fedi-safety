import os
import datetime
import sys
from PIL import Image
from io import BytesIO
import stat
from pathlib import Path
from loguru import logger
import pytz

local_base_directory = os.getenv("PICTRS_FILES_DIRECTORY")
if local_base_directory is None:
    logger.error("You need to provide an PICTRS_FILES_DIRECTORY var in your .env file")
    sys.exit(1)

def get_all_images(min_date=None):
    filelist = []
    def list_files_recursively(local_directory):
        for root, _, files in os.walk(local_directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                modify_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path), tz=datetime.timezone.utc)

                if min_date is None or modify_time >= min_date:
                    relative_path = Path(file_path).relative_to(local_base_directory)
                    filelist.append(
                        {
                            "key": str(relative_path),
                            "filepath": Path(file_path),
                            "mtime": modify_time,
                        }
                    )

    list_files_recursively(local_base_directory)
    return filelist

def load_image(local_path):
    with open(local_path, "rb") as local_file:
        image_bytes = local_file.read()
    image_pil = Image.open(BytesIO(image_bytes))
    return image_pil


def delete_image(local_path):
    try:
        os.remove(local_path)
        print(f"Deleted file: {local_path}")
    except FileNotFoundError:
        print(f"File not found: {local_path}")
    except Exception as e:
        print(f"Error deleting file {local_path}: {e}")