import streamlit as st
from resizer import resize_image, resize_imgs_temp ,delete_file, get_datetime, generate_random_string
import os

MAX_FREE_FILES      = 100
FILE_UPLOADER_KEY   = 'file_uploader_key'
MULTIPLIER_SEL      = 'mult_selected'
NUMERIC_STATE       = 'numeric_state'
SLIDER_STATE        = 'slider_state'

def delete_file_st(zipfile_name):
    print(f'[! STREAMLIT - {get_datetime(True)}] Downloading {zipfile_name} --- Contains {len(file_uploader)} files!')
    delete_file(zipfile_name)

def update_slider():
    st.session_state[SLIDER_STATE] = st.session_state[NUMERIC_STATE]
def update_numeric():
    st.session_state[NUMERIC_STATE] = st.session_state[SLIDER_STATE]

@st.experimental_dialog('Maximum number of files reached', width="large")
def max_files_dialog(uploaded_files):
    st.markdown(f'You have surpassed our maximum of {MAX_FREE_FILES} files uploaded at once.')
    st.markdown(f'We will keep and process your first {MAX_FREE_FILES} images (from {uploaded_files[0].name} to {uploaded_files[-1].name}) but you **will need to reupload the rest**.')
   
if FILE_UPLOADER_KEY not in st.session_state:
    st.session_state[FILE_UPLOADER_KEY] = 0
if MULTIPLIER_SEL not in st.session_state:
    st.session_state[MULTIPLIER_SEL] = False
if NUMERIC_STATE not in st.session_state:
    st.session_state[NUMERIC_STATE] = 1.0
if SLIDER_STATE not in st.session_state:
    st.session_state[SLIDER_STATE] = 1.0

st.title('SIMPLE BULK IMAGE RESIZER')
st.markdown('''Welcome to ***Simple Bulk Image Resizer***, a super easy to use app to resize all your images for **FREE**.
            In order to use this app you can check the instructions in the dropdown below. .
            ''')
aux = [
    f'1. ⬆️**Upload your images using the drag & drop menu below**⬆️. Our service supports uploading **up to {MAX_FREE_FILES} images at once (50MB per file max)**.',
    '''2. ✅**Select how you want to resize your images**✅:
    - **Size multiplier**: Adjust the size of your image(s) by a specified factor. This option will not alter the aspect ratio. For example, choosing a multiplier of 2.0 will double the size of your image(s).
    - **Horizontal and vertical sizes**: Specify the exact dimensions of your image(s) in pixels. Note that this may change the aspect ratio of your images.''',
    '''3. ⏳Once you have selected a resizing method and set the corresponding parameters (using the slider or the text boxes below), click the ***Start conversion*** button to begin the process. A progress bar will appear below this button once the process starts. Please note that the conversion may take some time depending on the number of images, their sizes, the new sizes, and the current server load.''',
    '''4. ⬇️ When the process is complete, a ***Download data!*** button will appear below the progress bar. Click it to **download a .zip file containing all the resized images.**''',
    '**Note**: You can clear your uploaded files using the ***Clear uploaded files*** button. This will delete all the uploaded files, allowing you to process a new batch of images.'
]
with st.expander(':book: Instructions :book:', expanded=False):
    for line in aux:
        st.markdown(line)

file_uploader = st.file_uploader('Choose your files', 
                                 accept_multiple_files=True,
                                 type=['jpg', 'jpeg', 'png'],
                                 key=st.session_state[FILE_UPLOADER_KEY])

st.markdown('#')   
select_box = st.selectbox('Resize by', 
                          options=['Size multiplier', 'Horizontal and vertical sizes'])
st.session_state[MULTIPLIER_SEL] = (select_box != 'Size multiplier')

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
    petition_id = f'{generate_random_string(k=20)}_{get_datetime()}'
    
    if n > MAX_FREE_FILES:
        max_files_dialog(file_uploader)
        file_uploader = file_uploader[:MAX_FREE_FILES]

    if select_box == 'Size multiplier':
        zipfile_name = resize_imgs_temp(file_uploader, progress_bar, multiplier=dimension_slider, petition_id=petition_id)
    else:
        zipfile_name = resize_imgs_temp(file_uploader, progress_bar, size_x=x_dim, size_y=y_dim, petition_id=petition_id)
        
    with open(os.path.join('files', zipfile_name), 'rb') as file:
        progress_bar.progress(1.0, 'Process completed!')
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
