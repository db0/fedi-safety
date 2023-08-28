# lemmy-safety
This is a tool for Lemmy Administrators to easily check and clean all images in the pict-rs object storage for illegal or unethical content

Note, this script **does not save any images locally**. All images are stored in only, checked and then forgotten.

Due to the way lemmy and pict-rs works, we instance admins do not have sufficient means to check for CSAM, which puts them in big risks as image thumbnails from foreign instances are cached by default to their own object storage. 

There's two big potential problems:

1. Malicious users can simply open a new post, upload an image and cancel the new post, and that image will then be invisibly hosted by their instance among thousands of others with a URL known only by the malicious user. That user could then contact their  provider anonymously forwarding that URL, and try to take their lemmy instance down
2. Users on different instances with looser controls can upload CSAM posts and if those instances subscribed by any user in your own instance those image thumbnails will be cached to your own instance. Even if the relevant CSAM post is deleted, such images will persists in your object storage.

The lemmy safety will go directly through your object storage and scan each image for potential CSAM and automatically delete it. Covering both those problems in one go. You can also run this script constantly, to ensure no new such images can survive.

The results will also be written in an sqlite DB, which can then be used to follow-up and discover the user and instances uploading them.

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

The daemon will then endlessly repeat this process after a 30 seconds wait.

# False positives and False negatives

The scirpt has the potential to detect wrongly of course as the clip model is not perfect.
However the library used for checking for CSAM has been [robustly checked through the AI Horde](https://dbzer0.com/blog/ai-powered-anti-csam-filter-for-stable-diffusion/)

If you are concerned about deleting too many, or not deleting enough, or want to follow-up first before taking action, you can use the `--dry_run`
cli arg to mark the found csam but avoid deleting them.

