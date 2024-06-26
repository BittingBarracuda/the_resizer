import streamlit as st
from resizer import resize_image, delete_file, get_datetime, generate_random_string
import os

MAX_FREE_FILES      = 1_000
FILE_UPLOADER_KEY   = 'file_uploader_key'
MULTIPLIER_SEL      = 'mult_selected'
NUMERIC_STATE       = 'numeric_state'
SLIDER_STATE        = 'slider_state'

def delete_file_st(zipfile_name):
    print(f'[! {get_datetime(True)}] Downloading {zipfile_name} --- Contains {len(file_uploader)} files!')
    delete_file(zipfile_name)

def update_slider():
    st.session_state[SLIDER_STATE] = st.session_state[NUMERIC_STATE]
def update_numeric():
    st.session_state[NUMERIC_STATE] = st.session_state[SLIDER_STATE]
   
if FILE_UPLOADER_KEY not in st.session_state:
    st.session_state[FILE_UPLOADER_KEY] = 0
if MULTIPLIER_SEL not in st.session_state:
    st.session_state[MULTIPLIER_SEL] = False
if NUMERIC_STATE not in st.session_state:
    st.session_state[NUMERIC_STATE] = 1.0
if SLIDER_STATE not in st.session_state:
    st.session_state[SLIDER_STATE] = 1.0

st.title('SIMPLE IMAGE RESIZER')
st.markdown('#')

file_uploader = st.file_uploader('Choose your files', 
                                 accept_multiple_files=True,
                                 type=['jpg', 'jpeg', 'png'],
                                 key=st.session_state[FILE_UPLOADER_KEY])

st.markdown('#')   
select_box = st.selectbox('Resize by', 
                          options=['Multiplier', 'Horizontal and vertical sizes'])
st.session_state[MULTIPLIER_SEL] = (select_box != 'Multiplier')

st.markdown('#')
c1, c2 = st.columns((3, 1))
with c1:
    dimension_slider = st.slider('Size multiplier (keeps aspect ratio)',
                                min_value=0.1,
                                max_value=5.0,
                                step=0.1,
                                key=SLIDER_STATE,
                                on_change=update_numeric,
                                disabled=st.session_state[MULTIPLIER_SEL])
with c2:
    numeric_input = st.number_input('Multiplier value',
                                    min_value=0.1,
                                    max_value=5.0,
                                    key=NUMERIC_STATE,
                                    on_change=update_slider,
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
    petition_id = f'{generate_random_string(k=4)}_{get_datetime()}'
    
    if n <= MAX_FREE_FILES:
        if select_box == 'Multiplier':
            zipfile_name = resize_image(file_uploader, progress_bar, multiplier=dimension_slider, petition_id=petition_id)
        else:
            zipfile_name = resize_image(file_uploader, progress_bar, size_x=x_dim, size_y=y_dim, petition_id=petition_id)
        
        progress_bar.progress(1.0, 'Process completed!')
        with open(os.path.join('files', zipfile_name), 'rb') as file:
            download_button = st.download_button('Download data!', 
                                                 key='download_button',
                                                 data=file,
                                                 file_name=zipfile_name,
                                                 on_click=delete_file_st,
                                                 args=(zipfile_name, ),
                                                 mime='application/zip')
    else:
        st.warning(f'Only {MAX_FREE_FILES} can be uploaded at once.')
            

if delete_button:
    st.session_state[FILE_UPLOADER_KEY] += 1
    st.rerun()
