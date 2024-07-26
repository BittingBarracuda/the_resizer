from threading import Thread, Lock
from queue import Queue
from datetime import datetime
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

import streamlit as st
import numpy as np
import zipfile
import string
import shutil
import random
import cv2
import os

TEXT_1 = 'Operation in process. Please wait.'
IMGS_DIR = os.path.join('files', 'imgs')

try:
    os.mkdir('files')
    os.mkdir(os.path.join('files', 'imgs'))
except FileExistsError:
    pass

def get_datetime(display=False):
    if display:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return datetime.now().strftime("%d%m%Y%H%M%S")

def generate_random_string(k=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))

def delete_file(file_name):
    os.remove(os.path.join('files', file_name))

def save_np_images(converted_imgs, file_names):
    aux_file_names = []
    for converted_img, file_name in zip(converted_imgs, file_names):
        aux_file_name = f'{generate_random_string()}_{get_datetime()}.npy'
        np.save(os.path.join('files', aux_file_name), converted_img)
        aux_file_names.append(aux_file_name)
    return [(x, y) for x, y in zip(file_names, aux_file_names)]

def merge_np_images(np_files, progress_bar):
    zipfile_name = f'{generate_random_string()}_{get_datetime()}.zip'
    prog_per_file = 0.1 / len(np_files)
    with zipfile.ZipFile(os.path.join('files', zipfile_name), 'w') as file:
        i = 1
        for file_name, np_file in np_files:
            arr = np.load(os.path.join('files', np_file))
            file_ext = file_name[file_name.rindex('.'):]
            _, buf = cv2.imencode(file_ext, arr)
            file.writestr(file_name, buf)

            progress_bar.progress(0.9 + (i * prog_per_file), TEXT_1)
            i += 1
    for _, np_file in np_files:
        delete_file(np_file)
    return zipfile_name

def create_zip_file(converted_imgs, file_names, zipfile_name):
    mode = ''
    if os.path.exists(os.path.join('files', zipfile_name)):
        mode = 'a'
    else:
        mode = 'w'
    
    with zipfile.ZipFile(os.path.join('files', zipfile_name), mode) as file:
        for converted_img, file_name in zip(converted_imgs, file_names):
            file_ext = file_name[file_name.rindex('.'):]
            _, buf = cv2.imencode(file_ext, converted_img)
            file.writestr(file_name, buf)

def merge_zip_files(zip_files_names, progress_bar, petition_id):
    print(f'[! RESIZER - {get_datetime(True)}] Merging {zip_files_names} for {petition_id} petition')
    prog_per_file = 0.1 / len(zip_files_names)

    with zipfile.ZipFile(os.path.join('files', zip_files_names[0]), 'a') as file:
        i = 2
        for zip_name in zip_files_names[1:]:
            with zipfile.ZipFile(os.path.join('files', zip_name), 'r') as zip_file:
                for name in zip_file.namelist():
                    file.writestr(name, zip_file.open(name).read())
            progress_bar.progress(0.9 + (i * prog_per_file), TEXT_1)
            i += 1
    
    for zip_file_name in zip_files_names[1:]:
        delete_file(zip_file_name)
    
    return zip_files_names[0]

def resize_image(images_data, progress_bar, multiplier=None, size_x=None, size_y=None, petition_id=''):
    converted_imgs, file_names = [], []
    progress_per_img = 1.0 / len(images_data)
    zipfile_name = f'{generate_random_string()}_{get_datetime()}.zip'
    
    for i, image_data in enumerate(images_data):
        progress_bar.progress((i + 1) * progress_per_img, TEXT_1)
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
            print(f'[! RESIZER - {get_datetime(True)}] {i+1} images read for petition {petition_id}, creating zip file...')
            create_zip_file(converted_imgs, file_names, zipfile_name)
            converted_imgs, file_names = [], []
    
    if converted_imgs != []:
        create_zip_file(converted_imgs, file_names, zipfile_name)

    return zipfile_name

def resize_image_np(images_data, progress_bar, multiplier=None, size_x=None, size_y=None):
    converted_imgs, file_names = [], []
    all_files_names = []
    progress_per_img = 0.9 / len(images_data)

    for i, image_data in enumerate(images_data):
        progress_bar.progress((i + 1) * progress_per_img, TEXT_1)
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
            print(f'[! RESIZER - {get_datetime(True)}] {i+1} images read, creating numpy file...')
            all_files_names.extend(save_np_images(converted_imgs, file_names))
            converted_imgs, file_names = [], []
    
    if converted_imgs != []:
        all_files_names.extend(save_np_images(converted_imgs, file_names))

    return merge_np_images(all_files_names, progress_bar)

