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
import contextlib
from fedi_safety.config import Config

hostname = Config.ssh_hostname
if hostname is None:
    logger.error("You need to provide an SSH_HOSTNAME var in your .env file")
    sys.exit(1)
port = Config.ssh_port
if hostname is None:
    logger.error("You need to provide an SSH_PORT var in your .env file")
    sys.exit(1)
username = Config.ssh_username
if hostname is None:
    logger.error("You need to provide an SSH_USERNAME var in your .env file")
    sys.exit(1)
private_key_path = Config.ssh_privkey
if hostname is None:
    logger.error("You need to provide an SSH_PRIVKEY var in your .env file")
    sys.exit(1)
remote_base_directory = Config.pictrs_files_directory
if remote_base_directory is None:
    logger.error("You need to provide an PICTRS_FILES_DIRECTORY var in your .env file")
    sys.exit(1)

private_key_passphrase = getpass(prompt="Enter passphrase for private key: ")
private_key = paramiko.RSAKey(filename=private_key_path, password=private_key_passphrase)

@contextlib.contextmanager
def get_connection():
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        yield sftp
    finally:
        sftp.close()
        transport.close()

def get_all_images(min_date=None):
    with get_connection() as sftp:
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
    with get_connection() as sftp:
        remote_file = sftp.open(remote_path, "rb")
        image_bytes = remote_file.read()
        remote_file.close()
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