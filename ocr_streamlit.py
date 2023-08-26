import streamlit as st
import numpy as np
from PIL import ImageOps
import pandas as pd
import os
import streamlit as st
import pandas as pd
from io import StringIO
from PIL import ImageFont
from paddleocr import PaddleOCR
import re
import psycopg2
from psycopg2 import extras
from receipt_utils import convert_to_float_if_decimal
from receipt_utils import build_table 
import time
from st_aggrid import AgGrid
from pdf_utils import read_pdf_instacart


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query,_conn):
    with _conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

@st.cache_data(ttl=600)
def insert_dataframe_to_table(dataframe, table_name, _connection):
    # Convert DataFrame to a list of tuples
    values = dataframe.values.tolist()

    # Create a SQL INSERT statement
    insert_query = f"INSERT INTO {table_name} VALUES %s"

    # Execute the insert statement
    with _connection.cursor() as cursor:
        extras.execute_values(cursor, insert_query, values, page_size=len(values))

    # Commit the changes
    _connection.commit()


def get_ocr(img_path):

    # Paddleocr supports Chinese, English, French, German, Korean and Japanese.
    # You can set the parameter `lang` as `ch`, `en`, `fr`, `german`, `korean`, `japan`
    # to switch the language model in order.
    ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
#    img_path = path
    with st.spinner('Wait as we are reading the image'):
        result = ocr.ocr(img_path, cls=True)
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            print(line[1][0])

    important_results = [convert_to_float_if_decimal(line[1][0]) for line in result[0]]
    names, costs, dates, vendor = build_table(important_results)
    df = pd.DataFrame({'item':names ,'cost':costs, 'dates':dates, 'vendor':vendor, 'path': img_path})
    #st.dataframe(df)
    grid_return = AgGrid(df,editable=True)

    if st.button('Say hello'):
        
        new_df = grid_return['data']
        conn = init_connection()
        insert_dataframe_to_table(new_df,"transactions",conn)
    
        print (important_results)
        rows = run_query("SELECT * from transactions;",conn)
        conn.close()
        st.write('Successfully to db')
    else:
        st.write('Goodbye')

   
    
    ''' 
# Print results.
    for row in rows:
        st.write(f"{row[0]} has a :{row[1]}:")
    '''
    font = "/usr/share/fonts/truetype/Gargi/Gargi.ttf"

    '''
    # draw result
    from PIL import Image
    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path=font)
    im_show = Image.fromarray(im_show)
    im_show.save('result.jpg')
    #st.image(im_show)
    '''
if check_password():
   

    #https://blog.jcharistech.com/2021/01/21/how-to-save-uploaded-files-to-directory-in-streamlit-apps/
    image_file = st.file_uploader("Upload An Image",type=['png','jpeg','jpg','pdf'])
    #image_file = st.file_uploader("Choose a file", "pdf")
    if image_file is not None:
        file_details = {"FileName":image_file.name,"FileType":image_file.type}
        st.write(file_details)
        #img = load_image(image_file)
        print (file_details)
        if 'pdf' not in image_file.name:
            st.image(image_file)
            with open(os.path.join("./",image_file.name),"wb") as f: 
                f.write(image_file.getbuffer())         
            st.success("Saved File")

            get_ocr(image_file.name)
        else:
            #file_details = {"FileName":image_file.name,"FileType":image_file.type}
            #st.write(file_details)
            #img = load_image(image_file)
            print (file_details)
            with open(os.path.join("./",image_file.name),"wb") as f: 
                f.write(image_file.getbuffer())         
            st.success("Saved File")
            names , costs, dates, vendor, img_path = read_pdf_instacart(image_file.name)
            df = pd.DataFrame({'item':names ,'cost':costs, 'dates':dates, 'vendor':vendor, 'path': img_path})
            st.dataframe(df)


