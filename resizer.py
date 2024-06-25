from datetime import datetime
import streamlit as st
import numpy as np
import zipfile
import string
import random
import cv2
import os

def get_datetime(display=False):
    if display:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return datetime.now().strftime("%d%m%Y%H%M%S")

def generate_random_string(k=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))

def delete_file(file_name):
    os.remove(os.path.join('files', file_name))

def create_zip_file(converted_imgs, file_names):
    zipfile_name = f'{generate_random_string()}_{get_datetime()}.zip'
    with zipfile.ZipFile(os.path.join('files', zipfile_name), 'w') as file:
        for converted_img, file_name in zip(converted_imgs, file_names):
            file_ext = file_name[file_name.rindex('.'):]
            _, buf = cv2.imencode(file_ext, converted_img)
            file.writestr(file_name, buf)
    return zipfile_name

def merge_zip_files(zip_files_names):
    print(f'[! {get_datetime(True)}] Merging {zip_files_names}')
    with zipfile.ZipFile(os.path.join('files', zip_files_names[0]), 'a') as file:
        for zip_name in zip_files_names[1:]:
            with zipfile.ZipFile(os.path.join('files', zip_name), 'r') as zip_file:
                # print(f'[{get_datetime(True)}] Processing {zip_name}')
                for name in zip_file.namelist():
                    # print(f'[{get_datetime(True)}] Processing {name}')
                    file.writestr(name, zip_file.open(name).read())
    
    for zip_file_name in zip_files_names[1:]:
        print(f'[! {get_datetime()}] Deleting files...')
        delete_file(zip_file_name)
    
    return zip_files_names[0]

def resize_image(images_data, progress_bar, multiplier=None, size_x=None, size_y=None):
    converted_imgs, file_names = [], []
    zip_files = []
    progress_per_img = 1.0 / len(images_data)
    for i, image_data in enumerate(images_data):
        progress_bar.progress((i + 1) * progress_per_img, 'Operation in process. Please wait.')
        jpg_as_np = np.fromstring(image_data.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
        file_names.append(image_data.name)
        # print(f'[! {get_datetime(True)}] Resizing {file_names[-1]}!')

        if multiplier != None:
            new_img = cv2.resize(img, 
                                dsize=None,
                                fx=multiplier, 
                                fy=multiplier,
                                interpolation=cv2.INTER_LANCZOS4)
        else:
            new_img = cv2.resize(img,
                                dsize=(size_x, size_y),
                                interpolation=cv2.INTER_LANCZOS4)
        
        converted_imgs.append(new_img)
        if (i+1) % 50 == 0:
            print(f'[! {get_datetime(True)}] {i+1} images read, creating zip file...')
            zip_files.append(create_zip_file(converted_imgs, file_names))
            converted_imgs, file_names = [], []
    
    progress_bar.progress(1.0, 'Process completed!')
    if converted_imgs != []:
        zip_files.append(create_zip_file(converted_imgs, file_names))

    return merge_zip_files(zip_files)