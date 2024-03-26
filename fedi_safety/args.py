import argparse

def get_argparser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--all', action="store_true", required=False, default=False, help="Check all images in the storage account")
    arg_parser.add_argument('-t', '--threads', action="store", required=False, default=10, type=int, help="How many threads to use. The more threads, the more VRAM requirements, but the faster the processing.")
    arg_parser.add_argument('-m', '--minutes', action="store", required=False, default=20, type=int, help="The images of the past how many minutes to check.")
    arg_parser.add_argument('--dry_run', action="store_true", required=False, default=False, help="Will check and reprt but will not delete")
    arg_parser.add_argument('--skip_unreadable', action="store_true", required=False, default=False, help="If True, unreadable images will be ignored instead of being marked as CSAM")
    arg_parser.add_argument('--rescan_skipped', action="store_true", required=False, default=False, help="If True, will rescan previously skipped files")
    return arg_parser