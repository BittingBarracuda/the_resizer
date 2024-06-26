from resizer import delete_file, get_datetime
from datetime import datetime
import time
import os

MAX_TIME = 10 * 60
current_files = {}

def look_files_folder():
    global current_files
    print(f'[! CHECKER - {get_datetime(True)}] files_checker looking for old files...')
    files = list(filter(lambda x: x.endswith('.zip'), os.listdir('files')))
    for file in files:
        if file not in current_files.keys():
            current_files[file] = datetime.now()

def delete_old_files():
    global current_files
    current_time = datetime.now()
    to_del = []
    for file, date in current_files.items():
        aux = date - current_time
        if aux.seconds >= MAX_TIME:
            print(f'[! CHECKER - {get_datetime(True)}] {file} has been stored for more than 10 minutes, deleting...')
            delete_file(file)
            to_del.append(file)
    current_files = {x:y for x,y in current_files.items() if x not in to_del}

if __name__ == "__main__":
    while True:
        look_files_folder()
        delete_old_files()
        time.sleep(60)
        
