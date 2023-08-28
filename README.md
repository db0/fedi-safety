# lemmy-safety
A script that goes through a lemmy pict-rs object storage and tries to prevent illegal or unethical content


# Requirements

This script uses your GPU to clip interrogate images and then use the results to determine if the image is a possible CSAM.

This means you need a GPU and the more powerful your GPU, the faster you can process your images.

# Use

* Install python>=3.10
* install requirements: `python -m pip install -r requirements.txt`
* Copy `env_example` to `.env`, then edit `.env` and add your Object Storage credentials and connection info
* Start the script

The script will record all image checked in an sqlite db called `lemmy_safety.db` which will prevent it from checking the same image twice.

The script has two methods: `all` and `daemon`

## All

Running with the cli arg `--all` will loop through all the images in your object storage and check each of them for CSAM. 

Any potential image will be automatically deleted and its ID recorded in the DB for potential follow-up.

## Daemon

Running without the `-all` arg will make the script run constantly and check all images uploaded in the past 20 minutes (can be changed using `--minutes`).

Any potential image will be automatically deleted and its ID recorded in the DB for potential follow-up.