def resize_imgs_temp(images_data, progress_bar, multiplier=None, size_x=None, size_y=None, petition_id='', keep_ratio=False):
    # if keep_ratio:
    #     resize_all_images_cv2(images_data, progress_bar, size_y, size_x, petition_id)

    progress_per_img = 1.0 / len(images_data)
    zipfile_name = f'{generate_random_string()}_{get_datetime()}.zip'
    aux_path = os.path.join(IMGS_DIR, petition_id)
    
    try:
        os.mkdir(aux_path)
    except FileExistsError:
        pass

    
    with zipfile.ZipFile(os.path.join('files', zipfile_name), 'w') as file:
        for i, image_data in enumerate(images_data):
            progress_bar.progress((i + 1) * progress_per_img, TEXT_1)
            jpg_as_np = np.fromstring(image_data.getvalue(), dtype=np.uint8)
            img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
            
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
            
            temp_filename = os.path.join(aux_path, image_data.name)
            
            cv2.imwrite(temp_filename, new_img)
            file.write(temp_filename, arcname=os.path.basename(temp_filename))
            os.remove(temp_filename)

            if (i+1) % 20 == 0:
                print(f'[! RESIZER - {get_datetime(True)}] {i+1} images resized for petition {petition_id}')
                st.write(f'{i+1} images resized...')
    
    shutil.rmtree(aux_path)
    print(f'[! RESIZER - {get_datetime(True)}] Total of {len(images_data)} images resized for petiton {petition_id}')
    return zipfile_name

# def resize_all_images_cv2(images_data, progress_bar, height, width, petition_id=''):
#     progress_per_img = 1.0 / len(images_data)
#     zipfile_name = f'{generate_random_string()}_{get_datetime()}.zip'
#     aux_path = os.path.join(IMGS_DIR, petition_id)
    
#     try:
#         os.mkdir(aux_path)
#     except FileExistsError:
#         pass

#     with zipfile.ZipFile(os.path.join('files', zipfile_name), 'w') as file:
#         for i, image_data in enumerate(images_data):
#             progress_bar.progress((i + 1) * progress_per_img, TEXT_1)
#             jpg_as_np = np.fromstring(image_data.getvalue(), dtype=np.uint8)
#             img_cv = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
            
#             try:
#                 background = np.zeros((width, height, 3))
#                 x, y = img_cv.shape[0], img_cv.shape[1]

#                 if x > y:
#                     new_width = width
#                     new_height = min(height, int((y * width) / x))
#                 else:
#                     new_height = height
#                     new_width = min(width, int((x * height) / y))

#                 new_img = cv2.resize(img_cv, (new_height, new_width))
#                 center = (width // 2, height // 2)
#                 delta_x = new_width // 2
#                 delta_y = new_height // 2

#                 aux_x = range(center[0]-delta_x,center[0]+delta_x)
#                 aux_y = range(center[1]-delta_y,center[1]+delta_y)
#                 background[center[0]-delta_x:center[0]+delta_x, center[1]-delta_y:center[1]+delta_y] = new_img[:min(len(list(aux_x)), new_img.shape[0]), :min(len(list(aux_y)), new_img.shape[1])]

#                 temp_filename = os.path.join(aux_path, image_data.name)
                
#                 cv2.imwrite(temp_filename, background)
#                 file.write(temp_filename, arcname=os.path.basename(temp_filename))
#                 os.remove(temp_filename)

#                 if (i+1) % 20 == 0:
#                     print(f'[! RESIZER - {get_datetime(True)}] {i+1} images resized for petition {petition_id}')
#                     st.write(f'{i+1} images resized...')
            
#             except (cv2.error, AttributeError) as e:
#                 print(e)
#                 print(f'[!] Error resizing {image_data}, skipping...')

def resize_one_image(q, l, aux_path, zipfile_name, progress_bar, progress_per_img, multiplier=None, size_x=None, size_y=None):
    image_data = q.get()
    with zipfile.ZipFile(os.path.join('files', zipfile_name), 'w') as file:
        jpg_as_np = np.fromstring(image_data.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
            
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
            
        temp_filename = os.path.join(aux_path, image_data.name)
            
        cv2.imwrite(temp_filename, new_img)
        with l:
            file.write(temp_filename, arcname=os.path.basename(temp_filename))
        os.remove(temp_filename)
    
    with l:
        progress_bar.progress(1.0 - (q.qsize() * progress_per_img), TEXT_1)
    q.task_done()

def resize_images_threads(images_data, progress_bar, multiplier=None, size_x=None, size_y=None, petition_id='', keep_ratio=False):
    progress_per_img = 1.0 / len(images_data)
    zipfile_name = f'{generate_random_string()}_{get_datetime()}.zip'
    aux_path = os.path.join(IMGS_DIR, petition_id)
    ctx = get_script_run_ctx()
    
    try:
        os.mkdir(aux_path)
    except FileExistsError:
        pass
    
    q = Queue()
    l = Lock()
    for image_data in images_data:
        q.put(image_data)
    
    if keep_ratio:
        threads = [Thread()]
    else:
        threads = [Thread(target=resize_one_image, args=(q, l, aux_path, zipfile_name, progress_bar, progress_per_img, multiplier, size_x, size_y)) for _ in range(4)]
    
    for thread in threads:
        add_script_run_ctx(thread, ctx)
        thread.start()
    
    q.join()

    shutil.rmtree(aux_path)
    print(f'[! RESIZER - {get_datetime(True)}] Total of {len(images_data)} images resized for petiton {petition_id}')
    return zipfile_name
    