from datetime import datetime
import numpy as np
import zipfile
import string
import random
import cv2
import os

def get_datetime():
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

def resize_image(images_data, multiplier=None, size_x=None, size_y=None):
    converted_imgs, file_names = [], []
    for image_data in images_data:
        jpg_as_np = np.fromstring(image_data.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
        file_names.append(image_data.name)

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
    return create_zip_file(converted_imgs, file_names)