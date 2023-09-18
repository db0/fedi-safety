import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-i', '--insecure', action="store_true", help="If set, will use http instead of https (useful for testing)")
arg_parser.add_argument('-v', '--verbosity', action='count', default=0, help="The default logging level is ERROR or higher. This value increases the amount of logging seen in your screen")
arg_parser.add_argument('-q', '--quiet', action='count', default=0, help="The default logging level is ERROR or higher. This value decreases the amount of logging seen in your screen")
arg_parser.add_argument('-p', '--port', action='store', default=14051, required=False, type=int, help="Provide a different port to start with")
arg_parser.add_argument('--color', default=False, action="store_true", help="Enabled colorized logs")
args = arg_parser.parse_args()
