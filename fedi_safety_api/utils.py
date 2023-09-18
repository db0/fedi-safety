import uuid
import bleach
import secrets
import hashlib
import os
import random
import regex as re
import json
from datetime import datetime
import dateutil.relativedelta
from loguru import logger
from fedi_safety_api.flask import SQLITE_MODE

random.seed(random.SystemRandom().randint(0, 2**32 - 1))


def get_db_uuid():
    if SQLITE_MODE:
        return str(uuid.uuid4())
    else: 
        return uuid.uuid4()

def generate_client_id():
    return secrets.token_urlsafe(16)

def sanitize_string(text):
    santxt = bleach.clean(text).strip()
    return santxt

def hash_api_key(unhashed_api_key):
    salt = os.getenv("secret_key", "s0m3s3cr3t") # Note default here, just so it can run without env file
    hashed_key = hashlib.sha256(salt.encode() + unhashed_api_key.encode()).hexdigest()
    # logger.warning([os.getenv("secret_key", "s0m3s3cr3t"), hashed_key,unhashed_api_key])
    return hashed_key


def hash_dictionary(dictionary):
    # Convert the dictionary to a JSON string
    json_string = json.dumps(dictionary, sort_keys=True)
    # Create a hash object
    hash_object = hashlib.sha256(json_string.encode())
    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()
    return hash_hex

def get_expiry_date():
    return datetime.utcnow() + dateutil.relativedelta.relativedelta(minutes=+20)

def get_random_seed(start_point=0):
    '''Generated a random seed, using a random number unique per node'''
    return random.randint(start_point, 2**32 - 1)

def validate_regex(regex_string):
    try:
        re.compile(regex_string, re.IGNORECASE)
    except:
        return False
    return True
