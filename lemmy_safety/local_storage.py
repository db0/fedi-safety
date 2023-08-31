import os
import datetime
import paramiko
import sys
from getpass import getpass
from PIL import Image
from io import BytesIO
import stat
from pathlib import Path
from loguru import logger
import pytz

hostname = os.getenv("SSH_HOSTNAME")
if hostname is None:
    logger.error("You need to provide an SSH_HOSTNAME var in your .env file")
    sys.exit(1)
port = os.getenv("SSH_PORT")
if hostname is None:
    logger.error("You need to provide an SSH_PORT var in your .env file")
    sys.exit(1)
port = int(port)
username = os.getenv("SSH_USERNAME")
if hostname is None:
    logger.error("You need to provide an SSH_USERNAME var in your .env file")
    sys.exit(1)
private_key_path = os.getenv("SSH_PRIVKEY")
if hostname is None:
    logger.error("You need to provide an SSH_PRIVKEY var in your .env file")
    sys.exit(1)
remote_base_directory = os.getenv("SSH_PICTRS_FILES_DIRECTORY")
if hostname is None:
    logger.error("You need to provide an SSH_PICTRS_FILES_DIRECTORY var in your .env file")
    sys.exit(1)

private_key_passphrase = getpass(prompt="Enter passphrase for private key: ")
private_key = paramiko.RSAKey(filename=private_key_path, password=private_key_passphrase)

def get_connection():
    # I can't re-use the same connection when using threading
    # So we have to initiate a new connection per thread
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp

def get_all_images(min_date=None):
    sftp = get_connection()
    filelist = []

    def list_files_recursively(remote_directory):
        files = sftp.listdir_attr(remote_directory)
        for file_info in files:
            file_path = os.path.join(remote_directory, file_info.filename)
            if stat.S_ISREG(file_info.st_mode):  # Check if it's a regular file
                modify_time = datetime.datetime.fromtimestamp(file_info.st_mtime, tz=pytz.UTC)
                if min_date is None or modify_time >= min_date:      
                    filelist.append(
                        {
                            "key": str(Path(file_path).relative_to(Path(remote_base_directory))),
                            "filepath": Path(file_path),
                            "mtime": modify_time,
                        }
                    )
            elif stat.S_ISDIR(file_info.st_mode):  # Check if it's a directory
                list_files_recursively(file_path)

    list_files_recursively(remote_base_directory)
    return filelist

def download_image(remote_path):
    sftp = get_connection()
    remote_file = sftp.open(remote_path, "rb")
    image_bytes = remote_file.read()
    remote_file.close()
    image_pil = Image.open(BytesIO(image_bytes))
    return image_pil


def delete_image(remote_path):
    sftp = get_connection()
    try:
        sftp.remove(remote_path)
    except FileNotFoundError:
        logger.error(f"File not found: {remote_path}")
    except Exception as e:
        logger.error(f"Error deleting file {remote_path}: {e}")
