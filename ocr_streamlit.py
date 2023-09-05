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
#import psycopg2
import gspread
from google.oauth2 import service_account
from gsheetsdb import connect
#from psycopg2 import extras
from receipt_utils import convert_to_float_if_decimal
from receipt_utils import build_table 
import time
from st_aggrid import AgGrid
from pdf_utils import read_pdf_instacart
import time
import boto3


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



def dataframe_to_list_of_lists(df):
    list_of_lists = []
    
    for index, row in df.iterrows():
        list_of_lists.append(row.tolist())
    
    return list_of_lists
def uploadMP4ToS3(file, bucket,filename):
    s3 = boto3.client('s3',
                      region_name=st.secrets["s3"]["AWS_DEFAULT_REGION"],
                      aws_access_key_id=st.secrets["s3"]["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key=st.secrets["s3"]["AWS_SECRET_ACCESS_KEY"])
    
    try:
        #s3.upload_file(file, bucket, s3_file)
        s3.upload_fileobj(file, bucket,filename)
        st.success('File Successfully Uploaded to s3')
        return True
    except FileNotFoundError:
        time.sleep(9)
        st.error('File not found.')
        return False 

@st.cache_resource
def get_ocr(img_path):

    # Paddleocr supports Chinese, English, French, German, Korean and Japanese.
    # You can set the parameter `lang` as `ch`, `en`, `fr`, `german`, `korean`, `japan`
    # to switch the language model in order.
    
    ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
#    img_path = path
    with st.spinner('Wait as we are reading the image'):
        res = ocr.ocr(img_path, cls=True)
    
    return res
    
    
   

if check_password():
   

    #https://blog.jcharistech.com/2021/01/21/how-to-save-uploaded-files-to-directory-in-streamlit-apps/
    image_file = st.file_uploader("Upload An Image",type=['png','jpeg','jpg','pdf'])
    #image_file = st.file_uploader("Choose a file", "pdf")
    if image_file is not None:
        file_details = {"FileName":image_file.name,"FileType":image_file.type}
        st.write(file_details)
        #img = load_image(image_file)
        print (file_details)
        #img = load_image(image_file)
        st.success(image_file.name + ' Selected')
  
        
        if 'pdf' not in image_file.name:
            st.image(image_file)
            with open(os.path.join("./",image_file.name),"wb") as f: 
                f.write(image_file.getbuffer())         
            st.success("Saved File")

            result =get_ocr(image_file.name)
            img_path = image_file.name
        else:

            print (file_details)
     
            rows =[]
            names , costs, dates, vendor, img_path = read_pdf_instacart(image_file.name)
            df = pd.DataFrame({'item':names ,'cost':costs, 'dates':dates, 'vendor':vendor, 'path': img_path})
            st.dataframe(df)



        
        important_results = [convert_to_float_if_decimal(line[1][0]) for line in result[0]]
        #rows =[]
        names, costs, dates, vendor = build_table(important_results)
        if 'N/A' in vendor:
            title = st.text_input('Could not figure out the name of the vendor, write it here', 'N/A')
            vendor = [title for _ in names]
        
        if st.button('Vendor updated?'):
            df = pd.DataFrame({'item':names ,'label':['' for _ in names],'cost':costs, 'dates':dates, 'vendor':vendor, 'path': img_path})
            #st.dataframe(df)
            grid_return = AgGrid(df,editable=True)

    # if st.button('If the info is correct, click here to add it to the database'):
            
            new_df = grid_return['data']
            # Create a connection object.
            rows = dataframe_to_list_of_lists(new_df)
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets"
                ],
            )
            conn = connect(credentials=credentials)
            client=gspread.authorize(credentials)
            sheet_url = st.secrets["gsheets"]["private_gsheets_url"] #this information should be included in streamlit secret
            sheet = client.open_by_url(sheet_url).sheet1
            sheet.append_rows(rows)
            #conn = init_connection()
            #insert_dataframe_to_table(new_df,"transactions",conn)

            #print (important_results)
            #rows = run_query("SELECT * from transactions;",conn)
            #conn.close()
            st.write('Successfully to db')

        else:
            st.write('Goodbye')

            
        if st.button('Upload to s3?'):
                with st.spinner('Uploading...'):
                    uploadMP4ToS3(image_file,st.secrets["s3"]["bucket_name"],image_file.name)