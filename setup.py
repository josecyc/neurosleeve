import os
from termcolor import colored

DATA_FOLDERS = ["latest_spec", "latest_wav", "models", "osc_data", "osc_record", "stream_files"]
CURR_PATH = os.getcwd()

print("Creating data folders...")
for folder in DATA_FOLDERS:
    try:
        path = os.path.join(CURR_PATH, folder)
        os.mkdir(path)
    except OSError:
        print(colored("Failed to create: %-13s, check if already present" % folder, 'red'))
    else:
        print(colored("Created directory: %-13s" % folder), 'green')