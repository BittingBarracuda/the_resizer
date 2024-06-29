from resizer import delete_file, get_datetime, IMGS_DIR
from datetime import datetime
import shutil
import time
import os

MAX_TIME = 10 * 60
current_files = {}
current_directories = {}

def look_files_folder():
    global current_files, current_directories
    print(f'[! CHECKER - {get_datetime(True)}] files_checker looking for old files...')
    files = list(filter(lambda x: x.endswith('.zip'), os.listdir('files')))
    for file in files:
        if file not in current_files.keys():
            current_files[file] = datetime.now()

    directories = [x[0] for x in os.walk(IMGS_DIR)][1:]
    for directory in directories:
        if directory not in current_directories.keys():
            current_directories[directory] = datetime.now()

def get_to_delete(current_dict, current_time, is_dirs=False):
    to_del = []
    for file, date in current_dict.items():
        aux = date - current_time
        if aux.seconds >= MAX_TIME:
            print(f'[! CHECKER - {get_datetime(True)}] {file} has been stored for more than 10 minutes, deleting...')
            if is_dirs:
                shutil.rmtree(file)
            else:
                delete_file(file)
            to_del.append(file)
    return to_del

def delete_old_files():
    global current_files, current_directories
    current_time = datetime.now()
    
    to_del = get_to_delete(current_files, current_time, is_dirs=False)
    current_files = {x:y for x,y in current_files.items() if x not in to_del}

    to_del = get_to_delete(current_directories, current_time, is_dirs=True)
    current_directories = {x:y for x,y in current_directories.items() if x not in to_del}

if __name__ == "__main__":
    while True:
        look_files_folder()
        delete_old_files()
        time.sleep(60)
        
