import streamlit as st
from resizer import resize_image, resize_image_np, delete_file, get_datetime
import os

MAX_FREE_FILES = 1_000
FILE_UPLOADER_KEY = 'file_uploader_key'
MULTIPLIER_SEL = 'mult_selected'

def delete_file_st(zipfile_name):
    print(f'[! {get_datetime(True)}] Downloading {zipfile_name} --- Contains {len(file_uploader)} files!')
    delete_file(zipfile_name)
   
if FILE_UPLOADER_KEY not in st.session_state:
    st.session_state[FILE_UPLOADER_KEY] = 0
if MULTIPLIER_SEL not in st.session_state:
    st.session_state[MULTIPLIER_SEL] = False

file_uploader = st.file_uploader('Choose your files', 
                                 accept_multiple_files=True,
                                 key=st.session_state[FILE_UPLOADER_KEY])

st.markdown('#')   
select_box = st.selectbox('Resize by', 
                          options=['Multiplier', 'Horizontal and vertical sizes'])
st.session_state[MULTIPLIER_SEL] = (select_box != 'Multiplier')

st.markdown('#')
dimension_slider = st.slider('Size multiplier (keeps aspect ratio)',
                            min_value=0.1,
                            max_value=10.0,
                            key='dimension_slider',
                            step=0.1,
                            disabled=st.session_state[MULTIPLIER_SEL])

st.markdown('#')
c1, c2 = st.columns(2)
with c1:
    x_dim = st.number_input('Horizontal pixels', 
                            key='x_dim',
                            min_value=1,
                            step=1,
                            disabled=(not st.session_state[MULTIPLIER_SEL]))
with c2:
    y_dim = st.number_input('Vertical pixels',
                            key='y_dim',
                            min_value=1,
                            step=1,
                            disabled=(not st.session_state[MULTIPLIER_SEL]))

st.markdown('#')   
c1, c2 = st.columns(2)
with c1:
    delete_button = st.button('Clear uploaded files',
                              key='delete_button')
with c2:
    start_conversion = st.button('Start conversion', 
                                 key='start_conversion')

if start_conversion and (file_uploader is not None):
    st.markdown('#')
    progress_bar = st.progress(0, 'Operation in process. Please wait.')
    n = len(file_uploader)
    if n < MAX_FREE_FILES:
        if select_box == 'Multiplier':
            zipfile_name = resize_image(file_uploader, progress_bar, multiplier=dimension_slider)
        else:
            zipfile_name = resize_image(file_uploader, progress_bar, size_x=x_dim, size_y=y_dim)
        
        progress_bar.progress(1.0, 'Process completed!')
        with open(os.path.join('files', zipfile_name), 'rb') as file:
            download_button = st.download_button('Download data!', 
                                                 key='download_button',
                                                 data=file,
                                                 file_name=zipfile_name,
                                                 on_click=delete_file_st,
                                                 args=(zipfile_name, ),
                                                 mime='application/zip')
            

if delete_button:
    st.session_state[FILE_UPLOADER_KEY] += 1
    st.rerun()
